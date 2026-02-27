# Integration Tests

Enterprise-grade integration testing for the cloud-native order processor.

## ✅ **Latest Update (2026-02-06): Redis IP-block docs & runbook**

- ✅ **Redis IP-block (SEC-011)**: Before/after clearing, check **both** `ip_block:*` (blocked IPs) and `login_fail:*` (failure count; next 401 can re-block). Clear both key families before user/auth integration tests. See §2 below and [incident/README.md](incident/README.md).
- ✅ Runbook [failed-login-burst.md](../docs/runbooks/failed-login-burst.md) §5 aligned: check state → clear both → verify with KEYS → run tests.

Previous refactor (test suite): `TestUserManager.create_test_user()`, direct assertions, single status code `== 200`, test isolation, 100% pass across 17 test files.

## 🏗️ Architecture

```
integration_tests/
├── auth/              # Gateway auth requirement tests
├── config/             # API endpoints, service URLs, constants
├── smoke/              # Basic connectivity / health checks
├── utils/              # User manager, retry, reporting helpers
├── user_services/      # User API tests: auth, balance, portfolio, insights
├── inventory_service/  # Asset/inventory API tests
├── order_service/      # Order, health, asset-transaction tests
├── incident/           # Incident/security (e.g. IP block SEC-011)
├── load_tests/         # K6 load and resilience (see load_tests/README.md)
├── infrastructure/     # Env/infrastructure validation (see README-Infrastructure-Tests.md)
├── reports/            # Generated test reports
├── run_all_tests.sh    # Main test runner
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Clear Redis IP-block state (required before user/auth tests)

If the gateway uses Redis for IP blocking (SEC-011), clear **both** `ip_block:*` and `login_fail:*` before running integration tests, or tests may get **403 AUTH_004 (IP blocked)**. From the directory where `docker-compose.yml` runs (e.g. `docker/`):

**Check current state** (blocked IPs vs failure counters — both matter):

```bash
docker compose exec redis redis-cli KEYS "ip_block:*"    # IPs currently blocked (403)
docker compose exec redis redis-cli KEYS "login_fail:*"  # IPs with failure count (next 401 can trigger block)
```

Clear both key families:

```bash
docker compose exec redis redis-cli --scan --pattern "ip_block:*"   | xargs -I {} docker compose exec -T redis redis-cli DEL {}
docker compose exec redis redis-cli --scan --pattern "login_fail:*" | xargs -I {} docker compose exec -T redis redis-cli DEL {}
```

Verify: run the two `KEYS` commands again; both should return `(empty array)`. Then run tests immediately.

**Details**: [incident/README.md](incident/README.md#before-running-userintegration-tests-avoid-403-auth_004) · **Runbook**: [docs/runbooks/failed-login-burst.md](../docs/runbooks/failed-login-burst.md).

### 3. Run All Tests
```bash
# Run all integration tests
./run_all_tests.sh all

# Run specific service tests
./run_all_tests.sh user      # User service only
./run_all_tests.sh inventory # Inventory service only
./run_all_tests.sh order     # Order service only
./run_all_tests.sh insights  # Insights service only
./run_all_tests.sh auth      # Auth requirement tests
./run_all_tests.sh smoke     # Health checks only
./run_all_tests.sh incident  # Incident tests (e.g. IP block SEC-011; not included in 'all')
```

### 4. View Reports
```bash
# Open HTML report in browser
open reports/test_report_*.html

# View JSON report
cat reports/test_report_*.json
```

### 5. Load Tests
For performance and stress testing (rate limiting, circuit breaker, lock management, latency), see the **[Load Tests documentation](load_tests/README.md)**:
```bash
cd load_tests
./run_load_tests.sh
```

## 🧪 Test Categories

### Smoke Tests (Health Checks)
- **Purpose**: Verify basic connectivity and service health
- **Tests**: All service health endpoints, root endpoints
- **Status**: ✅ Implemented - Comprehensive health checks for all services
- **Frequency**: Run before functional tests

### User Service Tests
- **Purpose**: Test user authentication and balance management
- **Status**: ✅ Fully Implemented - 8 test suites with 100+ test cases
- **Coverage**: Registration, login, profile, logout, balance, deposit, withdraw, transactions

### Inventory Service Tests
- **Purpose**: Test asset management and inventory operations
- **Status**: ✅ Fully Implemented - 1 test suite with comprehensive coverage
- **Coverage**: Asset listing, retrieval, validation, schema, performance

### Order Service Tests
- **Purpose**: Test order management and portfolio operations
- **Status**: ✅ Fully Implemented - 7 test suites with comprehensive coverage
- **Coverage**: Health, orders (list/create/get), portfolio, asset balances, transactions

### Insights Service Tests
- **Purpose**: Test AI portfolio insights endpoint (Google Gemini)
- **Status**: ✅ Fully Implemented - 1 test suite
- **Coverage**: Auth required, empty portfolio message, portfolio with orders returns summary

### Load Tests
- **Purpose**: Performance and stress testing for security features and system reliability
- **Status**: ✅ Fully Implemented - 4 test suites using k6
- **Documentation**: See **[Load Tests README](load_tests/README.md)** and **[k6 Tests README](load_tests/k6/README.md)** for detailed information
- **Coverage**: Rate limiting, circuit breaker, lock management, latency measurement

| Test Case | Status | Focus |
|-----------|--------|-------|
| Rate Limiting | ✅ Pass | Gateway/Redis efficiency |
| Circuit Breaker | ✅ Pass | System fault tolerance |
| Lock Management | ✅ Pass | Data consistency under stress |
| Latency | ✅ Pass | P99 Baseline |

**Note**: Load test configurations are optimized for a limited memory local environment. VU counts and durations have been set accordingly to work within these constraints. This helps understand the solution's resource efficiency and scalability characteristics.

For detailed load test documentation, configuration, and running instructions, please refer to **[load_tests/README.md](load_tests/README.md)**.

## ⚙️ Configuration

### Service Detection
The test suite automatically detects whether services are running on Docker or Kubernetes:
- **Docker**: `http://localhost:8000`, `http://localhost:8001`, `http://localhost:8002`
- **Kubernetes**: Service URLs from K8s configuration

### Environment Variables
```bash
# Override service URLs if needed
export USER_SERVICE_URL="http://localhost:8000"
export INVENTORY_SERVICE_URL="http://localhost:8001"
export ORDER_SERVICE_URL="http://localhost:8002"

# Environment (optional - defaults to 'dev')
export ENVIRONMENT="dev"
```

### Test Configuration
```python
# Timeouts and retry settings
TIMEOUT = 10  # seconds
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1  # seconds
```

## 🎯 Enterprise Features

### Test Data Management
- **UUID-based**: All test data uses UUIDs to prevent conflicts
- **Automatic Cleanup**: Test data is cleaned up after each run
- **Isolation**: Each test run is independent

### Error Handling
- **Retry Logic**: Simple retry for network issues
- **Graceful Degradation**: Tests continue even if some endpoints fail
- **Connection Error Handling**: Robust handling of connection issues

### Comprehensive Coverage
- **Authentication**: All endpoints test unauthorized access
- **Validation**: Input validation and edge case testing
- **Performance**: Response time monitoring
- **Schema Validation**: Response structure verification
- **Error Scenarios**: 4xx error handling testing

## 📊 Test Results

### Current Status
- **Total Test Suites**: 17
- **Total Test Cases**: 210+
- **Coverage**: All major service endpoints
- **Success Rate**: 100% (all tests passing)

### Recent Fixes
- **API-003**: Fixed User Service profile endpoint from `/auth/me` to `/auth/profile`
- **Endpoint Configuration**: Corrected asset transaction endpoint to use `{asset_id}` parameter
- **Test Structure**: Organized tests into granular, API-specific test suites

## 🔧 Troubleshooting

### Common Issues
1. **Service Not Running**: Ensure all services are deployed and healthy
2. **Port Conflicts**: Check that ports 8000, 8001, 8002 are available
3. **Authentication Errors**: Most endpoints require valid JWT tokens

### Debug Mode
```bash
# Run with verbose output
bash run_all_tests.sh user 2>&1 | tee test_output.log
```

## 📚 Additional Documentation

- **Integration Test Design**: See `../docs/design-docs/integration-test-design.md` for detailed architecture
- **API Endpoints**: See `config/api_endpoints.py` for endpoint definitions
- **Service URLs**: See `config/service_urls.py` for URL detection logic
- **Load Tests**: See `load_tests/README.md` for load testing documentation and `load_tests/k6/README.md` for detailed k6 test information