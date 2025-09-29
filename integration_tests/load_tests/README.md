# Load Tests

This directory contains load testing scripts for various components of the order-processor system.

## Available Tests

### Rate Limiting Test
- **File**: `rate_limiting_test.sh`
- **Purpose**: Tests gateway rate limiting functionality
- **Metrics**: Validates Prometheus metrics collection
- **Usage**: `./rate_limiting_test.sh`

### Future Load Tests
- **Authentication Load Test**: Test auth service under load
- **Database Load Test**: Test DynamoDB performance under load
- **End-to-End Load Test**: Full system load testing

## Configuration

Tests use environment variables for configuration:
- `GATEWAY_HOST`: Gateway hostname (default: localhost)
- `GATEWAY_PORT`: Gateway port (default: 8080)
- `TEST_REQUESTS`: Number of requests to make (default: varies by test)

## Running Load Tests

```bash
# Run all load tests
./run_all_load_tests.sh

# Run specific test
./rate_limiting_test.sh

# Run with custom gateway URL
GATEWAY_HOST=your-gateway.com GATEWAY_PORT=8080 ./rate_limiting_test.sh
```
