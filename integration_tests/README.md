# Integration Tests

Enterprise-grade integration testing for the cloud-native order processor.

## 🏗️ Architecture

```
integration_tests/
├── config/
│   └── services.yaml              # Service endpoints & configuration
├── smoke/
│   └── health_tests.py            # Basic connectivity checks
├── utils/
│   ├── test_data.py               # UUID-based test data management
│   ├── simple_retry.py            # Basic retry logic
│   └── reporting.py               # JSON/HTML test reports
├── user_services/
│   ├── __init__.py                # User services package
│   └── user_tests.py              # User registration, login, profile tests
├── inventory_service/
│   ├── __init__.py                # Inventory service package
│   └── inventory_tests.py         # Asset management, categories tests
├── reports/                       # Generated test reports
├── run_tests.py                   # Main test runner
└── README.md                      # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run All Tests
```bash
python run_tests.py
```

### 3. View Reports
```bash
# Open HTML report in browser
open reports/test_report_*.html

# View JSON report
cat reports/test_report_*.json
```

## 🧪 Test Categories

### Smoke Tests (Health Checks)
- **Purpose**: Verify basic connectivity
- **Tests**: API Gateway health, root, info endpoints
- **Frequency**: Run before functional tests

### Functional Tests (Business Logic)
- **Purpose**: Test actual business functionality
- **Tests**: User registration/login, inventory operations
- **Status**: ✅ Implemented - User and Inventory service tests available

## ⚙️ Configuration

### Environment Variables
```bash
# API Gateway URL (optional - will use config file if not set)
export API_GATEWAY_URL="http://localhost:8000"  # Replace with FastAPI service URL

# User Service URL (optional - for functional tests)
export USER_SERVICE_URL="http://localhost:8000"

# Inventory Service URL (optional - for functional tests)
export INVENTORY_SERVICE_URL="http://localhost:8001"

# Environment (optional - defaults to 'dev')
export ENVIRONMENT="dev"
```

### Configuration File (`config/services.yaml`)
```yaml
api_gateway:
  dev:
    base_url: "http://localhost:8000"  # Replace with FastAPI service URL
    timeout: 10
    retry_attempts: 3

test_config:
  cleanup_after_tests: true
  generate_reports: true
  report_format: ["json", "html"]
```

## 🎯 Enterprise Features

### Test Data Management
- **UUID-based**: All test data uses UUIDs to prevent conflicts
- **Automatic Cleanup**: Test data is cleaned up after each run
- **Isolation**: Each test run is independent

### Error Handling
- **Retry Logic**: Simple retry for network issues
- **Timeout Handling**: Configurable timeouts for external APIs
- **Graceful Degradation**: Tests continue even if some fail

### Reporting
- **JSON Reports**: Machine-readable for CI/CD integration
- **HTML Reports**: Human-readable with visual formatting
- **Metrics**: Success rates, response times, test duration

## 📊 Test Reports

### JSON Report
```json
{
  "test_run": {
    "start_time": "2024-01-01T12:00:00Z",
    "end_time": "2024-01-01T12:01:00Z",
    "duration_seconds": 60.0,
    "total_tests": 3,
    "passed_tests": 3,
    "failed_tests": 0
  },
  "summary": {
    "success_rate": 100.0,
    "average_response_time_ms": 250.5
  }
}
```

### HTML Report
- Visual test results with pass/fail indicators
- Response time metrics
- Error details for failed tests
- Professional formatting

## 🔧 Usage Examples

### Run Specific Test Categories
```bash
# Run only smoke tests
python -c "
from run_tests import IntegrationTestRunner
runner = IntegrationTestRunner()
runner.run_smoke_tests()
"

# Run with custom config
runner = IntegrationTestRunner('config/custom-services.yaml')
```

### Custom Test Data
```python
from tests.utils.test_data import TestDataManager

# Generate unique test data
data_manager = TestDataManager()
user_data = data_manager.generate_user_data()
asset_data = data_manager.generate_asset_data()
```

## 🚨 Troubleshooting

### Common Issues

#### PyYAML Not Found
```bash
pip install PyYAML
```

#### API Gateway Unreachable
1. Check if Lambda function is deployed
2. Verify API Gateway URL in config
3. Check AWS credentials and region

#### Test Data Conflicts
- Tests use UUID-based data to prevent conflicts
- If conflicts occur, check for stale test data in database

### Debug Mode
```bash
# Enable verbose logging
export DEBUG=true
python run_tests.py
```

## 🔮 Future Enhancements

### Planned Features
- [ ] Functional tests for user service
- [ ] Functional tests for inventory service
- [ ] Load testing capabilities
- [ ] CI/CD integration
- [ ] Test data seeding
- [ ] Performance benchmarking

### Monitoring Integration
- [ ] CloudWatch metrics integration
- [ ] Custom dashboards
- [ ] Alerting on test failures
- [ ] Historical test data analysis

## 📝 Contributing

### Adding New Tests
1. Create test file in appropriate category (`smoke/` or `utils/`)
2. Follow existing patterns for test structure
3. Use UUID-based test data
4. Add proper error handling and retry logic
5. Update this README

### Test Guidelines
- **Isolation**: Each test should be independent
- **Cleanup**: Always clean up test data
- **Reporting**: Use the TestReporter for consistent reporting
- **Configuration**: Use config file for environment-specific settings

## 📚 References

- [AWS API Gateway Testing](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-test-api.html)
- [Integration Testing Best Practices](https://martinfowler.com/articles/microservice-testing/)
- [Test Data Management](https://www.thoughtworks.com/insights/blog/test-data-management-strategy)