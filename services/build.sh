#!/bin/bash

# Universal Build Script for Python Microservices
# Usage: ./build.sh [OPTIONS] [SERVICE_NAME]

set -e  # Exit on any error

# Default configuration
DEFAULT_PYTHON_VERSION="3.11"
DEFAULT_TEST_COVERAGE_THRESHOLD=60

# Function to show usage
show_usage() {
    cat << EOF
Services Build Script

Usage: $0 [OPTIONS] [SERVICE_NAME]

OPTIONS:
    -h, --help              Show this help message
    -b, --build-only        Build only, skip tests
    -t, --test-only         Run tests only, skip building
    -v, --verbose           Enable verbose output

SERVICE_NAME:
    Optional. If provided, build only the specified service.
    If not provided, build all services.

    Available services: common, user_service, inventory_service, order_service, exception

Examples:
    $0                      # Build and test all services (default)
    $0 common               # Build and test only common package
    $0 user_service         # Build and test only user_service
    $0 --build-only         # Build only all services
    $0 --test-only common   # Run tests only for common package
    $0 -v user_service      # Verbose output for user_service

EOF
}

# Function to detect service/package name from current directory
detect_service_name() {
    local current_dir=$(basename "$PWD")

    # Check if we're in a specific service directory
    if [[ "$current_dir" == "common" || "$current_dir" == "user_service" || "$current_dir" == "inventory_service" || "$current_dir" == "order_service" || "$current_dir" == "exception" ]] && [[ -d "tests" || -f "setup.py" ]]; then
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

# Function to validate service name
validate_service_name() {
    local service_name=$1

    # List of valid services
    local valid_services=("common" "user_service" "inventory_service" "order_service" "exception")

    for valid_service in "${valid_services[@]}"; do
        if [[ "$service_name" == "$valid_service" ]]; then
            return 0
        fi
    done

    echo "Invalid service name: $service_name"
    echo "Valid services: ${valid_services[*]}"
    return 1
}

# Function to get list of available services
get_available_services() {
    local services=()
    for dir in */; do
        if [[ -d "$dir" && "$dir" != "*/" ]]; then
            services+=("${dir%/}")
        fi
    done
    echo "${services[*]}"
}

# Function to check if Python version is available
check_python_version() {
    # Always use python3.11
    if command -v python3.11 &> /dev/null; then
        echo "python3.11"
    else
        echo "python3.11 not found. Please install Python 3.11."
        exit 1
    fi
}

# Function to create virtual environment
setup_virtual_env() {
    local python_cmd=$1
    local service_name=$2

    local venv_dir=".venv-${service_name}"

    if [[ ! -d "$venv_dir" ]]; then
        echo "Creating virtual environment: $venv_dir"
        "$python_cmd" -m venv "$venv_dir"
    fi

    # Upgrade pip using the virtual environment's pip
    echo "Upgrading pip and tools"
    "$venv_dir/bin/pip" install --upgrade pip setuptools wheel

    echo "Virtual environment ready: $venv_dir"
}

# Function to set up CI/CD environment variables
setup_ci_environment() {
    local service_name=$1

    echo "Setting up CI/CD environment variables for $service_name"

    # All environment variable setup has been removed.

    echo "Environment variables set:"
    echo "  AWS_REGION: $AWS_REGION"
    echo "  USERS_TABLE: $USERS_TABLE"
    echo "  ORDERS_TABLE: $ORDERS_TABLE"
    echo "  INVENTORY_TABLE: $INVENTORY_TABLE"
    echo "  ASSETS_TABLE: $ASSETS_TABLE"
    echo "  ENVIRONMENT: $ENVIRONMENT"
    echo "  JWT_SECRET: [HIDDEN]"
    echo "  PORT: $PORT"
    echo "  HOST: $HOST"
    echo "  SERVICE_ENVIRONMENT: $SERVICE_ENVIRONMENT"
    echo "  LOG_LEVEL: $LOG_LEVEL"
    echo "  PYTHONUNBUFFERED: $PYTHONUNBUFFERED"
    echo "  TESTING: $TESTING"
    echo "  CI: $CI"

    echo "CI/CD environment setup complete"
}

# Function to install dependencies
install_dependencies() {
    local service_name=$1
    local venv_dir=".venv-${service_name}"
    local pip_cmd="${venv_dir}/bin/pip"

    echo "Installing dependencies for $service_name"

    # Install common package dependencies first if we're not building common itself
    if [[ "$service_name" != "common" ]]; then
        # Check for common package
        if [[ -f "../common/requirements.txt" ]]; then
            echo "Installing common package dependencies"
            "$pip_cmd" install -r ../common/requirements.txt
        fi

        # Install common package in development mode
        if [[ -f "../common/setup.py" ]]; then
            echo "Installing common package in development mode"
            "$pip_cmd" install -e ../common
        fi
    fi

    # Install service-specific dependencies
    if [[ -f "requirements.txt" ]]; then
        echo "Installing service requirements"
        "$pip_cmd" install --upgrade -r requirements.txt
    else
        echo "No requirements.txt found for $service_name"
    fi

    # Install test dependencies
    local test_requirements=""
    if [[ -f "test-requirements.txt" ]]; then
        test_requirements="test-requirements.txt"
    elif [[ -f "tests/requirements.txt" ]]; then
        test_requirements="tests/requirements.txt"
    fi

    if [[ -n "$test_requirements" && -f "$test_requirements" ]]; then
        echo "Installing test dependencies from $test_requirements"
        "$pip_cmd" install --upgrade -r "$test_requirements"
    else
        echo "Installing basic test dependencies"
        "$pip_cmd" install pytest pytest-asyncio pytest-mock pytest-cov
    fi

    # Install package in development mode if setup.py exists
    if [[ -f "setup.py" ]]; then
        echo "Installing package in development mode"
        "$pip_cmd" install -e .
    fi

    echo "Dependencies installed successfully"
}

# Function to clean build artifacts
clean_build() {
    echo "Cleaning build artifacts"

    # Remove common build directories
    rm -rf build dist "*.egg-info" .pytest_cache

    # Remove Python cache files recursively
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true

    echo "Build artifacts cleaned"
}

# Function to run tests
run_tests() {
    local coverage_threshold=$1
    local no_coverage=$2
    local verbose=$3
    local service_name=$4
    local venv_dir=".venv-${service_name}"

    echo "Running tests for service: $service_name"
    echo "Current directory: $(pwd)"

    # Check for test directories
    local test_dirs=()
    if [[ -d "tests" ]]; then
        test_dirs+=("tests")
        echo "Found tests directory"
    fi

    if [[ -d "test" ]]; then
        test_dirs+=("test")
        echo "Found test directory"
    fi

    if [[ ${#test_dirs[@]} -eq 0 ]]; then
        echo "No test directories found for $service_name"
        return 0
    fi

    echo "Test directories: ${test_dirs[*]}"

    # Set up Python path for imports
    # Only include current service's src in PYTHONPATH for test discovery
    # Common package should be available as installed dependency, not in PYTHONPATH
    local python_paths="${PWD}/src"
    export PYTHONPATH="${python_paths}:${PYTHONPATH:-}"
    echo "Set PYTHONPATH: $PYTHONPATH"

    # Build pytest command
    local pytest_cmd="${venv_dir}/bin/pytest"

    if [[ "$verbose" == "true" ]]; then
        pytest_cmd="$pytest_cmd -v"
    fi

    # Add test directories
    for test_dir in "${test_dirs[@]}"; do
        pytest_cmd="$pytest_cmd $test_dir"
    done

    # Add coverage options (respect service's pytest.ini)
    if [[ "$no_coverage" != "true" ]]; then
        # Create service-specific coverage directory
        local coverage_dir=htmlcov-${service_name}

        # Only add coverage options if service doesn't have pytest.ini with coverage
        if [[ ! -f "pytest.ini" ]] || ! grep -q "addopts.*--cov" pytest.ini; then
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

            # Add basic coverage reporting
            pytest_cmd="$pytest_cmd --cov-report=term-missing"
        fi

        # Always add HTML report with service-specific directory
        pytest_cmd="$pytest_cmd --cov-report=html:$coverage_dir"

        # Only add coverage threshold if explicitly provided (don't override service's pytest.ini)
        if [[ -n "$coverage_threshold" && "$coverage_threshold" != "$DEFAULT_TEST_COVERAGE_THRESHOLD" ]]; then
            pytest_cmd="$pytest_cmd --cov-fail-under=$coverage_threshold"
        fi
    fi

    echo "Running command: $pytest_cmd"

    # Run tests
    if $pytest_cmd; then
        echo "All tests passed"
    else
        echo "Tests failed"
        return 1
    fi
}

# Function to build package
build_package() {
    local service_name=$1
    local venv_dir=".venv-${service_name}"

    if [[ ! -f "setup.py" ]]; then
        echo "No setup.py found, skipping package build"
        return 0
    fi

    echo "Building package: $service_name"

    # Build using virtual environment's python
    "${venv_dir}/bin/python" setup.py sdist bdist_wheel

    echo "Package built successfully"
    if [[ -d "dist" ]]; then
        echo "Build artifacts:"
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
        echo "Service directory not found: $service_name"
        echo "Current directory: $PWD"
        echo "Available services:"
        for dir in */; do
            if [[ -d "$dir" && "$dir" != "*/" ]]; then
                echo "  - ${dir%/}"
            fi
        done
        exit 1
    fi
}

# Function to generate coverage summary
generate_coverage_summary() {
    echo "========================================"
    echo "COVERAGE SUMMARY"
    echo "========================================"

    for coverage_dir in htmlcov-*; do
        if [[ -d "$coverage_dir" ]]; then
            local service_name=${coverage_dir#htmlcov-}
            echo "Service: $service_name"
            echo "Coverage report: $coverage_dir/index.html"
        fi
    done

    echo "========================================"
}

# Main function
main() {
    local test_only=false
    local build_only=false
    local verbose=false
    local service_name=""

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
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
            -*)
                echo "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                # This case handles the SERVICE_NAME argument
                if [[ -z "$service_name" ]]; then
                    service_name=$1
                else
                    echo "Unknown argument: $1"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done

    # Set verbose mode
    if [[ "$verbose" == "true" ]]; then
        set -x
    fi

    # Change to services directory
    cd "$(dirname "$0")"
    echo "Working directory: $(pwd)"

    # Get list of available services
    local services=()
    if [[ -z "$service_name" ]]; then
        services=($(get_available_services))
    else
        if ! validate_service_name "$service_name"; then
            exit 1
        fi
        services+=("$service_name")
    fi

    if [[ ${#services[@]} -eq 0 ]]; then
        echo "No services found in current directory"
        exit 1
    fi

    echo "Found services: ${services[*]}"

    # Check Python version
    local python_cmd=$(check_python_version)
    echo "Using Python: $python_cmd"

    # Main execution logic
    local service_list_text
    if [[ ${#services[@]} -eq 1 ]]; then
        service_list_text="service: ${services[0]}"
    else
        service_list_text="services: ${services[*]}"
    fi

    if [[ "$test_only" == "true" ]]; then
        # For test-only, assume code is already built, just run tests
        echo "Running tests only for $service_list_text"
        for service in "${services[@]}"; do
            echo "Testing service: $service"
            cd "$service"
            setup_virtual_env "$python_cmd" "$service"
            install_dependencies "$service"
            run_tests "" "false" "$verbose" "$service"
            cd ..
        done
        exit 0
    fi

    if [[ "$build_only" == "true" ]]; then
        # For build-only, install deps and build
        echo "Building only for $service_list_text"
        for service in "${services[@]}"; do
            echo "Building service: $service"
            cd "$service"
            setup_virtual_env "$python_cmd" "$service"
            install_dependencies "$service"
            build_package "$service"
            cd ..
        done
        exit 0
    fi

    # Default: build and test services
    echo "Building and testing $service_list_text"
    local failed_services=()
    for service in "${services[@]}"; do
        echo ""
        echo "========================================"
        echo "Building service: $service"
        echo "========================================"

        cd "$service"
        setup_virtual_env "$python_cmd" "$service"
        install_dependencies "$service"

        if run_tests "" "false" "$verbose" "$service"; then
            build_package "$service"
            echo "✅ $service completed successfully"
        else
            echo "❌ $service failed"
            failed_services+=("$service")
        fi

        cd ..
    done

    # Report results
    echo ""
    echo "========================================"
    echo "BUILD SUMMARY"
    echo "========================================"

    if [[ ${#failed_services[@]} -eq 0 ]]; then
        if [[ ${#services[@]} -eq 1 ]]; then
            echo "✅ Service built successfully: ${services[0]}"
        else
            echo "✅ All services built successfully: ${services[*]}"
        fi
        echo "Build and test completed successfully!"
        exit 0
    else
        echo "❌ Failed services: ${failed_services[*]}"
        if [[ ${#services[@]} -gt 1 ]]; then
            echo "✅ Successful services: $(printf '%s\n' "${services[@]}" | grep -v "$(printf '%s\n' "${failed_services[@]}")" | tr '\n' ' ')"
        fi
        exit 1
    fi
}

# Run main function with all arguments
main "$@"