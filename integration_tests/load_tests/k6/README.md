# k6 Load Tests

Load testing scripts for security feature validation.

## Setup

1. Install k6 (if not already installed):
   ```bash
   ./setup/install_dependencies.sh
   ```

2. Create load test user:
   ```bash
   python3 setup/create_load_test_users.py
   ```

3. Set environment variables (optional, defaults to localhost:8080):
   ```bash
   export GATEWAY_HOST=localhost
   export GATEWAY_PORT=8080
   ```

## Running Tests

### Quick Start (Recommended)

Use the `run_load_tests.sh` script which handles all setup automatically:

```bash
# From integration_tests/load_tests/ directory:
cd integration_tests/load_tests

# Run all load tests (installs dependencies, creates users, runs tests)
./run_load_tests.sh

# Run specific test suite
./run_load_tests.sh rate-limiting
./run_load_tests.sh lock-management
./run_load_tests.sh latency

# See all options
./run_load_tests.sh --help
```

### Manual Execution

If you prefer to run tests manually:

```bash
# From integration_tests/load_tests/ directory:
cd integration_tests/load_tests

# 1. Install dependencies (if not already done)
./setup/install_dependencies.sh

# 2. Create load test users
python3 setup/create_load_test_users.py

# 3. Run individual test
k6 run k6/rate-limiting.js

# 4. Run all tests
./run_load_tests.sh
```

**Note:** The `test_user.json` file is saved to `k6/test_user.json` (relative to `load_tests` directory). Always run k6 from the `load_tests` directory.

## Test Scripts

- `rate-limiting.js` - Rate limit enforcement and headers (TC-RL-001, TC-RL-002) ✅
- `circuit-breaker.js` - Circuit breaker trip and recovery (TC-CB-001, TC-CB-002) ✅
- `lock-management.js` - Concurrent operations (TC-LOCK-001) ✅
- `latency.js` - P90/P99 latency measurement (TC-LATENCY-001) ✅

| Test Case | Status | Focus |
|-----------|--------|-------|
| Rate Limiting | ✅ Pass | Gateway/Redis efficiency |
| Circuit Breaker | ✅ Pass | System fault tolerance |
| Lock Management | ✅ Pass | Data consistency under stress |
| Latency | ✅ Pass | P99 Baseline |

**Notes**: 
- Monitoring and audit log tests are excluded - they test internal admin APIs, not customer-facing endpoints
- Resilience test is skipped - keeping simple for personal project (other tests already verify system stability under load)

## Configuration

### Environment Variables

- **Gateway URL**: Read from `GATEWAY_HOST` and `GATEWAY_PORT` environment variables
- **Gateway Rate Limit**: Configurable via `GATEWAY_RATE_LIMIT` (default: 10,000 req/min)
- **Test users**: Pre-created via `setup/create_load_test_users.py`
- **Test data**: Uses `load_test_*` prefix

### ⚠️ Memory Constraints

**Note**: Test configurations are optimized for a limited memory local environment. VU counts and durations have been set accordingly to work within these constraints. This helps understand the solution's resource efficiency and scalability characteristics.

### Rate Limit Configuration

The API Gateway implements IP-based rate limiting using Redis:

- **Gateway Rate Limit**: Configurable via `GATEWAY_RATE_LIMIT` environment variable
  - Default: 10,000 requests per minute (~166 req/sec)
  - Set in `docker-compose.yml` or via environment variable
- **Service-Specific Rate Limits** (configured in `gateway/pkg/constants/constants.go`):
  - Inventory Service: 7,500 req/min
  - User Service: 5,000 req/min
  - Order Service: 3,000 req/min

**Rate Limit Headers**: All responses include rate limit headers:
- `X-RateLimit-Limit`: Maximum requests allowed per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when the rate limit window resets

These headers are preserved even when proxying backend responses (BUG-002 fix).

### Test Configurations

**Rate Limiting Test** (`rate-limiting.js`):
- VUs: 150
- Duration: 30s
- Purpose: Exceed gateway rate limit to verify enforcement
- Expected: 429 responses after exceeding limit

**Latency Test** (`latency.js`):
- VUs: 5
- Duration: 50s (15s ramp-up, 30s steady, 5s ramp-down)
- Sleep: 100ms between requests
- Purpose: Measure P90/P95/P99 latency across multiple endpoints
- Thresholds: P90<500ms, P95<1000ms, P99<2000ms

**Lock Management Test** (`lock-management.js`):
- Max VUs: 50
- Request Rate: 30 req/s
- Duration: ~10s
- Purpose: Verify user-level locking prevents race conditions

**Circuit Breaker Test** (`circuit-breaker.js`):
- VUs: 1
- Purpose: Test circuit breaker trip and recovery mechanisms

**Note**: All test configurations are optimized for limited local memory. Increasing VUs or durations may cause memory issues.

## Reporting

k6 provides multiple output formats for test results. Results are saved to the `results/` directory.

### Standard Output

k6 displays real-time metrics in the console:
- Request rate (req/s)
- Response times (min, avg, max, p90, p95, p99)
- Status code distribution
- Threshold pass/fail status

### Generate Reports

**Default**: Tests automatically save log files to `results/` directory with timestamps.

**Optional Formats** (if needed for analysis):
```bash
# JSON output (for programmatic analysis)
k6 run --out json=results/rate-limiting.json k6/rate-limiting.js

# CSV output (for spreadsheet analysis)
k6 run --out csv=results/rate-limiting.csv k6/rate-limiting.js

# Summary only (suppress real-time output)
k6 run --quiet k6/rate-limiting.js
```

**Note**: For personal project, log files are usually sufficient. JSON/CSV only needed for automated analysis.

### Report Files Location

All reports are saved to: `integration_tests/load_tests/results/`

Files are timestamped when using `run_load_tests.sh`:
- `{test_name}_YYYYMMDD_HHMMSS.log` - Console output log (human-readable)
- For circuit breaker: `circuit-breaker-trip_*.log` and `circuit-breaker-recover_*.log`

### Key Metrics to Review

**Rate Limiting Tests:**
- `http_req_status{status:429}` - Count of rate limit violations
- `http_req_duration` - Response time (p95, p99)
- `X-RateLimit-*` headers - Rate limit headers present (should be present in all responses)
- **Note**: Tests are configured to exceed the gateway rate limit, so high 429 rates are expected

**Circuit Breaker Tests:**
- `http_req_status{status:503}` - Circuit breaker trips
- Request success rate before/after trip

**Lock Management Tests:**
- `http_req_duration` - p99 latency (should spike during lock contention)
- `http_req_status{status:429}` - Verified that lock timeouts are mapped to 429 (Too Many Requests) instead of 503, aligning with API semantic best practices
- Request success rate (only one should succeed)

**Latency Tests:**
- `http_req_duration` - p90, p95, p99 percentiles
- Compare against thresholds defined in test scripts (P90<500ms, P95<1000ms, P99<2000ms)
- **Note**: Test accepts 429 (rate limited) responses as valid for latency measurement purposes

### Integration with Monitoring

k6 results can be compared with Prometheus metrics (for analysis, not load testing):
1. Run load test
2. Check Prometheus metrics endpoint: `http://localhost:8080/metrics` (internal admin API)
3. Compare k6 metrics with Prometheus counters (e.g., `gateway_rate_limit_violations_total`)

**Note**: Prometheus `/metrics` endpoints are internal admin APIs and are not included in load tests.

### Example Report Analysis

```bash
# View log file (human-readable)
cat results/rate-limiting_YYYYMMDD_HHMMSS.log

# Or if JSON needed for analysis:
k6 run --out json=results/rate-limiting.json k6/rate-limiting.js
cat results/rate-limiting.json | jq '.metrics.http_req_status.values'
```
