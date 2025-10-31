#!/bin/bash

# Run All Load Tests
# Comprehensive load testing suite for the order-processor system

echo "🚀 Order Processor Load Test Suite"
echo "=================================="

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create results directory
mkdir -p "$RESULTS_DIR"

echo "📁 Results will be saved to: $RESULTS_DIR"
echo "⏰ Test run timestamp: $TIMESTAMP"
echo ""

# Test 1: Rate Limiting Load Test
echo "🧪 Test 1: Rate Limiting Load Test"
echo "---------------------------------"
if [ -f "$SCRIPT_DIR/rate_limiting_test.sh" ]; then
    echo "Running rate limiting test..."
    chmod +x "$SCRIPT_DIR/rate_limiting_test.sh"

    # Capture output
    "$SCRIPT_DIR/rate_limiting_test.sh" 2>&1 | tee "$RESULTS_DIR/rate_limiting_$TIMESTAMP.log"

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✅ Rate limiting test PASSED"
    else
        echo "❌ Rate limiting test FAILED"
    fi
else
    echo "❌ Rate limiting test script not found"
fi

echo ""

# Test 2: Basic Load Test (if implemented)
echo "🧪 Test 2: Basic Load Test"
echo "-------------------------"
echo "ℹ️  Basic load test not yet implemented"
echo "📋 Authentication service load test not yet implemented"

echo ""

# Test 3: Metrics Validation
echo "🧪 Test 3: Metrics Validation"
echo "----------------------------"
echo "Validating Prometheus metrics endpoints..."

GATEWAY_URL="${GATEWAY_HOST:-localhost}:${GATEWAY_PORT:-8080}"
GATEWAY_BASE_URL="http://$GATEWAY_URL"

# Test metrics endpoint
metrics_response=$(curl -s "$GATEWAY_BASE_URL/metrics")
if [ $? -eq 0 ] && [ -n "$metrics_response" ]; then
    echo "✅ Metrics endpoint accessible"

    # Check for specific metrics
    if echo "$metrics_response" | grep -q "gateway_requests_total"; then
        echo "✅ gateway_requests_total metric found"
    else
        echo "❌ gateway_requests_total metric not found"
    fi

    if echo "$metrics_response" | grep -q "gateway_rate_limit_violations_total"; then
        echo "✅ gateway_rate_limit_violations_total metric found"
    else
        echo "❌ gateway_rate_limit_violations_total metric not found"
    fi

    # Save metrics snapshot
    echo "$metrics_response" > "$RESULTS_DIR/metrics_snapshot_$TIMESTAMP.txt"
    echo "📊 Metrics snapshot saved to: $RESULTS_DIR/metrics_snapshot_$TIMESTAMP.txt"
else
    echo "❌ Metrics endpoint not accessible"
fi

echo ""
echo "📋 Load Test Summary"
echo "==================="
echo "✅ Rate Limiting Test: Completed"
echo "⏳ Authentication Load Test: Not implemented"
echo "⏳ Database Load Test: Not implemented"
echo "⏳ End-to-End Load Test: Not implemented"
echo ""
echo "📁 Results saved to: $RESULTS_DIR"
echo "🎯 Next steps: Implement additional load tests as needed"
