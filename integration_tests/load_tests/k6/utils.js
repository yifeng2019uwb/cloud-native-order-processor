/**
 * k6 Load Test Utilities
 * Shared utilities for k6 load test scripts
 */

// HTTP Header Names (constants)
export const HEADERS = {
  AUTHORIZATION: 'Authorization',
  CONTENT_TYPE: 'Content-Type',
  BEARER_PREFIX: 'Bearer ',
  JSON_CONTENT_TYPE: 'application/json',
};

// Rate Limit Header Names (constants)
export const RATE_LIMIT_HEADERS = {
  LIMIT: 'X-RateLimit-Limit',
  REMAINING: 'X-RateLimit-Remaining',
  RESET: 'X-RateLimit-Reset',
  // Lowercase variants for case-insensitive checks
  LIMIT_LC: 'x-ratelimit-limit',
  REMAINING_LC: 'x-ratelimit-remaining',
  RESET_LC: 'x-ratelimit-reset',
};

// Test User File Path
const TEST_USER_FILE = './test_user.json';

/**
 * Load test user token from JSON file
 * File is created by: python3 setup/create_load_test_users.py
 * 
 * @returns {string} Test user authentication token
 * @throws {Error} If file cannot be loaded or parsed
 */
export function loadTestUserToken() {
  try {
    const testUserData = open(TEST_USER_FILE);
    const userData = JSON.parse(testUserData);
    
    if (!userData.token) {
      throw new Error('Token not found in test_user.json');
    }
    
    return userData.token;
  } catch (e) {
    console.error(`Failed to load ${TEST_USER_FILE}. Run: python3 setup/create_load_test_users.py`);
    throw e;
  }
}

/**
 * Build authentication headers for API requests
 * 
 * @param {string} token - Authentication token
 * @param {Object} additionalHeaders - Optional additional headers to include
 * @returns {Object} Headers object for k6 http requests
 */
export function buildAuthHeaders(token, additionalHeaders = {}) {
  return {
    [HEADERS.AUTHORIZATION]: `${HEADERS.BEARER_PREFIX}${token}`,
    [HEADERS.CONTENT_TYPE]: HEADERS.JSON_CONTENT_TYPE,
    ...additionalHeaders,
  };
}

/**
 * Check if rate limit headers are present in response
 * Handles case-insensitive header names
 * 
 * @param {Object} response - k6 http response object
 * @returns {Object} Object with boolean checks for each header
 */
export function checkRateLimitHeaders(response) {
  const headers = response.headers;
  
  // Helper to get header value (case-insensitive)
  const getHeader = (name, nameLC) => {
    return headers[name] || headers[nameLC];
  };
  
  return {
    hasLimit: getHeader(RATE_LIMIT_HEADERS.LIMIT, RATE_LIMIT_HEADERS.LIMIT_LC) !== undefined,
    hasRemaining: getHeader(RATE_LIMIT_HEADERS.REMAINING, RATE_LIMIT_HEADERS.REMAINING_LC) !== undefined,
    hasReset: getHeader(RATE_LIMIT_HEADERS.RESET, RATE_LIMIT_HEADERS.RESET_LC) !== undefined,
    // Get actual values
    limit: getHeader(RATE_LIMIT_HEADERS.LIMIT, RATE_LIMIT_HEADERS.LIMIT_LC),
    remaining: getHeader(RATE_LIMIT_HEADERS.REMAINING, RATE_LIMIT_HEADERS.REMAINING_LC),
    reset: getHeader(RATE_LIMIT_HEADERS.RESET, RATE_LIMIT_HEADERS.RESET_LC),
  };
}

/**
 * Create k6 check assertions for rate limit headers
 * Returns check object ready to use with k6's check() function
 * 
 * @returns {Object} Check assertions object for rate limit headers
 */
export function createRateLimitHeaderChecks() {
  return {
    'has X-RateLimit-Limit header': (r) => {
      const headerCheck = checkRateLimitHeaders(r);
      return headerCheck.hasLimit;
    },
    'has X-RateLimit-Remaining header': (r) => {
      const headerCheck = checkRateLimitHeaders(r);
      return headerCheck.hasRemaining;
    },
    'has X-RateLimit-Reset header': (r) => {
      const headerCheck = checkRateLimitHeaders(r);
      return headerCheck.hasReset;
    },
  };
}
