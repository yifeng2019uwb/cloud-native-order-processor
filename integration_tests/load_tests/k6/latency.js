/**
 * Latency Load Tests
 * TC-LATENCY-001: P90/P99 latency measurement
 *
 * Tests response time percentiles (P90, P95, P99) across multiple endpoints
 * to establish baseline latency metrics for all services.
 *
 * Test Flow:
 * 1. Send requests to various endpoints (health, profile, inventory, balance)
 * 2. Measure response times
 * 3. Report P90/P95/P99 percentiles
 * 4. Verify latency thresholds are met
 */

import { check, sleep } from 'k6';
import http from 'k6/http';
import { BASE_URL, API_BASE, ENDPOINTS } from './config.js';
import { loadTestUserToken, buildAuthHeaders } from './utils.js';

// Load test user token
const testUserToken = loadTestUserToken();

export const options = {
  // Optimized for memory efficiency while still meeting latency measurement requirements
  // Gateway rate limit is configurable via GATEWAY_RATE_LIMIT (default: 10000 req/min)
  // Reduced VUs and duration to minimize memory usage while still getting good metrics
  stages: [
    { duration: '15s', target: 5 },   // Ramp up to 5 VUs
    { duration: '30s', target: 5 },    // Maintain 5 VUs for 30 seconds (enough for good metrics)
    { duration: '5s', target: 0 },    // Ramp down
  ],
  thresholds: {
    // P90 latency should be under 500ms for most endpoints
    http_req_duration: ['p(90)<500', 'p(95)<1000', 'p(99)<2000'],
    // Success rate should be high (allow some failures for write operations)
    http_req_failed: ['rate<0.05'], // Less than 5% failures
  },
};

export default function () {
  const headers = buildAuthHeaders(testUserToken);
  const vuId = __VU;

  // Test multiple endpoints to get latency metrics across different services
  const endpoints = [
    // Health check (fastest, no auth)
    { method: 'GET', url: `${BASE_URL}${ENDPOINTS.HEALTH}`, headers: {}, name: 'health' },
    
    // Auth profile (requires auth, gateway + auth service)
    { method: 'GET', url: `${API_BASE}${ENDPOINTS.AUTH_PROFILE}`, headers, name: 'profile' },
    
    // Inventory assets (public, gateway + inventory service)
    { method: 'GET', url: `${API_BASE}${ENDPOINTS.INVENTORY_ASSETS}`, headers: {}, name: 'inventory' },
    
    // Balance (requires auth, gateway + user service)
    { method: 'GET', url: `${API_BASE}${ENDPOINTS.BALANCE}`, headers, name: 'balance' },
    
    // Deposit (write operation, requires auth, gateway + user service)
    // Use small amount to avoid balance issues
    { method: 'POST', url: `${API_BASE}${ENDPOINTS.BALANCE_DEPOSIT}`, headers, 
      body: JSON.stringify({ amount: 1.00 }), name: 'deposit' },
  ];

  // Rotate through endpoints based on VU ID to distribute load
  const endpoint = endpoints[vuId % endpoints.length];
  
  let response;
  if (endpoint.method === 'GET') {
    response = http.get(endpoint.url, { headers: endpoint.headers });
  } else {
    response = http.post(endpoint.url, endpoint.body, { headers: endpoint.headers });
  }

  // Small delay to maintain steady load distribution and reduce memory usage
  sleep(0.1); // 100ms delay to reduce iteration rate and memory usage

  // Verify response is successful (2xx), expected error (422 for validation), or rate limited (429)
  // Allow 422 for validation errors (e.g., insufficient balance)
  // Allow 429 for rate limiting (expected behavior under load, not a system error)
  const statusCheck = check(response, {
    [`${endpoint.name} status is successful`]: (r) => 
      r.status >= 200 && r.status < 300 || r.status === 422 || r.status === 429,
  });

  // Log unexpected failures (not 429) to diagnose issues (only log first few per endpoint to avoid spam)
  if (!statusCheck && __VU <= 3 && response.status !== 429) {
    console.log(`⚠️  ${endpoint.name} failed: status=${response.status}, url=${endpoint.url}`);
  }
}
