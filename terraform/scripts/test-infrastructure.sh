#!/bin/bash
# File: terraform/scripts/test-infrastructure.sh
# Test Orchestration
# Comprehensive test runner with multiple test types
# Environment preparation and validation
# Parallel test execution support
# HTML and JUnit report generation
# Detailed logging and error handling

set -euo pipefail

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${TERRAFORM_DIR}/.." && pwd)"

# Source shared utilities
source "${PROJECT_ROOT}/scripts/shared/logging-utils.sh"
source "${PROJECT_ROOT}/scripts/shared/environment-loader.sh"
source "${PROJECT_ROOT}/scripts/shared/aws-utils.sh"
source "${PROJECT_ROOT}/scripts/shared/error-handler.sh"

# Script configuration
SCRIPT_NAME="test-infrastructure"
VERSION="1.0.0"

# Test configuration
TEST_TYPES="${TEST_TYPES:-all}"
TEST_TIMEOUT="${TEST_TIMEOUT:-1800}"  # 30 minutes
TEST_PARALLEL="${TEST_PARALLEL:-false}"
TEST_VERBOSE="${TEST_VERBOSE:-false}"
TEST_COVERAGE="${TEST_COVERAGE:-false}"
PYTEST_ARGS="${PYTEST_ARGS:-}"
REPORT_FORMAT="${REPORT_FORMAT:-html}"
FAIL_FAST="${FAIL_FAST:-false}"
DRY_RUN="${DRY_RUN:-false}"

# Report configuration
REPORT_DIR="${TERRAFORM_DIR}/test-reports"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPORT_PREFIX="${ENVIRONMENT:-unknown}-${TIMESTAMP}"

# Usage information
show_usage() {
    cat << EOF
Usage: ${0} [OPTIONS]

Run infrastructure validation tests for Terraform-managed AWS resources

OPTIONS:
    -t, --test-type TYPE    Test type to run (terraform|aws|connectivity|security|all)
    -e, --environment ENV   Target environment (dev, staging, ci, prod)
    -p, --parallel         Run tests in parallel
    -v, --verbose          Enable verbose test output
    -d, --debug            Enable debug mode
    -c, --coverage         Generate test coverage report
    -f, --fail-fast        Stop on first test failure
    --dry-run              Show what would be tested without running
    --timeout SECONDS      Test timeout in seconds (default: 1800)
    --report-format FORMAT Report format (html|xml|json|all) (default: html)
    --pytest-args ARGS     Additional arguments to pass to pytest
    -h, --help             Show this help message

TEST TYPES:
    terraform              Terraform configuration and state tests
    aws                    AWS resource validation tests
    connectivity           Network connectivity and endpoint tests
    security               Security and compliance tests
    performance            Performance and load tests
    all                    Run all test types (default)

EXAMPLES:
    ${0}                                    # Run all tests for auto-detected environment
    ${0} --test-type terraform              # Run only Terraform tests
    ${0} --environment dev --verbose        # Run tests for dev with verbose output
    ${0} --parallel --timeout 3600          # Run tests in parallel with 1-hour timeout
    ${0} --test-type security --fail-fast   # Run security tests and stop on first failure
    ${0} --dry-run                          # Show what tests would run
    ${0} --coverage --report-format all     # Generate coverage and all report formats

ENVIRONMENT VARIABLES:
    ENVIRONMENT            Target environment (auto-detected if not set)
    TEST_TYPES             Test types to run (comma-separated)
    TEST_TIMEOUT           Test timeout in seconds
    TEST_PARALLEL          Enable parallel testing (true/false)
    TEST_VERBOSE           Enable verbose output (true/false)
    TEST_COVERAGE          Generate coverage report (true/false)
    PYTEST_ARGS            Additional pytest arguments
    REPORT_FORMAT          Report format (html|xml|json|all)
    FAIL_FAST              Stop on first failure (true/false)
    DRY_RUN                Show tests without running (true/false)

CONFIGURATION:
    The script uses the shared environment configuration from:
    - ${PROJECT_ROOT}/config/environments/.env.defaults
    - ${PROJECT_ROOT}/config/environments/.env.{environment}
    - ${PROJECT_ROOT}/config/environments/.env.local (if exists)

REPORTS:
    Test reports are generated in: ${REPORT_DIR}/
    - HTML report: infrastructure-test-report-{timestamp}.html
    - JUnit XML: junit-results-{timestamp}.xml
    - Coverage report: coverage-{timestamp}.html (if --coverage used)

EOF
}

# Parse command line arguments
parse_arguments() {
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
            -p|--parallel)
                TEST_PARALLEL="true"
                shift
                ;;
            -v|--verbose)
                TEST_VERBOSE="true"
                shift
                ;;
            -d|--debug)
                DEBUG_MODE="true"
                LOG_LEVEL="DEBUG"
                shift
                ;;
            -c|--coverage)
                TEST_COVERAGE="true"
                shift
                ;;
            -f|--fail-fast)
                FAIL_FAST="true"
                shift
                ;;
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            --timeout)
                TEST_TIMEOUT="$2"
                shift 2
                ;;
            --report-format)
                REPORT_FORMAT="$2"
                shift 2
                ;;
            --pytest-args)
                PYTEST_ARGS="$2"
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
}

# Check test prerequisites
check_test_prerequisites() {
    log_subsection "Checking Test Prerequisites"

    local missing_tools=()

    # Check Python
    if ! command -v python3 >/dev/null 2>&1; then
        missing_tools+=("python3")
    fi

    # Check required Python packages
    local required_packages=(
        "boto3"
        "requests"
        "pytest"
    )

    for package in "${required_packages[@]}"; do
        if ! python3 -c "import ${package}" 2>/dev/null; then
            missing_tools+=("python-${package}")
        fi
    done

# Check optional packages for enhanced functionality
    local optional_packages=(
        "pytest-html:HTML reports"
        "pytest-cov:Coverage reports"
        "pytest-xdist:Parallel execution"
        "pytest-json-report:JSON reports"
    )

    for package_info in "${optional_packages[@]}"; do
        local package="${package_info%%:*}"
        local description="${package_info##*:}"

        if ! python3 -c "import ${package//-/_}" 2>/dev/null; then
            log_warn "Optional package missing: ${package} (${description})"
            if [[ "${package}" == "pytest-html" && "${REPORT_FORMAT}" =~ html ]]; then
                log_warn "HTML report format requested but pytest-html not available"
            elif [[ "${package}" == "pytest-cov" && "${TEST_COVERAGE}" == "true" ]]; then
                missing_tools+=("python-${package}")
            elif [[ "${package}" == "pytest-xdist" && "${TEST_PARALLEL}" == "true" ]]; then
                missing_tools+=("python-${package}")
            fi
        fi
    done

# Check Terraform
    if ! command -v terraform >/dev/null 2>&1; then
        missing_tools+=("terraform")
    fi

# Check AWS CLI
    if ! command -v aws >/dev/null 2>&1; then
        missing_tools+=("aws-cli")
    fi

# Report missing tools
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools/packages:"
        for tool in "${missing_tools[@]}"; do
            log_error "  - ${tool}"
        done

        log_info "=== Installation Commands ==="
        log_info "Python packages: pip install boto3 requests pytest pytest-html pytest-cov pytest-xdist pytest-timeout pytest-json-report"
        log_info "Terraform: https://developer.hashicorp.com/terraform/downloads"
        log_info "AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        log_info "============================="
        return 1
    fi

# Check AWS credentials
    if ! check_aws_credentials; then
        log_error "AWS credentials are required for infrastructure tests"
        return 1
    fi

    log_success "All test prerequisites satisfied"
    return 0
}

# Prepare test environment
prepare_test_environment() {
    log_subsection "Preparing Test Environment"

    # Create report directory
    mkdir -p "${REPORT_DIR}"

    # Set environment variables for pytest
    export ENVIRONMENT
    export AWS_DEFAULT_REGION
    export RESOURCE_PREFIX
    export PROJECT_NAME
    export TERRAFORM_WORKSPACE

    # Set test configuration
    export TEST_TIMEOUT
    export TEST_VERBOSE
    export TEST_COVERAGE
    export FAIL_FAST

    # Change to terraform directory
    cd "${TERRAFORM_DIR}"

    # Verify Terraform is initialized
    if [[ ! -d ".terraform" ]]; then
        log_info "Initializing Terraform..."
        if ! terraform init -input=false; then
            log_error "Failed to initialize Terraform"
            return 1
        fi
    fi

    # Select/create workspace
    local workspace="${TERRAFORM_WORKSPACE}"
    log_info "Ensuring Terraform workspace: ${workspace}"

    if ! terraform workspace select "${workspace}" 2>/dev/null; then
        log_info "Creating new workspace: ${workspace}"
        if ! terraform workspace new "${workspace}"; then
            log_error "Failed to create workspace: ${workspace}"
            return 1
        fi
    fi

    # Validate Terraform configuration
    log_info "Validating Terraform configuration..."
    if ! terraform validate; then
        log_error "Terraform configuration validation failed"
        return 1
    fi

    log_success "Test environment prepared"
    return 0
}

# Build pytest command
build_pytest_command() {
    local test_type="${1}"
    local pytest_cmd="python3 -m pytest"

    # Add basic options
    pytest_cmd+=" --tb=short"
    pytest_cmd+=" --strict-markers"
    pytest_cmd+=" --strict-config"

    # Add timeout (only if pytest-timeout is available)
    if python3 -c "import pytest_timeout" 2>/dev/null; then
        pytest_cmd+=" --timeout=${TEST_TIMEOUT}"
    else
        log_warn "pytest-timeout not available, timeout functionality will not work"
    fi

    # Add verbosity
    if [[ "${TEST_VERBOSE}" == "true" ]]; then
        pytest_cmd+=" -v"
    else
        pytest_cmd+=" -q"
    fi

    # Add debug output
    if [[ "${DEBUG_MODE:-false}" == "true" ]]; then
        pytest_cmd+=" -s --log-cli-level=DEBUG"
    fi

    # Add fail fast
    if [[ "${FAIL_FAST}" == "true" ]]; then
        pytest_cmd+=" -x"
    fi

    # Add parallel execution
    if [[ "${TEST_PARALLEL}" == "true" ]]; then
        if python3 -c "import xdist" 2>/dev/null; then
            pytest_cmd+=" -n auto"
        else
            log_warn "pytest-xdist not available, running tests sequentially"
        fi
    fi

    # Add coverage
    if [[ "${TEST_COVERAGE}" == "true" ]]; then
        if python3 -c "import pytest_cov" 2>/dev/null; then
            pytest_cmd+=" --cov=infrastructure-tests --cov-report=html:${REPORT_DIR}/coverage-${REPORT_PREFIX}.html"
            pytest_cmd+=" --cov-report=term-missing"
        else
            log_warn "pytest-cov not available, skipping coverage report"
        fi
    fi

    # Add test selection based on type
    case "${test_type}" in
        "terraform")
            pytest_cmd+=" -m terraform"
            ;;
        "aws")
            pytest_cmd+=" -m aws"
            ;;
        "connectivity")
            pytest_cmd+=" -m integration"
            ;;
        "security")
            pytest_cmd+=" -m 'aws and not slow'"
            ;;
        "performance")
            pytest_cmd+=" -m 'slow or performance'"
            ;;
        "all")
            # Run all tests
            ;;
        *)
            log_error "Unknown test type: ${test_type}"
            return 1
            ;;
    esac

    # Add report generation
    case "${REPORT_FORMAT}" in
        "html"|"all")
            if python3 -c "import pytest_html" 2>/dev/null; then
                pytest_cmd+=" --html=${REPORT_DIR}/infrastructure-test-report-${REPORT_PREFIX}.html --self-contained-html"
            fi
            ;;
    esac

    case "${REPORT_FORMAT}" in
        "xml"|"all")
            pytest_cmd+=" --junit-xml=${REPORT_DIR}/junit-results-${REPORT_PREFIX}.xml"
            ;;
    esac

    case "${REPORT_FORMAT}" in
        "json"|"all")
            if python3 -c "import pytest_json_report" 2>/dev/null; then
                pytest_cmd+=" --json-report --json-report-file=${REPORT_DIR}/test-results-${REPORT_PREFIX}.json"
            fi
            ;;
    esac

    # Add test directory
    pytest_cmd+=" infrastructure-tests/"

    # Add custom pytest arguments
    if [[ -n "${PYTEST_ARGS}" ]]; then
        pytest_cmd+=" ${PYTEST_ARGS}"
    fi

    echo "${pytest_cmd}"
}

# Show dry run information
show_dry_run() {
    log_section "Dry Run - Test Execution Plan"

    log_info "Environment: ${ENVIRONMENT}"
    log_info "Test Types: ${TEST_TYPES}"
    log_info "Parallel Execution: ${TEST_PARALLEL}"
    log_info "Verbose Output: ${TEST_VERBOSE}"
    log_info "Coverage Report: ${TEST_COVERAGE}"
    log_info "Fail Fast: ${FAIL_FAST}"
    log_info "Test Timeout: ${TEST_TIMEOUT} seconds"
    log_info "Report Format: ${REPORT_FORMAT}"
    log_info "Report Directory: ${REPORT_DIR}"

    log_subsection "Tests to Execute"

    if [[ "${TEST_TYPES}" == "all" ]]; then
        for test_type in terraform aws connectivity security; do
            local pytest_cmd
            pytest_cmd=$(build_pytest_command "${test_type}")
            log_info "Test Type: ${test_type}"
            log_info "  Command: ${pytest_cmd}"
            echo
        done
    else
        IFS=',' read -ra TEST_TYPE_ARRAY <<< "${TEST_TYPES}"
        for test_type in "${TEST_TYPE_ARRAY[@]}"; do
            test_type=$(echo "${test_type}" | xargs)  # Trim whitespace
            local pytest_cmd
            pytest_cmd=$(build_pytest_command "${test_type}")
            log_info "Test Type: ${test_type}"
            log_info "  Command: ${pytest_cmd}"
            echo
        done
    fi

    log_subsection "Available Test Files"
    if [[ -d "infrastructure-tests" ]]; then
        find infrastructure-tests -name "test_*.py" -type f | sort | while read -r test_file; do
            log_info "  ${test_file}"
        done
    else
        log_warn "Infrastructure tests directory not found"
    fi

    log_info "Use --dry-run=false or remove --dry-run to execute tests"
}

# Run specific test type
run_test_type() {
    local test_type="${1}"

    log_subsection "Running ${test_type} Tests"

    local pytest_cmd
    pytest_cmd=$(build_pytest_command "${test_type}")

    log_info "Executing: ${pytest_cmd}"

    # Create test-specific log file
    local test_log="${REPORT_DIR}/test-${test_type}-${REPORT_PREFIX}.log"

    # Run tests with proper error handling
    local start_time
    start_time=$(date +%s)

    # Execute pytest and capture output
    if [[ "${TEST_VERBOSE}" == "true" ]]; then
        # Show output in real-time for verbose mode
        if eval "${pytest_cmd}" 2>&1 | tee "${test_log}"; then
            local exit_code=0
        else
            local exit_code=1
        fi
    else
        # Capture output to log file for quiet mode
        if eval "${pytest_cmd}" > "${test_log}" 2>&1; then
            local exit_code=0
        else
            local exit_code=1
        fi
    fi

    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))

    if [[ ${exit_code} -eq 0 ]]; then
        log_success "${test_type} tests passed (${duration}s)"
        return 0
    else
        log_error "${test_type} tests failed (${duration}s)"

        # Show error summary if not in verbose mode
        if [[ "${TEST_VERBOSE}" != "true" ]]; then
            log_info "Error summary (see ${test_log} for details):"
            tail -20 "${test_log}" | grep -E "(FAILED|ERROR|AssertionError)" || true
        fi

        return 1
    fi
}

# Generate test summary report
generate_test_summary() {
    local overall_exit_code="${1}"
    local start_time="${2}"
    local end_time="${3}"

    log_section "Test Execution Summary"

    local total_duration=$((end_time - start_time))

    # Parse test results from log files
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    local skipped_tests=0

    if [[ -d "${REPORT_DIR}" ]]; then
        for log_file in "${REPORT_DIR}"/test-*-"${REPORT_PREFIX}".log; do
            if [[ -f "${log_file}" ]]; then
                # Extract test counts from pytest output
                if grep -q "test session starts" "${log_file}"; then
                    local test_line
                    test_line=$(grep -E "=[[:space:]]*[0-9]+" "${log_file}" | tail -1 || echo "")

                    if [[ -n "${test_line}" ]]; then
                        local current_passed current_failed current_skipped
                        current_passed=$(echo "${test_line}" | grep -o "[0-9]* passed" | grep -o "[0-9]*" || echo "0")
                        current_failed=$(echo "${test_line}" | grep -o "[0-9]* failed" | grep -o "[0-9]*" || echo "0")
                        current_skipped=$(echo "${test_line}" | grep -o "[0-9]* skipped" | grep -o "[0-9]*" || echo "0")

                        passed_tests=$((passed_tests + current_passed))
                        failed_tests=$((failed_tests + current_failed))
                        skipped_tests=$((skipped_tests + current_skipped))
                    fi
                fi
            fi
        done
    fi

    total_tests=$((passed_tests + failed_tests + skipped_tests))

    # Display summary
    log_info "=== Test Results ==="
    log_info "Environment: ${ENVIRONMENT}"
    log_info "Total Tests: ${total_tests}"
    log_info "Passed: ${passed_tests}"
    log_info "Failed: ${failed_tests}"
    log_info "Skipped: ${skipped_tests}"
    log_info "Execution Time: ${total_duration} seconds"
    log_info "==================="

    # Display report files
    log_info "=== Generated Reports ==="
    if [[ -d "${REPORT_DIR}" ]]; then
        find "${REPORT_DIR}" -name "*${REPORT_PREFIX}*" -type f | sort | while read -r report_file; do
            local file_size
            file_size=$(du -h "${report_file}" | cut -f1)
            log_info "  ${report_file} (${file_size})"
        done
    fi
    log_info "========================="

    # Final status
    if [[ ${overall_exit_code} -eq 0 ]]; then
        log_success "All infrastructure tests passed successfully"
        log_info "Environment '${ENVIRONMENT}' infrastructure validated"

        if [[ "${failed_tests}" -gt 0 ]]; then
            log_warn "Note: Some individual tests failed but overall result is success"
        fi
    else
        log_failure "Infrastructure tests failed"
        log_error "Please review test output and fix issues"

        # Provide debugging hints
        log_info "=== Debugging Tips ==="
        log_info "1. Check individual test logs in ${REPORT_DIR}/"
        log_info "2. Run with --verbose for detailed output"
        log_info "3. Run specific test types to isolate issues:"
        log_info "   ${0} --test-type terraform"
        log_info "   ${0} --test-type aws"
        log_info "   ${0} --test-type connectivity"
        log_info "4. Use --fail-fast to stop on first failure"
        log_info "5. Check AWS console for resource status"
        log_info "6. Verify Terraform state matches actual resources"
        log_info "========================"
    fi
}

# Cleanup function
cleanup_test_environment() {
    log_debug "Cleaning up test environment..."

    # Remove temporary files
    find "${TERRAFORM_DIR}" -name "tfplan*" -type f -delete 2>/dev/null || true
    find "${TERRAFORM_DIR}" -name "*.tmp" -type f -delete 2>/dev/null || true

    # Compress old log files
    if [[ -d "${REPORT_DIR}" ]]; then
        find "${REPORT_DIR}" -name "*.log" -mtime +7 -type f -exec gzip {} \; 2>/dev/null || true
    fi
}

# Register cleanup function
register_cleanup_function cleanup_test_environment

# Main execution function
main() {
    local exit_code=0
    local start_time
    start_time=$(date +%s)

    # Initialize logging
    init_logging

    # Setup error handling
    setup_error_handling

    log_section "Infrastructure Testing - ${SCRIPT_NAME} v${VERSION}"

    # Load and validate environment configuration
    if ! load_environment_config "${ENVIRONMENT:-}"; then
        log_error "Failed to load environment configuration"
        exit 1
    fi

    # Print environment summary
    print_environment_summary

    # Show dry run if requested
    if [[ "${DRY_RUN}" == "true" ]]; then
        show_dry_run
        exit 0
    fi

    # Check prerequisites
    if ! check_test_prerequisites; then
        log_error "Prerequisites check failed"
        exit 1
    fi

    # Prepare test environment
    if ! prepare_test_environment; then
        log_error "Failed to prepare test environment"
        exit 1
    fi

    # Run tests based on type
    if [[ "${TEST_TYPES}" == "all" ]]; then
        log_info "Running all test types..."

        for test_type in terraform aws connectivity security; do
            if ! run_test_type "${test_type}"; then
                exit_code=1
                log_error "Test type '${test_type}' failed"

                # Stop immediately if fail-fast is enabled
                if [[ "${FAIL_FAST}" == "true" ]]; then
                    log_error "Stopping due to --fail-fast option"
                    break
                fi
            fi
        done
    else
        # Run specific test types
        IFS=',' read -ra TEST_TYPE_ARRAY <<< "${TEST_TYPES}"
        for test_type in "${TEST_TYPE_ARRAY[@]}"; do
            test_type=$(echo "${test_type}" | xargs)  # Trim whitespace

            if ! run_test_type "${test_type}"; then
                exit_code=1
                log_error "Test type '${test_type}' failed"

                if [[ "${FAIL_FAST}" == "true" ]]; then
                    log_error "Stopping due to --fail-fast option"
                    break
                fi
            fi
        done
    fi

    # Calculate total execution time
    local end_time
    end_time=$(date +%s)

    # Generate final summary
    generate_test_summary "${exit_code}" "${start_time}" "${end_time}"

    exit ${exit_code}
}

# Set default values
DEBUG_MODE="${DEBUG_MODE:-false}"
TEST_VERBOSE="${TEST_VERBOSE:-false}"
TEST_PARALLEL="${TEST_PARALLEL:-false}"
TEST_COVERAGE="${TEST_COVERAGE:-false}"
FAIL_FAST="${FAIL_FAST:-false}"
DRY_RUN="${DRY_RUN:-false}"

# Parse command line arguments
parse_arguments "$@"

# Export environment variables for subprocess access
export DEBUG_MODE TEST_VERBOSE TEST_PARALLEL TEST_TIMEOUT TEST_COVERAGE FAIL_FAST DRY_RUN REPORT_FORMAT

# Run main function
main