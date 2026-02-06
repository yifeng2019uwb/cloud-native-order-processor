# Load Tests

This directory contains load testing scripts for various components of the order-processor system.

**📖 Documentation Structure:**
- **This file** (`README.md`): Quick overview and getting started guide
- **`k6/README.md`**: Detailed technical documentation, setup instructions, configuration details, and metrics analysis

All load tests use k6 for comprehensive testing. See `k6/README.md` for detailed technical information.

## Available Tests

### k6 Load Tests
All load tests use k6 for comprehensive testing. See `k6/README.md` for detailed setup, configuration, and reporting information.

**Test Scripts:**
- `k6/rate-limiting.js` - Rate limit enforcement and headers (TC-RL-001, TC-RL-002) ✅
- `k6/circuit-breaker.js` - Circuit breaker trip and recovery (TC-CB-001, TC-CB-002) ✅
- `k6/lock-management.js` - Concurrent operations (TC-LOCK-001) ✅
- `k6/latency.js` - P90/P99 latency measurement (TC-LATENCY-001) ✅

| Test Case | Status | Focus |
|-----------|--------|-------|
| Rate Limiting | ✅ Pass | Gateway/Redis efficiency |
| Circuit Breaker | ✅ Pass | System fault tolerance |
| Lock Management | ✅ Pass | Data consistency under stress |
| Latency | ✅ Pass | P99 Baseline |

**Notes**:
- Monitoring and audit log tests are excluded - they test internal admin APIs, not customer-facing endpoints
- Resilience test is skipped - keeping simple for personal project (other tests already verify system stability)

## Configuration

### Environment Variables

Tests use environment variables for configuration:
- `GATEWAY_HOST`: Gateway hostname (default: localhost)
- `GATEWAY_PORT`: Gateway port (default: 8080)
- `GATEWAY_RATE_LIMIT`: Gateway rate limit in requests per minute (default: 10000 req/min)
- `TEST_REQUESTS`: Number of requests to make (default: varies by test)

### Rate Limit Configuration

The API Gateway rate limiting is configurable via the `GATEWAY_RATE_LIMIT` environment variable:

- **Gateway Rate Limit**: Configurable via `GATEWAY_RATE_LIMIT` (default: 10,000 req/min)
- **Service-Specific Rate Limits**:
  - Inventory Service: 7,500 req/min
  - User Service: 5,000 req/min
  - Order Service: 3,000 req/min

Rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`) are preserved and returned in all responses (fixed in BUG-002).

### Test Optimizations

Tests have been optimized for memory efficiency while maintaining test integrity:
- **Rate Limiting Test**: 150 VUs, 30s duration (reduced from 200 VUs, 1m)
- **Latency Test**: 5 VUs, 50s duration (15s ramp-up, 30s steady, 5s ramp-down)
- **Lock Management Test**: 50 VUs max, reduced request rates

These optimizations significantly reduce memory usage while still meeting all test requirements.

**Note on Memory Constraints**: Test configurations are optimized for a limited memory local environment. VU counts and durations have been set accordingly to work within these constraints.

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

# Run with custom gateway rate limit
GATEWAY_RATE_LIMIT=20000 ./run_load_tests.sh
```

## Test Results

Test results are automatically saved to the `results/` directory with timestamps:
- `{test_name}_YYYYMMDD_HHMMSS.log` - Console output log (human-readable)
- For circuit breaker: `circuit-breaker-trip_*.log` and `circuit-breaker-recover_*.log`

See `k6/README.md` for detailed information about metrics and report analysis.

## Recent Updates

- **Rate Limit Configuration**: Gateway rate limit is now configurable via `GATEWAY_RATE_LIMIT` environment variable (default: 10,000 req/min)
- **BUG-002 Fix**: Rate limit headers are now properly preserved and returned in gateway responses
- **Memory Optimizations**: Test configurations optimized to reduce memory usage while maintaining test coverage
- **Service Rate Limits**: Updated service-specific rate limits (Inventory: 7500, User: 5000, Order: 3000 req/min)
