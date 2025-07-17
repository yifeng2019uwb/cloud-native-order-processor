#!/bin/bash

# Universal Build Script for Python Microservices
# Usage: ./build.sh [OPTIONS] [SERVICE_NAME]

set -e  # Exit on any error

# Default configuration
DEFAULT_PYTHON_VERSION="3.11"
DEFAULT_TEST_COVERAGE_THRESHOLD=60

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Universal Build Script for Python Microservices

Usage: $0 [OPTIONS] [SERVICE_NAME]

OPTIONS:
    -h, --help              Show this help message
    -c, --clean             Clean build artifacts before building
    -t, --test-only         Run tests only, skip building
    -b, --build-only        Build only, skip tests
    -v, --verbose           Enable verbose output
    -p, --python VERSION    Specify Python version (default: ${DEFAULT_PYTHON_VERSION})
    --coverage THRESHOLD    Set test coverage threshold (default: ${DEFAULT_TEST_COVERAGE_THRESHOLD})
    --no-coverage           Skip coverage reporting
    --install-deps          Install dependencies only

SERVICE_NAME:
    Name of the service to build (e.g., order-service, common)
    If not specified, will attempt to detect from current directory

Examples:
    $0                                  # Build current service/package
    $0 order-service                    # Build order-service
    $0 common                           # Build common package
    $0 --clean --verbose order-service  # Clean build with verbose output
    $0 --test-only                      # Run tests only

EOF
}

# Function to detect service/package name from current directory
detect_service_name() {
    local current_dir=$(basename "$PWD")

    # Check if we're in a specific service directory
    if [[ "$current_dir" == "common" || "$current_dir" == "order-service" ]] && [[ -d "tests" || -f "setup.py" ]]; then
        echo "$current_dir"
        return 0
    fi

    # Check if we're in the services root directory - allow building all services
    if [[ "$current_dir" == "services" ]]; then
        echo "ALL_SERVICES"
        return 0
    fi

    # For other directories, assume it's a service name
    echo "$current_dir"
}

# Function to check if Python version is available
check_python_version() {
    # Always use python3.11
    if command -v python3.11 &> /dev/null; then
        echo "python3.11"
    else
        print_error "python3.11 not found. Please install Python 3.11."
        exit 1
    fi
}

# Function to create virtual environment
setup_virtual_env() {
    local python_cmd=$1
    local service_name=$2

    local venv_dir=".venv-${service_name}"

    if [[ ! -d "$venv_dir" ]]; then
        print_status "Creating virtual environment: $venv_dir"
        "$python_cmd" -m venv "$venv_dir"
    fi

    # Upgrade pip using the virtual environment's pip
    print_status "Upgrading pip and tools"
    "$venv_dir/bin/pip" install --upgrade pip setuptools wheel

    print_success "Virtual environment ready: $venv_dir"
}

# Function to set up CI/CD environment variables
setup_ci_environment() {
    local service_name=$1

    print_status "Setting up CI/CD environment variables for $service_name"

    # Set AWS environment variables (required for tests)
    export AWS_REGION="${AWS_REGION:-us-west-2}"
    export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-west-2}"

    # Set DynamoDB table names (required for database tests)
    export USERS_TABLE="${USERS_TABLE:-test-users-table}"
    export ORDERS_TABLE="${ORDERS_TABLE:-test-orders-table}"
    export INVENTORY_TABLE="${INVENTORY_TABLE:-test-inventory-table}"
    export ASSETS_TABLE="${ASSETS_TABLE:-test-assets-table}"

    # Set service-specific environment variables
    export SERVICE_ENVIRONMENT="${SERVICE_ENVIRONMENT:-test}"
    export LOG_LEVEL="${LOG_LEVEL:-INFO}"
    export ENVIRONMENT="${ENVIRONMENT:-test}"
    export JWT_SECRET="${JWT_SECRET:-test-jwt-secret-key-for-testing-only}"
    export PORT="${PORT:-8000}"
    export HOST="${HOST:-0.0.0.0}"

    # Set Python environment variables
    export PYTHONPATH="${PYTHONPATH:-}"
    export PYTHONUNBUFFERED="1"

    # Set test-specific variables
    export TESTING="true"
    export CI="true"

    # Clear Lambda environment (tests expect this to be unset by default)
    unset AWS_LAMBDA_FUNCTION_NAME

    print_status "Environment variables set:"
    print_status "  AWS_REGION: $AWS_REGION"
    print_status "  USERS_TABLE: $USERS_TABLE"
    print_status "  ORDERS_TABLE: $ORDERS_TABLE"
    print_status "  INVENTORY_TABLE: $INVENTORY_TABLE"
    print_status "  ASSETS_TABLE: $ASSETS_TABLE"
    print_status "  ENVIRONMENT: $ENVIRONMENT"
    print_status "  JWT_SECRET: [HIDDEN]"
    print_status "  PORT: $PORT"
    print_status "  HOST: $HOST"
    print_status "  SERVICE_ENVIRONMENT: $SERVICE_ENVIRONMENT"
    print_status "  LOG_LEVEL: $LOG_LEVEL"
    print_status "  PYTHONUNBUFFERED: $PYTHONUNBUFFERED"
    print_status "  TESTING: $TESTING"
    print_status "  CI: $CI"

    print_success "CI/CD environment setup complete"
}

# Function to install dependencies
install_dependencies() {
    local service_name=$1
    local venv_dir=".venv-${service_name}"
    local pip_cmd="${venv_dir}/bin/pip"

    print_status "Installing dependencies for $service_name"

    # Install common package dependencies first if we're not building common itself
    if [[ "$service_name" != "common" ]]; then
        # Check for common package
        if [[ -f "../common/requirements.txt" ]]; then
            print_status "Installing common package dependencies"
            "$pip_cmd" install -r ../common/requirements.txt
        fi

        # Install common package in development mode
        if [[ -f "../common/setup.py" ]]; then
            print_status "Installing common package in development mode"
            "$pip_cmd" install -e ../common
        fi
    fi

    # Install service-specific dependencies
    if [[ -f "requirements.txt" ]]; then
        print_status "Installing service requirements"
        "$pip_cmd" install --upgrade -r requirements.txt
    else
        print_status "No requirements.txt found for $service_name"
    fi

    # Install test dependencies
    local test_requirements=""
    if [[ -f "test-requirements.txt" ]]; then
        test_requirements="test-requirements.txt"
    elif [[ -f "tests/requirements.txt" ]]; then
        test_requirements="tests/requirements.txt"
    fi

    if [[ -n "$test_requirements" && -f "$test_requirements" ]]; then
        print_status "Installing test dependencies from $test_requirements"
        "$pip_cmd" install --upgrade -r "$test_requirements"
    else
        print_status "Installing basic test dependencies"
        "$pip_cmd" install pytest pytest-asyncio pytest-mock pytest-cov
    fi

    # Install package in development mode if setup.py exists
    if [[ -f "setup.py" ]]; then
        print_status "Installing package in development mode"
        "$pip_cmd" install -e .
    fi

    print_success "Dependencies installed successfully"
}

# Function to clean build artifacts
clean_build() {
    print_status "Cleaning build artifacts"

    # Remove common build directories
    rm -rf build dist "*.egg-info" .pytest_cache .coverage __pycache__

    # Remove Python cache files recursively
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true

    print_success "Build artifacts cleaned"
}

# Function to run tests
run_tests() {
    local coverage_threshold=$1
    local no_coverage=$2
    local verbose=$3
    local service_name=$4
    local venv_dir=".venv-${service_name}"

    print_status "Running tests for service: $service_name"
    print_status "Current directory: $(pwd)"

    # Check for test directories
    local test_dirs=()
    if [[ -d "tests" ]]; then
        test_dirs+=("tests")
        print_status "Found tests directory"
    fi

    if [[ -d "test" ]]; then
        test_dirs+=("test")
        print_status "Found test directory"
    fi

    # For services (not common), also include common tests if available
    # if [[ "$service_name" != "common" && -d "../common/tests" ]]; then
    #     test_dirs+=("../common/tests")
    #     print_status "Found common tests directory"
    # fi
    # Only run common tests when building the common package itself

    if [[ ${#test_dirs[@]} -eq 0 ]]; then
        print_warning "No test directories found for $service_name"
        return 0
    fi

    print_status "Test directories: ${test_dirs[*]}"

    # Set up Python path for imports
    local python_paths=""
    if [[ -d "src" ]]; then
        python_paths="${PWD}/src"
    fi
    if [[ -d "../common" ]]; then
        python_paths="${python_paths:+${python_paths}:}${PWD}/../common"
    fi
    if [[ -n "$python_paths" ]]; then
        export PYTHONPATH="${python_paths}:${PYTHONPATH:-}"
        print_status "Set PYTHONPATH: $PYTHONPATH"
    fi

    # Build pytest command
    local pytest_cmd="${venv_dir}/bin/pytest"

    if [[ "$verbose" == "true" ]]; then
        pytest_cmd="$pytest_cmd -v"
    fi

    # Add test directories
    for test_dir in "${test_dirs[@]}"; do
        pytest_cmd="$pytest_cmd $test_dir"
    done

    # Add coverage options
    if [[ "$no_coverage" != "true" ]]; then
        # Create service-specific coverage directory
        local coverage_dir=htmlcov-${service_name}
        # Add coverage for source code only (not common)
        if [[ -d "src" ]]; then
            pytest_cmd="$pytest_cmd --cov=src"
        elif [[ -f "setup.py" ]]; then
            pytest_cmd="$pytest_cmd --cov=."
        fi

        # For common package, include common coverage
        if [[ "$service_name" == "common" ]]; then
            pytest_cmd="$pytest_cmd --cov=src"
        fi

        # Use service-specific coverage directory to avoid conflicts
        pytest_cmd="$pytest_cmd --cov-report=html:$coverage_dir --cov-report=term-missing"

        if [[ -n "$coverage_threshold" ]]; then
            pytest_cmd="$pytest_cmd --cov-fail-under=$coverage_threshold"
        fi
    fi

    print_status "Running command: $pytest_cmd"

    # Run tests
    if $pytest_cmd; then
        print_success "All tests passed"
    else
        print_error "Tests failed"
        return 1
    fi
}

# Function to build package
build_package() {
    local service_name=$1
    local venv_dir=".venv-${service_name}"

    if [[ ! -f "setup.py" ]]; then
        print_status "No setup.py found, skipping package build"
        return 0
    fi

    print_status "Building package: $service_name"

    # Build using virtual environment's python
    "${venv_dir}/bin/python" setup.py sdist bdist_wheel

    print_success "Package built successfully"
    if [[ -d "dist" ]]; then
        print_status "Build artifacts:"
        ls -la dist/ 2>/dev/null || true
    fi
}

# Function to get service directory
get_service_directory() {
    local service_name=$1

    # If we're in the services root and looking for a specific service
    if [[ -d "$service_name" ]]; then
        echo "$service_name"
    # If we're already in the service directory
    elif [[ "$(basename "$PWD")" == "$service_name" && ( -d "tests" || -f "setup.py" ) ]]; then
        echo "."
    else
        print_error "Service directory not found: $service_name"
        print_error "Current directory: $PWD"
        print_error "Available services:"
        for dir in */; do
            if [[ -d "$dir" && "$dir" != "*/" ]]; then
                echo "  - ${dir%/}"
            fi
        done
        exit 1
    fi
}

# Function to clean up old coverage directories
cleanup_coverage_dirs() {
    print_status "Cleaning up old coverage directories"
    find . -name htmlcov*-type d -exec rm -rf {} + 2>/dev/null || true
    find . -name .coverage* -type f -delete 2>/dev/null || true
}

# Function to generate coverage summary
generate_coverage_summary() {
    print_status "========================================"
    print_status "COVERAGE SUMMARY"
    print_status "========================================"

    for coverage_dir in htmlcov-*; do
        if [[ -d "$coverage_dir" ]]; then
            local service_name=${coverage_dir#htmlcov-}
            print_status "Service: $service_name"
            print_status "Coverage report: $coverage_dir/index.html"
        fi
    done

    print_status "========================================"
}

# Main function
main() {
    local service_name=""
    local clean=false
    local test_only=false
    local build_only=false
    local verbose=false
    local python_version="$DEFAULT_PYTHON_VERSION"
    local coverage_threshold="$DEFAULT_TEST_COVERAGE_THRESHOLD"
    local no_coverage=false
    local install_deps_only=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -c|--clean)
                clean=true
                shift
                ;;
            -t|--test-only)
                test_only=true
                shift
                ;;
            -b|--build-only)
                build_only=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -p|--python)
                python_version="$2"
                shift 2
                ;;
            --coverage)
                coverage_threshold="$2"
                shift 2
                ;;
            --no-coverage)
                no_coverage=true
                shift
                ;;
            --install-deps)
                install_deps_only=true
                shift
                ;;
            -*)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                service_name="$1"
                shift
                ;;
        esac
    done

    # Detect service name if not provided
    if [[ -z "$service_name" ]]; then
        service_name=$(detect_service_name)
        if [[ "$service_name" == "ALL_SERVICES" ]]; then
            print_status "No service specified - building all services"

            # Get list of available services
            local services=()
            for dir in */; do
                if [[ -d "$dir" && "$dir" != "*/" ]]; then
                    services+=("${dir%/}")
                fi
            done

            if [[ ${#services[@]} -eq 0 ]]; then
                print_error "No services found in current directory"
                exit 1
            fi

            print_status "Found services: ${services[*]}"

            # Clean up old coverage directories before building
            cleanup_coverage_dirs

            # Build each service
            local failed_services=()
            for service in "${services[@]}"; do
                print_status ""
                print_status "========================================"
                print_status "Building service: $service"
                print_status "========================================"

                # Run the script recursively for each service
                if ./build.sh "$@" "$service"; then
                    print_success "✅ $service completed successfully"
                else
                    print_error "❌ $service failed"
                    failed_services+=("$service")
                fi
            done

            # Generate coverage summary
            generate_coverage_summary

            # Report results
            print_status ""
            print_status "========================================"
            print_status "BUILD SUMMARY"
            print_status "========================================"

            if [[ ${#failed_services[@]} -eq 0 ]]; then
                print_success "✅ All services built successfully: ${services[*]}"
                exit 0
            else
                print_error "❌ Failed services: ${failed_services[*]}"
                print_success "✅ Successful services: $(printf '%s\n' "${services[@]}" | grep -v "$(printf '%s\n' "${failed_services[@]}")" | tr '\n' ' ')"
                exit 1
            fi
        else
            print_status "Detected service: $service_name"
        fi
    fi

    # Get service directory
    local service_dir=$(get_service_directory "$service_name")
    local original_dir="$PWD"

    # Change to service directory
    if [[ "$service_dir" != "." ]]; then
        print_status "Changing to service directory: $service_dir"
        if cd "$service_dir"; then
            print_status "Now in directory: $(pwd)"
        else
            print_error "Failed to change to directory: $service_dir"
            exit 1
        fi
    else
        print_status "Already in correct directory: $(pwd)"
    fi

    # Check Python version
    local python_cmd=$(check_python_version)
    print_status "Using Python: $python_cmd"

    # Clean if requested
    if [[ "$clean" == "true" ]]; then
        clean_build
    fi

    # Clean up old coverage directories for this service
    cleanup_coverage_dirs

    # Setup virtual environment
    setup_virtual_env "$python_cmd" "$service_name"

    # Install dependencies
    install_dependencies "$service_name"

    # If only installing dependencies, exit here
    if [[ "$install_deps_only" == "true" ]]; then
        print_success "Dependencies installed successfully"
        cd "$original_dir"
        exit 0
    fi

    # Set up CI/CD environment variables before running tests
    setup_ci_environment "$service_name"

    # Run tests (unless build-only is specified)
    if [[ "$build_only" != "true" ]]; then
        if ! run_tests "$coverage_threshold" "$no_coverage" "$verbose" "$service_name"; then
            cd "$original_dir"
            exit 1
        fi
    fi

    # Build package (unless test-only is specified)
    if [[ "$test_only" != "true" ]]; then
        build_package "$service_name"
    fi

    print_success "Build completed successfully for: $service_name"

    # Return to original directory
    cd "$original_dir"
}

# Run main function with all arguments
main "$@"