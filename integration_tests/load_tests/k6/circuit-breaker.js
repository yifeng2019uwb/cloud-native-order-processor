/**
 * Circuit Breaker Load Tests
 * TC-CB-001: Circuit breaker trip on failures
 * TC-CB-002: Circuit breaker recovery
 * 
 * Tests circuit breaker behavior when backend services fail
 * Circuit breaker: 5 failures threshold, 60s timeout, 3 successes to recover
 * 
 * AUTOMATED EXECUTION:
 * Use run_load_tests.sh which automatically:
 * 1. Stops inventory_service
 * 2. Runs trip test (TC-CB-001)
 * 3. Waits 60s for timeout
 * 4. Starts inventory_service
 * 5. Runs recovery test (TC-CB-002)
 * 
 * MANUAL EXECUTION:
 * Set CIRCUIT_BREAKER_PHASE environment variable:
 * - CIRCUIT_BREAKER_PHASE=trip k6 run k6/circuit-breaker.js
 * - CIRCUIT_BREAKER_PHASE=recover k6 run k6/circuit-breaker.js
 */

import { check, sleep } from 'k6';
import http from 'k6/http';
import { BASE_URL, API_BASE, ENDPOINTS } from './config.js';
import { loadTestUserToken, buildAuthHeaders } from './utils.js';

// Load test user token
const testUserToken = loadTestUserToken();

// Test configuration
const FAILURE_THRESHOLD = 5; // Circuit breaker opens after 5 failures
const TIMEOUT_SECONDS = 60; // Circuit breaker timeout
const SUCCESS_THRESHOLD = 3; // Successes needed to recover

// Test phase: 'trip' or 'recover'
// Set via environment variable: CIRCUIT_BREAKER_PHASE=trip or CIRCUIT_BREAKER_PHASE=recover
const TEST_PHASE = __ENV.CIRCUIT_BREAKER_PHASE || 'trip';

export const options = {
  // Use single VU to send requests sequentially
  vus: 1,
  iterations: TEST_PHASE === 'trip' ? FAILURE_THRESHOLD + 1 : SUCCESS_THRESHOLD,
  // Note: maxDuration removed - k6 will calculate automatically from iterations
  thresholds: {
    http_req_duration: ['p(95)<5000'],
  },
};

export default function () {
  const iteration = __ITER;
  
  // Use inventory service endpoint
  // IMPORTANT: For 'trip' phase, service must be stopped or failing
  // For 'recover' phase, service must be running
  const url = `${API_BASE}${ENDPOINTS.INVENTORY_ASSETS}`;
  const headers = buildAuthHeaders(testUserToken);

  if (TEST_PHASE === 'trip') {
    // TC-CB-001: Trigger circuit breaker trip
    const response = http.get(url, { headers });
    
    const circuitCheck = check(response, {
      'request completed': (r) => r.status !== undefined,
      'failure detected (network error or 5xx)': (r) => {
        // Network error (status 0) or 5xx indicates failure
        // Circuit breaker records failures on network errors or 5xx status codes
        return r.status === 0 || (r.status >= 500 && r.status < 600);
      },
      'circuit breaker opens after threshold': (r) => {
        // After 5 failures, 6th request should get 503 (circuit open)
        if (iteration >= FAILURE_THRESHOLD) {
          return r.status === 503;
        }
        // Before threshold: failures are expected (network error or 5xx)
        return true;
      },
    });

    if (iteration < FAILURE_THRESHOLD) {
      // Sending failure requests
      console.log(`📤 TC-CB-001: Failure request ${iteration + 1}/${FAILURE_THRESHOLD}: status=${response.status}`);
    } else if (iteration === FAILURE_THRESHOLD) {
      // Verify circuit is open
      console.log(`✅ TC-CB-001: Circuit breaker should be OPEN`);
      console.log(`   Verification request status: ${response.status}`);
      
      if (response.status === 503) {
        console.log(`   ✅ Circuit breaker confirmed OPEN - returning 503`);
        console.log(`   ⏳ Wait ${TIMEOUT_SECONDS}s, then start service and run recovery test`);
      } else {
        console.log(`   ⚠️  Expected 503, got ${response.status}. Circuit may not be open yet.`);
      }
    }

    // Small delay between requests
    sleep(1);

  } else {
    // TC-CB-002: Circuit breaker recovery
    // Circuit should be HALF-OPEN after timeout
    // Send successful requests to recover
    const response = http.get(url, { headers });
    
    const recoveryCheck = check(response, {
      'recovery request sent': (r) => r.status !== undefined,
      'circuit recovering (not 503)': (r) => {
        // After timeout, circuit is half-open
        // Successful requests (200 or 4xx, not 503) should recover it
        return r.status !== 503;
      },
    });

    console.log(`🔄 TC-CB-002: Recovery attempt ${iteration + 1}/${SUCCESS_THRESHOLD}: status=${response.status}`);

    if (iteration === SUCCESS_THRESHOLD - 1) {
      if (response.status !== 503) {
        console.log(`✅ Circuit breaker should be CLOSED after ${SUCCESS_THRESHOLD} successes`);
      } else {
        console.log(`⚠️  Circuit still returning 503. May need more time or more successes.`);
      }
    }

    // Small delay between recovery requests
    sleep(1);
  }
}
