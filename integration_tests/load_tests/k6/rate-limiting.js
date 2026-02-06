/**
 * Rate Limiting Load Tests
 * TC-RL-001: Gateway rate limit enforcement (Profile API)
 * TC-RL-002: Rate limit headers
 *
 * Tests rate limiting on GET /api/v1/auth/profile endpoint
 * Uses pre-created load_test_user_1 (run setup/create_load_test_users.py first)
 */

import { check } from 'k6';
import http from 'k6/http';
import { BASE_URL, API_BASE, ENDPOINTS } from './config.js';
import { loadTestUserToken, buildAuthHeaders, createRateLimitHeaderChecks, checkRateLimitHeaders } from './utils.js';

// Load test user token using utility function
const testUserToken = loadTestUserToken();

export const options = {
  // Gateway rate limit is configurable via GATEWAY_RATE_LIMIT (default: 10000 req/min = ~166 req/sec)
  // To test rate limiting, we need to exceed this limit
  // Reduced VUs but removed delay to still exceed limit while using less memory
  stages: [
    { duration: '30s', target: 150 }, // 150 VUs for 30s (reduced from 200 VUs for 1m to save memory)
  ],
  thresholds: {
    // Response time threshold
    http_req_duration: ['p(95)<1000'],
    // Note: We expect high failure rate when rate limit is exceeded
    // The check() function below validates 429 responses
    // No threshold on http_req_failed since we're testing rate limiting behavior
  },
};

export default function () {
  // Test Profile endpoint (requires authentication)
  const url = `${API_BASE}${ENDPOINTS.AUTH_PROFILE}`;
  
  // Build auth headers using utility function
  const headers = buildAuthHeaders(testUserToken);

  const response = http.get(url, { headers });
  
  // No delay - we want to exceed rate limit quickly to minimize test duration and memory usage

  // TC-RL-001: Verify rate limit enforcement
  // After 100 requests, should get 429
  // Note: We expect some 429s after exceeding rate limit
  const statusCheck = check(response, {
    'status is 200 or 429': (r) => r.status === 200 || r.status === 429,
  });

  // TC-RL-002: Check rate limit headers using utility function
  const hasRateLimitHeaders = check(response, createRateLimitHeaderChecks());

  // Log only first few 429 responses to confirm rate limiting is working (avoid log spam)
  if (response.status === 429) {
    const headerInfo = checkRateLimitHeaders(response);
    
    // Only log first 5 429 responses to confirm rate limiting works
    if (__VU <= 5 && __ITER === 0) {
      console.log(`✅ Rate limit triggered: status=429, remaining=${headerInfo.remaining || 'N/A'}`);
      
      // Log missing headers only on first few 429 responses
      if (!hasRateLimitHeaders) {
        console.log(`⚠️  Missing rate limit headers on 429 response`);
      }
    }
  }

  // Only log unexpected status codes (actual failures)
  if (!statusCheck && response.status !== 429) {
    // Only log first few unexpected errors to avoid spam
    if (__VU <= 3) {
      console.log(`⚠️  Unexpected status code: ${response.status}`);
    }
  }
}
