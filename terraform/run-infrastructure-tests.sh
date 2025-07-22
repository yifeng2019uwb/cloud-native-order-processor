#!/bin/bash
# File: terraform/run-infrastructure-tests.sh
# Simple infrastructure test runner for Terraform-managed AWS resources
# Focused on core functionality: Terraform state, AWS resources, connectivity
# Designed to be lightweight and easy to use

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(cd "${TERRAFORM_DIR}/.." && pwd)"

# Test configuration
TEST_TYPES="${TEST_TYPES:-all}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
VERBOSE="${VERBOSE:-false}"
FAIL_FAST="${FAIL_FAST:-false}"
TIMEOUT="${TIMEOUT:-1800}"  # 30 minutes

# Report configuration
REPORT_DIR="${TERRAFORM_DIR}/test-reports"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPORT_PREFIX="${ENVIRONMENT}-${TIMESTAMP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Usage information
show_usage() {
    cat << EOF
Usage: ${0} [OPTIONS]

Run infrastructure validation tests for Terraform-managed AWS resources

OPTIONS:
    -t, --test-type TYPE    Test type to run (terraform|aws|connectivity|all)
    -e, --environment ENV   Target environment (dev, staging, prod)
    -v, --verbose          Enable verbose test output
    -f, --fail-fast        Stop on first test failure
    --timeout SECONDS      Test timeout in seconds (default: 1800)
    -h, --help             Show this help message

TEST TYPES:
    terraform              Terraform configuration and state tests
    aws                    AWS resource validation tests
    connectivity           Network connectivity and endpoint tests
    all                    Run all test types (default)

EXAMPLES:
    ${0}                                    # Run all tests for dev environment
    ${0} --test-type terraform              # Run only Terraform tests
    ${0} --environment prod --verbose       # Run tests for prod with verbose output
    ${0} --fail-fast --timeout 3600         # Stop on first failure with 1-hour timeout

ENVIRONMENT VARIABLES:
    ENVIRONMENT            Target environment (default: dev)
    TEST_TYPES             Test types to run (comma-separated)
    VERBOSE                Enable verbose output (true/false)
    FAIL_FAST              Stop on first failure (true/false)
    TIMEOUT                Test timeout in seconds

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--test-type)
            TEST_TYPES="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="true"
            shift
            ;;
        -f|--fail-fast)
            FAIL_FAST="true"
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    log_error "Invalid environment: $ENVIRONMENT. Must be dev, staging, or prod"
    exit 1
fi

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi

    # Check pytest
    if ! python3 -c "import pytest" &> /dev/null; then
        log_error "pytest is required but not installed. Install with: pip install pytest"
        exit 1
    fi

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is required but not installed"
        exit 1
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials are not configured"
        exit 1
    fi

    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is required but not installed"
        exit 1
    fi

    log_success "All prerequisites satisfied"
}

# Setup test environment
setup_test_environment() {
    log_info "Setting up test environment..."

    # Create report directory
    mkdir -p "$REPORT_DIR"

    # Set environment variables for tests
    export TERRAFORM_WORKSPACE="$ENVIRONMENT"
    export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

    # Change to terraform directory
    cd "$TERRAFORM_DIR"

    log_success "Test environment setup complete"
}

# Run specific test type
run_test_type() {
    local test_type="$1"
    local report_file="$REPORT_DIR/test-${test_type}-${REPORT_PREFIX}.log"

    log_info "Running $test_type tests..."

    # Build pytest command
    local pytest_cmd="python3 -m pytest"

    # Add test directory
    case "$test_type" in
        "terraform")
            pytest_cmd="$pytest_cmd infrastructure-tests/test_terraform_state.py"
            ;;
        "aws")
            pytest_cmd="$pytest_cmd infrastructure-tests/test_aws_resources.py"
            ;;
        "connectivity")
            pytest_cmd="$pytest_cmd infrastructure-tests/test_connectivity.py"
            ;;
        *)
            log_error "Unknown test type: $test_type"
            return 1
            ;;
    esac

    # Add pytest options
    if [[ "$VERBOSE" == "true" ]]; then
        pytest_cmd="$pytest_cmd -v"
    fi

    if [[ "$FAIL_FAST" == "true" ]]; then
        pytest_cmd="$pytest_cmd -x"
    fi

    # Add timeout
    pytest_cmd="timeout $TIMEOUT $pytest_cmd"

    # Run tests and capture output
    log_info "Command: $pytest_cmd"
    if eval "$pytest_cmd" 2>&1 | tee "$report_file"; then
        log_success "$test_type tests completed successfully"
        return 0
    else
        log_error "$test_type tests failed. Check log: $report_file"
        return 1
    fi
}

# Main execution
main() {
    log_info "🚀 Starting infrastructure tests for environment: $ENVIRONMENT"
    log_info "📊 Test types: $TEST_TYPES"
    log_info "⏱️  Timeout: $TIMEOUT seconds"

    # Check prerequisites
    check_prerequisites

    # Setup environment
    setup_test_environment

    # Track overall success
    local overall_success=true

    # Run tests based on test types
    if [[ "$TEST_TYPES" == "all" ]]; then
        test_types=("terraform" "aws" "connectivity")
    else
        IFS=',' read -ra test_types <<< "$TEST_TYPES"
    fi

    for test_type in "${test_types[@]}"; do
        if ! run_test_type "$test_type"; then
            overall_success=false
            if [[ "$FAIL_FAST" == "true" ]]; then
                log_error "Stopping due to fail-fast mode"
                break
            fi
        fi
    done

    # Final summary
    if [[ "$overall_success" == "true" ]]; then
        log_success "🎉 All infrastructure tests completed successfully!"
        log_info "📁 Test reports saved in: $REPORT_DIR"
        exit 0
    else
        log_error "💥 Some infrastructure tests failed"
        log_info "📁 Check test reports in: $REPORT_DIR"
        exit 1
    fi
}

# Run main function
main "$@"