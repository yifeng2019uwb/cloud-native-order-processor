# Infrastructure Tests

## Overview
Infrastructure tests for Terraform-managed AWS resources. These tests validate that your infrastructure is properly deployed and functioning correctly.

## Test Types

### 1. Terraform State Tests (`test_terraform_state.py`)
- Validates Terraform configuration and state
- Checks for configuration drift
- Verifies resource dependencies
- Tests Terraform workspace management

### 2. AWS Resource Tests (`test_aws_resources.py`)
- Validates AWS resources exist and are properly configured
- Tests VPC, subnets, security groups
- Verifies ECS clusters and task definitions
- Checks S3 buckets and DynamoDB tables
- Validates IAM roles and policies

### 3. Connectivity Tests (`test_connectivity.py`)
- Tests network connectivity and reachability
- Validates load balancer health checks
- Tests database connectivity (if RDS is deployed)
- Verifies service endpoints and API Gateway
- Tests cross-AZ connectivity

## Usage

### Quick Start
```bash
# Run all tests for dev environment
./run-infrastructure-tests.sh

# Run specific test type
./run-infrastructure-tests.sh --test-type aws

# Run with verbose output
./run-infrastructure-tests.sh --verbose

# Run for production environment
./run-infrastructure-tests.sh --environment prod
```

### Test Options
- `--test-type`: Choose test type (terraform|aws|connectivity|all)
- `--environment`: Target environment (dev|staging|prod)
- `--verbose`: Enable detailed output
- `--fail-fast`: Stop on first failure
- `--timeout`: Set timeout in seconds (default: 1800)

### Environment Variables
- `ENVIRONMENT`: Target environment (default: dev)
- `TEST_TYPES`: Comma-separated test types
- `VERBOSE`: Enable verbose output (true/false)
- `FAIL_FAST`: Stop on first failure (true/false)
- `TIMEOUT`: Test timeout in seconds

## Prerequisites
- Python 3 with pytest
- AWS CLI with configured credentials
- Terraform installed
- Access to AWS account

## Test Reports
Test reports are saved in `../test-reports/` with timestamps for easy tracking.

## Future Enhancements
After adding Redis support, these tests will be enhanced to include:
- Redis connectivity tests
- Cache performance validation
- Redis cluster health checks
- Cache invalidation testing

## Notes
- Tests are designed to be non-destructive
- They validate existing infrastructure without making changes
- Some tests may be skipped if resources are not deployed
- Tests include proper error handling and timeouts