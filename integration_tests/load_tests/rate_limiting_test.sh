#!/bin/bash

# Rate Limiting Load Test
# Tests the gateway's rate limiting functionality with metrics collection

echo "🚀 Rate Limiting Load Test"
echo "=========================="

# Configuration
GATEWAY_URL="${GATEWAY_HOST:-localhost}:${GATEWAY_PORT:-8080}"
GATEWAY_BASE_URL="http://$GATEWAY_URL"
TEST_ENDPOINT="/api/v1/auth/login"
RATE_LIMIT=100  # From gateway configuration
TEST_REQUESTS=105  # Test exceeding the limit

echo "📊 Testing Rate Limiting on: $GATEWAY_BASE_URL$TEST_ENDPOINT"
echo "🎯 Rate Limit: $RATE_LIMIT requests/minute"
echo "🧪 Test Requests: $TEST_REQUESTS (should trigger rate limiting)"
echo ""

# Function to make a request and check rate limit headers
make_request() {
    local request_num=$1
    echo -n "Request $request_num: "

    response=$(curl -s -i -X POST "$GATEWAY_BASE_URL$TEST_ENDPOINT" \
        -H "Content-Type: application/json" \
        -d '{"username":"testuser","password":"testpass"}' \
        2>/dev/null)

    # Extract rate limit headers
    limit=$(echo "$response" | grep -i "X-RateLimit-Limit" | cut -d: -f2 | tr -d ' \r')
    remaining=$(echo "$response" | grep -i "X-RateLimit-Remaining" | cut -d: -f2 | tr -d ' \r')
    reset=$(echo "$response" | grep -i "X-RateLimit-Reset" | cut -d: -f2 | tr -d ' \r')
    status=$(echo "$response" | grep "HTTP/" | awk '{print $2}')

    echo "Status: $status, Limit: $limit, Remaining: $remaining, Reset: $reset"

    # Check if we hit rate limit
    if [ "$status" = "429" ]; then
        echo "🎯 RATE LIMIT TRIGGERED! Request $request_num was blocked"
        return 1
    fi

    return 0
}

# Test metrics endpoint
echo "📈 Testing Metrics Endpoint..."
metrics_response=$(curl -s "$GATEWAY_BASE_URL/metrics")
if [ $? -eq 0 ]; then
    echo "✅ Metrics endpoint accessible"
    echo "📊 Rate limiting metrics found:"
    echo "$metrics_response" | grep -E "(gateway_rate_limit|gateway_requests_total)" | head -5
else
    echo "❌ Metrics endpoint not accessible"
fi

echo ""
echo "🧪 Starting Rate Limit Test..."

# Make requests until we hit the rate limit
for i in $(seq 1 $TEST_REQUESTS); do
    if ! make_request $i; then
        echo ""
        echo "🎉 SUCCESS: Rate limiting is working correctly!"
        echo "📊 Final metrics:"
        curl -s "$GATEWAY_BASE_URL/metrics" | grep -E "gateway_rate_limit_violations_total|gateway_requests_total" | head -3
        break
    fi

    # Small delay to avoid overwhelming the system
    sleep 0.1
done

echo ""
echo "✅ Rate limiting load test completed!"
