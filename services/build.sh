#!/bin/bash

# Universal Build Script for Python Microservices
# Usage: ./build.sh [OPTIONS] [SERVICE_NAME]
#
# This script can be used to build and test Python packages in a microservices architecture.
# It supports both individual services and the common shared package.

set -e  # Exit on any error

# Default configuration
DEFAULT_PYTHON_VERSION="3.11"
DEFAULT_TEST_COVERAGE_THRESHOLD=80
BUILD_DIR="build"
DIST_DIR="dist"

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
    --docker                Build Docker image (if Dockerfile exists)
    --all-tests             Run all tests in services/tests directory (when in services root)

SERVICE_NAME:
    Name of the service to build (e.g., order-service, inventory-service, common)
    If not specified, will attempt to detect from current directory
    If in services root directory, use --all-tests to run shared tests

Examples:
    $0                                  # Build current service/package
    $0 order-service                    # Build order-service
    $0 common                           # Build common package
    $0 --clean --verbose order-service  # Clean build with verbose output
    $0 --test-only                      # Run tests only
    $0 --all-tests                      # Run all shared tests (from services root)
    $0 --docker order-service           # Build with Docker image

EOF
}

# Function to detect service/package name from current directory
detect_service_name() {
    local current_dir=$(basename "$PWD")

    # Check if we're in the services root directory
    if [[ "$current_dir" == "services" ]]; then
        print_error "You are in the services root directory. Please either:"
        print_error "  1. Specify a service name (e.g., ./build.sh order-service)"
        print_error "  2. Use --all-tests to run shared tests (e.g., ./build.sh --all-tests)"
        print_error "  3. Navigate to a specific service directory"
        print_error ""
        print_error "Available services:"
        for dir in */; do
            if [[ -d "$dir" && "$dir" != "*/" && "$dir" != "tests/" ]]; then
                echo "  - ${dir%/}"
            fi
        done
        exit 1
    fi

    # Check if we're in a service directory
    if [[ -f "src/app.py" || -f "app.py" ]]; then
        echo "$current_dir"
    elif [[ -f "setup.py" ]]; then
        # Try to extract name from setup.py
        local name=$(grep -E "name=" setup.py | head -1 | sed -E 's/.*name="([^"]+)".*/\1/')
        if [[ -n "$name" ]]; then
            echo "$name"
        else
            echo "$current_dir"
        fi
    elif [[ "$current_dir" == "common" ]]; then
        echo "common"
    else
        echo "$current_dir"
    fi
}

# Function to check if Python version is available
check_python_version() {
    local python_version=$1
    local python_cmd="python${python_version}"

    if ! command -v "$python_cmd" &> /dev/null; then
        python_cmd="python3"
        if ! command -v "$python_cmd" &> /dev/null; then
            python_cmd="python"
            if ! command -v "$python_cmd" &> /dev/null; then
                print_error "Python not found. Please install Python ${python_version} or later."
                exit 1
            fi
        fi
    fi

    echo "$python_cmd"
}

# Function to create virtual environment
setup_virtual_env() {
    local python_cmd=$1
    local service_name=$2

    local venv_dir=".venv"
    if [[ -n "$service_name" ]]; then
        venv_dir=".venv-${service_name}"
    fi

    if [[ ! -d "$venv_dir" ]]; then
        print_status "Creating virtual environment: $venv_dir"
        "$python_cmd" -m venv "$venv_dir"
    fi

    # Activate virtual environment
    source "$venv_dir/bin/activate"

    # Upgrade pip
    pip install --upgrade pip setuptools wheel

    echo "$venv_dir"
}

# Function to install dependencies
install_dependencies() {
    local service_name=$1

    print_status "Installing dependencies for $service_name"

    # Install common package dependencies first if we're not building common itself
    if [[ "$service_name" != "common" && -f "../common/requirements.txt" ]]; then
        print_status "Installing common package dependencies"
        pip install -r ../common/requirements.txt

        # Install common package in development mode
        if [[ -f "../common/setup.py" ]]; then
            print_status "Installing common package in development mode"
            pip install -e ../common
        fi
    elif [[ "$service_name" != "common" && -f "common/requirements.txt" ]]; then
        # We're in services root, install common package
        print_status "Installing common package dependencies"
        pip install -r common/requirements.txt

        if [[ -f "common/setup.py" ]]; then
            print_status "Installing common package in development mode"
            pip install -e common
        fi
    fi

    # Install service-specific dependencies
    if [[ -f "requirements.txt" ]]; then
        print_status "Installing service requirements"
        pip install -r requirements.txt
    fi

    # Install test dependencies from multiple possible locations
    local test_requirements=""
    if [[ -f "test-requirements.txt" ]]; then
        test_requirements="test-requirements.txt"
    elif [[ -f "tests/requirements.txt" ]]; then
        test_requirements="tests/requirements.txt"
    elif [[ -f "../tests/requirements.txt" ]]; then
        test_requirements="../tests/requirements.txt"
    fi

    if [[ -n "$test_requirements" && -f "$test_requirements" ]]; then
        print_status "Installing test dependencies from $test_requirements"
        pip install -r "$test_requirements"
    else
        print_status "No test requirements file found, installing basic test dependencies"
        pip install pytest pytest-asyncio pytest-mock pytest-cov
    fi

    # Install package in development mode if setup.py exists
    if [[ -f "setup.py" ]]; then
        print_status "Installing package in development mode"
        pip install -e .
    fi

    # For order-service, ensure we can import the common modules and service modules
    if [[ "$service_name" == "order-service" ]]; then
        # Add paths to enable imports during testing
        export PYTHONPATH="${PWD}/src:${PWD}/../common:${PYTHONPATH:-}"
        print_status "Set PYTHONPATH for order-service: $PYTHONPATH"
    fi
}

# Function to install dependencies for all-tests mode
install_all_tests_dependencies() {
    print_status "Installing dependencies for all tests"

    # Install common package dependencies and the package itself
    if [[ -f "common/requirements.txt" ]]; then
        print_status "Installing common package dependencies"
        pip install -r common/requirements.txt
    fi

    if [[ -f "common/setup.py" ]]; then
        print_status "Installing common package in development mode"
        pip install -e common
    fi

    # Install order-service dependencies for order-service tests
    if [[ -f "order-service/requirements.txt" ]]; then
        print_status "Installing order-service dependencies"
        pip install -r order-service/requirements.txt
    fi

    # Install test dependencies
    if [[ -f "tests/requirements.txt" ]]; then
        print_status "Installing test dependencies"
        pip install -r tests/requirements.txt
    else
        print_status "Installing basic test dependencies"
        pip install pytest pytest-asyncio pytest-mock pytest-cov
    fi

    # Set up Python path for tests - include all service source directories
    local python_paths="${PWD}/common"

    # Add order-service src directory to Python path
    if [[ -d "order-service/src" ]]; then
        python_paths="${python_paths}:${PWD}/order-service/src"
    fi

    # Add any other service directories that might be needed
    for service_dir in */; do
        if [[ -d "$service_dir/src" && "$service_dir" != "common/" && "$service_dir" != "tests/" ]]; then
            python_paths="${python_paths}:${PWD}/${service_dir}src"
        fi
    done

    # Add the services root directory itself
    python_paths="${python_paths}:${PWD}"

    export PYTHONPATH="${python_paths}:${PYTHONPATH:-}"
    print_status "Set PYTHONPATH for all tests: $PYTHONPATH"
}

# Function to clean build artifacts
clean_build() {
    print_status "Cleaning build artifacts"

    # Remove common build directories
    rm -rf "$BUILD_DIR" "$DIST_DIR" "*.egg-info" ".pytest_cache" ".coverage" "__pycache__"

    # Remove Python cache files recursively
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
}

# Function to run linting
run_linting() {
    print_status "Running code linting"

    # Check if linting tools are available
    local has_flake8=$(pip list | grep -i flake8 || true)
    local has_black=$(pip list | grep -i black || true)

    if [[ -n "$has_flake8" ]]; then
        print_status "Running flake8"
        flake8 . --exclude=.venv*,build,dist --max-line-length=88 || print_warning "Linting issues found"
    fi

    if [[ -n "$has_black" ]]; then
        print_status "Checking code formatting with black"
        black --check . --exclude="\.venv.*|build|dist" || print_warning "Code formatting issues found"
    fi
}

# Function to run tests
run_tests() {
    local coverage_threshold=$1
    local no_coverage=$2
    local verbose=$3
    local service_name=$4

    print_status "Running tests for service: $service_name"

    # Find test directory - look in multiple locations
    local test_dir=""
    local pytest_args=""

    # Check for service-specific test directory first
    if [[ -d "tests" ]]; then
        test_dir="tests"
        print_status "Found service-specific tests in: $test_dir"
    elif [[ -d "test" ]]; then
        test_dir="test"
        print_status "Found service-specific tests in: $test_dir"
    # Check for shared test directory
    elif [[ -d "../tests" ]]; then
        test_dir="../tests"
        print_status "Found shared tests in: $test_dir"

        # For shared tests, we need to set up the Python path correctly
        # and potentially filter tests based on the service

        # Add current service to Python path so tests can import from it
        export PYTHONPATH="${PWD}:${PWD}/src:${PYTHONPATH:-}"

        # For specific services, we might want to run all tests since they test shared components
        if [[ "$service_name" == "common" ]]; then
            # For common package, run all tests
            pytest_args="$test_dir"
        elif [[ "$service_name" == "order-service" ]]; then
            # For order-service, run all tests but exclude service-specific ones that don't apply
            pytest_args="$test_dir"
        else
            # For other services, run all tests
            pytest_args="$test_dir"
        fi
    elif [[ -d "../../tests" ]]; then
        test_dir="../../tests"
        print_status "Found shared tests in: $test_dir"
        export PYTHONPATH="${PWD}:${PWD}/src:${PYTHONPATH:-}"
        pytest_args="$test_dir"
    else
        print_warning "No test directory found. Checked:"
        print_warning "  - ./tests/"
        print_warning "  - ./test/"
        print_warning "  - ../tests/"
        print_warning "  - ../../tests/"
        print_warning "Skipping tests for $service_name"
        return 0
    fi

    # Build pytest command
    local pytest_cmd="pytest"

    if [[ "$verbose" == "true" ]]; then
        pytest_cmd="$pytest_cmd -v"
    fi

    # Add the test arguments
    if [[ -n "$pytest_args" ]]; then
        pytest_cmd="$pytest_cmd $pytest_args"
    else
        pytest_cmd="$pytest_cmd $test_dir"
    fi

    # Add coverage options
    if [[ "$no_coverage" != "true" ]]; then
        # Check if pytest-cov is available
        local has_coverage=$(pip list | grep pytest-cov || true)
        if [[ -n "$has_coverage" ]]; then
            # For shared test directory, we need to be more specific about what to cover
            if [[ "$test_dir" == "../tests" || "$test_dir" == "../../tests" ]]; then
                # Cover the service code, not the test code
                if [[ -d "src" ]]; then
                    pytest_cmd="$pytest_cmd --cov=src"
                elif [[ "$service_name" == "common" ]]; then
                    # For common package, cover the common modules
                    pytest_cmd="$pytest_cmd --cov=."
                else
                    # For services, cover the service source
                    pytest_cmd="$pytest_cmd --cov=."
                fi
                pytest_cmd="$pytest_cmd --cov-report=html --cov-report=term-missing"
            else
                pytest_cmd="$pytest_cmd --cov=. --cov-report=html --cov-report=term-missing"
            fi

            if [[ -n "$coverage_threshold" ]]; then
                pytest_cmd="$pytest_cmd --cov-fail-under=$coverage_threshold"
            fi
        fi
    fi

    print_status "Test command: $pytest_cmd"
    print_status "PYTHONPATH: ${PYTHONPATH:-<not set>}"

    # Run tests
    if ! eval "$pytest_cmd"; then
        print_error "Tests failed"
        return 1
    fi

    print_success "All tests passed"
}

# Function to run all tests (from services root)
run_all_tests() {
    local coverage_threshold=$1
    local no_coverage=$2
    local verbose=$3

    print_status "Running all tests from services/tests directory"

    if [[ ! -d "tests" ]]; then
        print_error "No tests directory found in services root"
        return 1
    fi

    # Build pytest command
    local pytest_cmd="pytest"

    if [[ "$verbose" == "true" ]]; then
        pytest_cmd="$pytest_cmd -v"
    fi

    pytest_cmd="$pytest_cmd tests"

    # Add coverage options
    if [[ "$no_coverage" != "true" ]]; then
        local has_coverage=$(pip list | grep pytest-cov || true)
        if [[ -n "$has_coverage" ]]; then
            # Cover the common package and order-service source
            local coverage_sources="--cov=common"

            # Add order-service src to coverage if it exists
            if [[ -d "order-service/src" ]]; then
                coverage_sources="$coverage_sources --cov=order-service/src"
            fi

            pytest_cmd="$pytest_cmd $coverage_sources --cov-report=html --cov-report=term-missing"

            if [[ -n "$coverage_threshold" ]]; then
                pytest_cmd="$pytest_cmd --cov-fail-under=$coverage_threshold"
            fi
        fi
    fi

    print_status "Test command: $pytest_cmd"
    print_status "PYTHONPATH: ${PYTHONPATH:-<not set>}"
    print_status "Current directory: $PWD"

    # Run tests
    if ! eval "$pytest_cmd"; then
        print_error "Tests failed"
        return 1
    fi

    print_success "All tests passed"
}

# Function to build package
build_package() {
    local service_name=$1

    if [[ ! -f "setup.py" ]]; then
        print_warning "No setup.py found, skipping package build"
        return 0
    fi

    print_status "Building package: $service_name"

    # Build source distribution and wheel
    python setup.py sdist bdist_wheel

    print_success "Package built successfully"
    print_status "Build artifacts:"
    ls -la dist/ 2>/dev/null || true
}

# Function to build Docker image
build_docker() {
    local service_name=$1

    if [[ ! -f "Dockerfile" ]]; then
        print_warning "No Dockerfile found, skipping Docker build"
        return 0
    fi

    print_status "Building Docker image for $service_name"

    local image_name="${service_name}:latest"
    docker build -t "$image_name" .

    print_success "Docker image built: $image_name"
}

# Function to get service directory
get_service_directory() {
    local service_name=$1

    # If we're already in the service directory
    if [[ -f "app.py" || -f "src/app.py" || -f "setup.py" ]]; then
        echo "."
    # If we're in the services root and looking for a specific service
    elif [[ -d "$service_name" ]]; then
        echo "$service_name"
    # If we're somewhere else and need to find the service in a services subdirectory
    elif [[ -d "services/$service_name" ]]; then
        echo "services/$service_name"
    else
        print_error "Service directory not found: $service_name"
        print_error "Current directory: $PWD"
        print_error "Looking for one of:"
        print_error "  - ./$service_name"
        print_error "  - ./services/$service_name"
        print_error "  - Current directory (if it contains app.py, src/app.py, or setup.py)"
        exit 1
    fi
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
    local build_docker=false
    local all_tests=false

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
            --docker)
                build_docker=true
                shift
                ;;
            --all-tests)
                all_tests=true
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

    # Handle all-tests mode
    if [[ "$all_tests" == "true" ]]; then
        # Check if we're in services root
        if [[ "$(basename "$PWD")" != "services" ]]; then
            print_error "--all-tests can only be used from the services root directory"
            exit 1
        fi

        print_status "Running all tests mode from services root"

        # Check Python version
        local python_cmd=$(check_python_version "$python_version")
        print_status "Using Python: $python_cmd"

        # Clean if requested
        if [[ "$clean" == "true" ]]; then
            clean_build
        fi

        # Setup virtual environment
        local venv_dir=$(setup_virtual_env "$python_cmd" "all-tests")
        print_success "Virtual environment ready: $venv_dir"

        # Install dependencies for all tests
        install_all_tests_dependencies

        # If only installing dependencies, exit here
        if [[ "$install_deps_only" == "true" ]]; then
            print_success "Dependencies installed successfully"
            exit 0
        fi

        # Run all tests
        if ! run_all_tests "$coverage_threshold" "$no_coverage" "$verbose"; then
            exit 1
        fi

        print_success "All tests completed successfully"
        exit 0
    fi

    # Detect service name if not provided
    if [[ -z "$service_name" ]]; then
        service_name=$(detect_service_name)
        print_status "Detected service: $service_name"
    fi

    # Get service directory
    local service_dir=$(get_service_directory "$service_name")
    local original_dir="$PWD"

    # Change to service directory
    if [[ "$service_dir" != "." ]]; then
        print_status "Changing to service directory: $service_dir"
        cd "$service_dir"
    fi

    # Check Python version
    local python_cmd=$(check_python_version "$python_version")
    print_status "Using Python: $python_cmd"

    # Clean if requested
    if [[ "$clean" == "true" ]]; then
        clean_build
    fi

    # Setup virtual environment
    local venv_dir=$(setup_virtual_env "$python_cmd" "$service_name")
    print_success "Virtual environment ready: $venv_dir"

    # Install dependencies
    install_dependencies "$service_name"

    # If only installing dependencies, exit here
    if [[ "$install_deps_only" == "true" ]]; then
        print_success "Dependencies installed successfully"
        cd "$original_dir"
        exit 0
    fi

    # Run linting
    if [[ "$test_only" != "true" && "$build_only" != "true" ]]; then
        run_linting
    fi

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

    # Build Docker image if requested
    if [[ "$build_docker" == "true" ]]; then
        build_docker "$service_name"
    fi

    print_success "Build completed successfully for: $service_name"

    # Return to original directory
    cd "$original_dir"
}

# Run main function with all arguments
main "$@"