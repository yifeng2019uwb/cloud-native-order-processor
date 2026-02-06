# Load Tests

This directory contains load testing scripts for various components of the order-processor system.

## Available Tests

### k6 Load Tests
All load tests use k6 for comprehensive testing. See `k6/README.md` for details.

**Test Scripts:**
- `k6/rate-limiting.js` - Rate limit enforcement and headers (TC-RL-001, TC-RL-002) ✅
- `k6/circuit-breaker.js` - Circuit breaker trip and recovery (TC-CB-001, TC-CB-002) ✅
- `k6/lock-management.js` - Concurrent operations (TC-LOCK-001) ✅
- `k6/latency.js` - P90/P99 latency measurement (TC-LATENCY-001) ✅

**Notes**: 
- Monitoring and audit log tests are excluded - they test internal admin APIs, not customer-facing endpoints
- Resilience test is skipped - keeping simple for personal project (other tests already verify system stability)

## Configuration

Tests use environment variables for configuration:
- `GATEWAY_HOST`: Gateway hostname (default: localhost)
- `GATEWAY_PORT`: Gateway port (default: 8080)
- `TEST_REQUESTS`: Number of requests to make (default: varies by test)

## Running Load Tests

```bash
# Run all load tests (recommended - handles setup automatically)
./run_load_tests.sh

# Run specific test suite
./run_load_tests.sh rate-limiting
./run_load_tests.sh circuit-breaker
./run_load_tests.sh lock-management
./run_load_tests.sh latency

# Run with custom gateway URL
GATEWAY_HOST=your-gateway.com GATEWAY_PORT=8080 ./run_load_tests.sh
```
