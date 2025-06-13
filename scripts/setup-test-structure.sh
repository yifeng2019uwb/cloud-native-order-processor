#!/bin/bash
# File: scripts/setup-test-structure.sh
# setup-test-structure.sh - Create the complete test directory structure

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🏗️ Setting up test directory structure..."
echo "Project root: $PROJECT_ROOT"

# Create main test directories
mkdir -p "$PROJECT_ROOT/tests"
mkdir -p "$PROJECT_ROOT/tests/integration"
mkdir -p "$PROJECT_ROOT/tests/integration/infrastructure"
mkdir -p "$PROJECT_ROOT/tests/integration/services"
mkdir -p "$PROJECT_ROOT/tests/integration/workflows"
mkdir -p "$PROJECT_ROOT/tests/e2e"
mkdir -p "$PROJECT_ROOT/tests/load"
mkdir -p "$PROJECT_ROOT/tests/fixtures"
mkdir -p "$PROJECT_ROOT/test-results"
mkdir -p "$PROJECT_ROOT/scripts"

# Create __init__.py files for Python package structure
touch "$PROJECT_ROOT/tests/__init__.py"
touch "$PROJECT_ROOT/tests/integration/__init__.py"
touch "$PROJECT_ROOT/tests/integration/infrastructure/__init__.py"
touch "$PROJECT_ROOT/tests/integration/services/__init__.py"
touch "$PROJECT_ROOT/tests/integration/workflows/__init__.py"
touch "$PROJECT_ROOT/tests/e2e/__init__.py"
touch "$PROJECT_ROOT/tests/load/__init__.py"

# Create conftest.py
cat > "$PROJECT_ROOT/tests/conftest.py" << 'EOF'
"""
File: tests/conftest.py
Shared test configuration and fixtures for the Order Processor project.
"""

import pytest
import boto3
import subprocess
import os
import json
from pathlib import Path

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "infrastructure: Infrastructure integration tests")
    config.addinivalue_line("markers", "services: Service integration tests")
    config.addinivalue_line("markers", "workflows: End-to-end workflow tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "aws: Tests that require AWS credentials")

@pytest.fixture(scope="session")
def project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def terraform_outputs(project_root):
    """Get Terraform outputs for use across all tests"""
    terraform_dir = project_root / "terraform"

    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to get Terraform outputs: {e.stderr}")
    except FileNotFoundError:
        pytest.fail("Terraform not found. Ensure Terraform is installed.")

@pytest.fixture(scope="session")
def aws_session():
    """Create AWS session for tests"""
    try:
        session = boto3.Session()
        # Verify credentials work
        sts = session.client('sts')
        sts.get_caller_identity()
        return session
    except Exception as e:
        pytest.fail(f"AWS credentials not configured: {e}")

@pytest.fixture(scope="session")
def aws_account_id(aws_session):
    """Get AWS account ID"""
    sts = aws_session.client('sts')
    identity = sts.get_caller_identity()
    return identity['Account']

@pytest.fixture(scope="session")
def aws_region(aws_session):
    """Get AWS region"""
    return aws_session.region_name or 'us-west-2'

def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their path"""
    for item in items:
        # Add markers based on test file location
        if "infrastructure" in str(item.fspath):
            item.add_marker(pytest.mark.infrastructure)
            item.add_marker(pytest.mark.aws)
            item.add_marker(pytest.mark.slow)
        elif "services" in str(item.fspath):
            item.add_marker(pytest.mark.services)
            item.add_marker(pytest.mark.aws)
        elif "workflows" in str(item.fspath):
            item.add_marker(pytest.mark.workflows)
            item.add_marker(pytest.mark.aws)
            item.add_marker(pytest.mark.slow)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.slow)
        elif "load" in str(item.fspath):
            item.add_marker(pytest.mark.slow)
EOF

# Create pytest.ini
cat > "$PROJECT_ROOT/pytest.ini" << 'EOF'
# File: pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --color=yes
    --durations=10
markers =
    infrastructure: Infrastructure integration tests
    services: Service integration tests
    workflows: End-to-end workflow tests
    slow: Slow running tests
    aws: Tests that require AWS credentials
    skip_ci: Skip in CI environment

# Test timeout (10 minutes for infrastructure tests)
timeout = 600
EOF

# Create test requirements
cat > "$PROJECT_ROOT/tests/requirements-test.txt" << 'EOF'
# File: tests/requirements-test.txt
# Core testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-timeout==2.2.0
pytest-xdist==3.5.0
pytest-html==4.1.1

# AWS SDK
boto3==1.34.0
botocore==1.34.0

# Kubernetes testing (optional)
kubernetes==28.1.0

# HTTP testing
requests==2.31.0
httpx==0.25.2

# JSON and data handling
pydantic==2.5.0

# Database testing
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Load testing (for later phases)
locust==2.17

# Development utilities
python-dotenv==1.0.0
pyyaml==6.0.1
EOF

# Create README for tests
cat > "$PROJECT_ROOT/tests/README.md" << 'EOF'
# File: tests/README.md
# Integration Tests

This directory contains integration tests for the Cloud-Native Order Processor project.

## Test Structure

```
tests/
├── integration/
│   ├── infrastructure/     # AWS infrastructure validation tests
│   ├── services/          # Service integration tests
│   └── workflows/         # End-to-end workflow tests
├── e2e/                   # Full system end-to-end tests
├── load/                  # Performance and load tests
├── fixtures/              # Test data and fixtures
└── conftest.py           # Shared test configuration
```

## Running Tests

### Prerequisites

1. **AWS Credentials**: Configure AWS CLI with appropriate credentials
2. **Terraform**: Ensure infrastructure is deployed
3. **Python**: Python 3.11+ with pip

### Install Test Dependencies

```bash
pip install -r tests/requirements-test.txt
```

### Run Infrastructure Tests

```bash
# Quick run
pytest tests/integration/infrastructure/ -v

# Full run with reports
./scripts/run-infrastructure-tests.sh

# Using Makefile
make test-infrastructure
```

### Run Specific Test Categories

```bash
# Infrastructure tests only
pytest -m infrastructure

# Service integration tests
pytest -m services

# Workflow tests
pytest -m workflows

# Slow tests
pytest -m slow

# AWS-dependent tests
pytest -m aws
```

### Test Configuration

Tests are configured via `pytest.ini` and support the following markers:

- `infrastructure`: Infrastructure validation tests
- `services`: Service integration tests
- `workflows`: End-to-end workflow tests
- `slow`: Tests that take more than 30 seconds
- `aws`: Tests requiring AWS credentials
- `skip_ci`: Tests to skip in CI environment

### Environment Variables

- `SKIP_TERRAFORM_CHECK`: Skip Terraform state validation
- `PARALLEL_TESTS`: Enable parallel test execution
- `GENERATE_REPORT`: Generate HTML and XML test reports
- `AWS_REGION`: Override default AWS region

## Test Reports

Test reports are generated in the `test-results/` directory:

- `infrastructure-tests.html`: HTML test report
- `infrastructure-tests.xml`: JUnit XML report
- `coverage/`: Coverage reports
- `test-summary.md`: Executive summary

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   ```bash
   aws configure
   # or
   export AWS_ACCESS_KEY_ID=your-key
   export AWS_SECRET_ACCESS_KEY=your-secret
   ```

2. **Terraform Outputs Not Available**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

3. **Test Dependencies Missing**
   ```bash
   pip install -r tests/requirements-test.txt
   ```

### Debug Mode

Run tests with additional debugging:

```bash
pytest tests/integration/infrastructure/ -v -s --tb=long
```

### Skip Slow Tests

```bash
pytest tests/integration/infrastructure/ -m "not slow"
```
EOF

# Create helper script to validate test setup
cat > "$PROJECT_ROOT/scripts/validate-test-setup.sh" << 'EOF'
#!/bin/bash
# File: scripts/validate-test-setup.sh
# validate-test-setup.sh - Validate test environment setup

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔍 Validating test environment setup..."

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 available: $(python3 --version)"
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Check pip
if command -v pip &> /dev/null; then
    echo "✅ pip available: $(pip --version)"
else
    echo "❌ pip not found"
    exit 1
fi

# Check pytest installation
if python3 -c "import pytest" 2>/dev/null; then
    echo "✅ pytest installed: $(pytest --version)"
else
    echo "❌ pytest not installed"
    echo "Install with: pip install -r tests/requirements-test.txt"
    exit 1
fi

# Check AWS CLI
if command -v aws &> /dev/null; then
    echo "✅ AWS CLI available: $(aws --version)"
else
    echo "❌ AWS CLI not found"
    exit 1
fi

# Check AWS credentials
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ AWS credentials configured"
else
    echo "❌ AWS credentials not configured"
    exit 1
fi

# Check Terraform
if command -v terraform &> /dev/null; then
    echo "✅ Terraform available: $(terraform version -json | jq -r '.terraform_version')"
else
    echo "❌ Terraform not found"
    exit 1
fi

# Check test directory structure
required_dirs=(
    "tests"
    "tests/integration"
    "tests/integration/infrastructure"
    "test-results"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        echo "✅ Directory exists: $dir"
    else
        echo "❌ Directory missing: $dir"
        exit 1
    fi
done

# Check test files exist
required_files=(
    "tests/conftest.py"
    "tests/requirements-test.txt"
    "pytest.ini"
)

for file in "${required_files[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo "✅ File exists: $file"
    else
        echo "❌ File missing: $file"
        exit 1
    fi
done

echo ""
echo "🎉 Test environment validation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Install test dependencies: pip install -r tests/requirements-test.txt"
echo "2. Run infrastructure tests: ./scripts/run-infrastructure-tests.sh"
echo "3. Check test results in: test-results/"
EOF

# Make scripts executable
chmod +x "$PROJECT_ROOT/scripts/validate-test-setup.sh"

# Create quick test runner for development
cat > "$PROJECT_ROOT/scripts/quick-test.sh" << 'EOF'
#!/bin/bash
# File: scripts/quick-test.sh
# quick-test.sh - Quick test runner for development

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Quick test options
TEST_TYPE=${1:-"infrastructure"}
VERBOSE=${2:-"false"}

print_status "🚀 Quick Test Runner"
print_status "Test type: $TEST_TYPE"

cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d ".venv-tests" ]; then
    source .venv-tests/bin/activate
    print_status "Using test virtual environment"
fi

# Set Python path
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

case $TEST_TYPE in
    "infrastructure"|"infra")
        print_status "Running infrastructure tests..."
        if [ "$VERBOSE" = "true" ]; then
            pytest tests/integration/infrastructure/ -v -s
        else
            pytest tests/integration/infrastructure/ -v
        fi
        ;;
    "services")
        print_status "Running service integration tests..."
        if [ "$VERBOSE" = "true" ]; then
            pytest tests/integration/services/ -v -s
        else
            pytest tests/integration/services/ -v
        fi
        ;;
    "workflows")
        print_status "Running workflow tests..."
        if [ "$VERBOSE" = "true" ]; then
            pytest tests/integration/workflows/ -v -s
        else
            pytest tests/integration/workflows/ -v
        fi
        ;;
    "all")
        print_status "Running all integration tests..."
        if [ "$VERBOSE" = "true" ]; then
            pytest tests/integration/ -v -s
        else
            pytest tests/integration/ -v
        fi
        ;;
    "validate")
        print_status "Validating test setup..."
        ./scripts/validate-test-setup.sh
        ;;
    *)
        echo "Usage: $0 [test_type] [verbose]"
        echo ""
        echo "Test types:"
        echo "  infrastructure, infra  - Run infrastructure tests"
        echo "  services              - Run service integration tests"
        echo "  workflows            - Run workflow tests"
        echo "  all                  - Run all integration tests"
        echo "  validate             - Validate test setup"
        echo ""
        echo "Verbose: true|false (default: false)"
        echo ""
        echo "Examples:"
        echo "  $0 infrastructure"
        echo "  $0 services true"
        echo "  $0 validate"
        exit 1
        ;;
esac

print_success "Quick test completed!"
EOF

# Create test data fixtures
cat > "$PROJECT_ROOT/tests/fixtures/sample_data.py" << 'EOF'
"""
File: tests/fixtures/sample_data.py
Sample test data and fixtures for integration tests.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List

# Sample AWS resource configurations
SAMPLE_AWS_CONFIG = {
    "region": "us-west-2",
    "account_id": "123456789012",  # Will be replaced with actual
}

# Sample Terraform outputs structure
SAMPLE_TERRAFORM_OUTPUTS = {
    "eks_cluster_name": {"value": "order-processor-dev-cluster"},
    "eks_cluster_endpoint": {"value": "https://example.eks.us-west-2.amazonaws.com"},
    "database_endpoint": {"value": "order-processor-dev-postgres.abc123.us-west-2.rds.amazonaws.com:5432"},
    "database_secret_arn": {"value": "arn:aws:secretsmanager:us-west-2:123456789012:secret:order-processor-dev-db-credentials-AbCdEf"},
    "s3_events_bucket_name": {"value": "order-processor-dev-events-12345678"},
    "sns_order_events_topic_arn": {"value": "arn:aws:sns:us-west-2:123456789012:order-processor-dev-order-events"},
    "sqs_order_processing_queue_url": {"value": "https://sqs.us-west-2.amazonaws.com/123456789012/order-processor-dev-order-processing"},
    "ecr_order_api_repository_url": {"value": "123456789012.dkr.ecr.us-west-2.amazonaws.com/order-processor-dev-order-api"},
    "order_service_role_arn": {"value": "arn:aws:iam::123456789012:role/order-processor-dev-order-service-role"}
}

# Sample database credentials
SAMPLE_DB_CREDENTIALS = {
    "username": "orderuser",
    "password": "sample-password-123",
    "engine": "postgres",
    "host": "order-processor-dev-postgres.abc123.us-west-2.rds.amazonaws.com",
    "port": 5432,
    "dbname": "orderprocessor"
}

# Sample order data for testing
SAMPLE_ORDER_DATA = {
    "customer_email": "test@example.com",
    "customer_name": "Test Customer",
    "items": [
        {
            "product_id": "prod-123",
            "quantity": 2
        },
        {
            "product_id": "prod-456",
            "quantity": 1
        }
    ],
    "shipping_address": {
        "street": "123 Test Street",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "country": "US"
    }
}

# Sample product data
SAMPLE_PRODUCTS = [
    {
        "product_id": "prod-123",
        "sku": "TEST-WIDGET-001",
        "name": "Test Widget",
        "description": "A test widget for integration testing",
        "price": Decimal("29.99"),
        "category": "Widgets"
    },
    {
        "product_id": "prod-456",
        "sku": "TEST-GADGET-001",
        "name": "Test Gadget",
        "description": "A test gadget for integration testing",
        "price": Decimal("49.99"),
        "category": "Gadgets"
    }
]

# Sample inventory data
SAMPLE_INVENTORY = [
    {
        "product_id": "prod-123",
        "stock_quantity": 100,
        "reserved_quantity": 10,
        "min_stock_level": 5,
        "warehouse_location": "Warehouse A"
    },
    {
        "product_id": "prod-456",
        "stock_quantity": 50,
        "reserved_quantity": 5,
        "min_stock_level": 10,
        "warehouse_location": "Warehouse B"
    }
]

# Sample SNS/SQS messages
SAMPLE_ORDER_EVENT = {
    "event_id": "evt-123456",
    "event_type": "order_created",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "service_name": "order-service",
    "order_id": "order-789",
    "customer_email": "test@example.com",
    "data": {
        "order_id": "order-789",
        "status": "pending",
        "total_amount": "79.98",
        "currency": "USD"
    }
}

# Test timeouts and retries
TEST_TIMEOUTS = {
    "aws_api_call": 30,          # seconds
    "database_connection": 15,    # seconds
    "message_propagation": 10,    # seconds
    "eks_operation": 120,         # seconds
    "terraform_operation": 300    # seconds
}

# Expected AWS resource counts
EXPECTED_RESOURCE_COUNTS = {
    "eks_clusters": 1,
    "rds_instances": 1,
    "s3_buckets": 2,  # events + backups
    "sns_topics": 1,
    "sqs_queues": 2,  # main + dlq
    "ecr_repositories": 1,
    "iam_roles": 3,   # cluster + fargate + service
}

def get_test_order_data(order_id: str = None) -> Dict[str, Any]:
    """Generate test order data with optional custom order ID."""
    order_data = SAMPLE_ORDER_DATA.copy()
    if order_id:
        order_data["order_id"] = order_id
    return order_data

def get_test_event_data(event_type: str = "order_created") -> Dict[str, Any]:
    """Generate test event data for messaging tests."""
    event_data = SAMPLE_ORDER_EVENT.copy()
    event_data["event_type"] = event_type
    event_data["timestamp"] = datetime.now(timezone.utc).isoformat()
    return event_data

def get_expected_terraform_outputs() -> List[str]:
    """Get list of expected Terraform output keys."""
    return list(SAMPLE_TERRAFORM_OUTPUTS.keys())

def get_test_s3_object_key() -> str:
    """Generate test S3 object key with timestamp."""
    timestamp = int(datetime.now().timestamp())
    return f"integration-tests/test-object-{timestamp}.json"
EOF

# Create infrastructure test helper utilities
cat > "$PROJECT_ROOT/tests/integration/infrastructure/test_helpers.py" << 'EOF'
"""
File: tests/integration/infrastructure/test_helpers.py
Helper utilities for infrastructure integration tests.
"""

import time
import json
import boto3
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError


class AWSResourceHelper:
    """Helper class for AWS resource operations in tests."""

    def __init__(self, session: boto3.Session):
        self.session = session
        self.region = session.region_name or 'us-west-2'

    def wait_for_eks_cluster_active(self, cluster_name: str, timeout: int = 600) -> bool:
        """Wait for EKS cluster to be in ACTIVE state."""
        eks_client = self.session.client('eks')
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = eks_client.describe_cluster(name=cluster_name)
                status = response['cluster']['status']

                if status == 'ACTIVE':
                    return True
                elif status in ['FAILED', 'DELETING']:
                    raise RuntimeError(f"EKS cluster {cluster_name} is in {status} state")

                time.sleep(30)  # Check every 30 seconds

            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    raise RuntimeError(f"EKS cluster {cluster_name} not found")
                raise

        raise TimeoutError(f"EKS cluster {cluster_name} did not become active within {timeout} seconds")

    def wait_for_rds_available(self, db_identifier: str, timeout: int = 900) -> bool:
        """Wait for RDS instance to be available."""
        rds_client = self.session.client('rds')
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = rds_client.describe_db_instances(DBInstanceIdentifier=db_identifier)
                instances = response['DBInstances']

                if instances:
                    status = instances[0]['DBInstanceStatus']
                    if status == 'available':
                        return True
                    elif status in ['failed', 'deleting']:
                        raise RuntimeError(f"RDS instance {db_identifier} is in {status} state")

                time.sleep(60)  # Check every minute

            except ClientError as e:
                if e.response['Error']['Code'] == 'DBInstanceNotFoundFault':
                    raise RuntimeError(f"RDS instance {db_identifier} not found")
                raise

        raise TimeoutError(f"RDS instance {db_identifier} did not become available within {timeout} seconds")

    def test_sns_sqs_message_flow(self, topic_arn: str, queue_url: str, test_message: Dict[str, Any]) -> bool:
        """Test message flow from SNS topic to SQS queue."""
        sns_client = self.session.client('sns')
        sqs_client = self.session.client('sqs')

        # Publish test message
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(test_message),
            Subject="Integration Test Message"
        )
        message_id = response['MessageId']

        # Wait for message to appear in queue
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(2)  # Wait 2 seconds between attempts

            response = sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=5
            )

            if 'Messages' in response:
                # Message found, clean it up
                message = response['Messages'][0]
                sqs_client.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                return True

        return False

    def test_s3_bucket_operations(self, bucket_name: str, test_key: str, test_content: str) -> bool:
        """Test S3 bucket read/write operations."""
        s3_client = self.session.client('s3')

        try:
            # Test write
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content,
                ContentType='application/json'
            )

            # Test read
            response = s3_client.get_object(
                Bucket=bucket_name,
                Key=test_key
            )
            retrieved_content = response['Body'].read().decode('utf-8')

            # Test delete (cleanup)
            s3_client.delete_object(
                Bucket=bucket_name,
                Key=test_key
            )

            return retrieved_content == test_content

        except ClientError:
            return False

    def get_ecr_login_command(self, registry_id: Optional[str] = None) -> str:
        """Get ECR docker login command."""
        ecr_client = self.session.client('ecr')

        kwargs = {}
        if registry_id:
            kwargs['registryIds'] = [registry_id]

        response = ecr_client.get_authorization_token(**kwargs)
        auth_data = response['authorizationData'][0]

        return f"docker login {auth_data['proxyEndpoint']}"


class TerraformHelper:
    """Helper class for Terraform operations in tests."""

    def __init__(self, terraform_dir: str):
        self.terraform_dir = terraform_dir

    def get_output(self, output_name: str) -> Optional[str]:
        """Get specific Terraform output value."""
        import subprocess

        try:
            result = subprocess.run(
                ["terraform", "output", "-raw", output_name],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def get_all_outputs(self) -> Dict[str, Any]:
        """Get all Terraform outputs as dictionary."""
        import subprocess

        try:
            result = subprocess.run(
                ["terraform", "output", "-json"],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError:
            return {}

    def validate_configuration(self) -> bool:
        """Validate Terraform configuration."""
        import subprocess

        try:
            result = subprocess.run(
                ["terraform", "validate"],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return "Success" in result.stdout
        except subprocess.CalledProcessError:
            return False


def retry_on_aws_throttle(func, max_retries: int = 3, backoff_factor: float = 2.0):
    """Decorator to retry AWS operations on throttling errors."""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code in ['Throttling', 'ThrottlingException', 'RequestLimitExceeded']:
                    if attempt < max_retries - 1:
                        wait_time = backoff_factor ** attempt
                        time.sleep(wait_time)
                        continue
                raise
    return wrapper


def wait_for_condition(condition_func, timeout: int = 300, interval: int = 10, *args, **kwargs) -> bool:
    """Wait for a condition function to return True."""
    start_time = time.time()

    while time.time() - start_time < timeout:
        if condition_func(*args, **kwargs):
            return True
        time.sleep(interval)

    return False
EOF

# Make all scripts executable
chmod +x "$PROJECT_ROOT/scripts/quick-test.sh"

echo ""
echo "✅ Test directory structure created successfully!"
echo ""
echo "📁 Created directories:"
echo "   tests/integration/infrastructure/"
echo "   tests/integration/services/"
echo "   tests/integration/workflows/"
echo "   tests/e2e/"
echo "   tests/load/"
echo "   tests/fixtures/"
echo "   test-results/"
echo ""
echo "📄 Created files:"
echo "   tests/conftest.py"
echo "   tests/requirements-test.txt"
echo "   tests/fixtures/sample_data.py"
echo "   tests/integration/infrastructure/test_helpers.py"
echo "   pytest.ini"
echo "   scripts/validate-test-setup.sh"
echo "   scripts/quick-test.sh"
echo ""
echo "🚀 Next steps:"
echo "1. Validate setup: ./scripts/validate-test-setup.sh"
echo "2. Install dependencies: pip install -r tests/requirements-test.txt"
echo "3. Run quick test: ./scripts/quick-test.sh validate"
echo "4. Run infrastructure tests: ./scripts/run-infrastructure-tests.sh"
EOF