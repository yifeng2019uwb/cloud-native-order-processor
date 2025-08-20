#!/bin/bash
# services/inventory_service/dev.sh
# Inventory Service development script - build, test, clean
# Simple interface for fast iteration during coding

set -e

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    printf "${BLUE}[INFO]${NC} %s\n" "$1"
}

log_success() {
    printf "${GREEN}[SUCCESS]${NC} %s\n" "$1"
}

log_error() {
    printf "${RED}[ERROR]${NC} %s\n" "$1"
}

# Usage function
show_usage() {
    cat << EOF
Inventory Service Development Script

Usage: $0 {build|test|clean} [test_target]

Commands:
    build              Build the inventory service package
    test [test_target] Run inventory service tests (all or specific file/class)
    clean              Clean build artifacts

Examples:
    $0 build                    # Build inventory service
    $0 test                     # Run all tests
    $0 test test_inventory     # Test specific test file
    $0 test "test_*.py"        # Test files matching pattern
    $0 clean                   # Clean build files

EOF
}

# Check prerequisites
check_prerequisites() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi

    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

# Build inventory service
build() {
    log_info "Building inventory service..."

    cd "$SCRIPT_DIR"

    # Create virtual environment if it doesn't exist
    if [[ ! -d ".venv-inventory_service" ]]; then
        log_info "Creating virtual environment..."
        python3 -m venv .venv-inventory_service
    fi

    # Activate virtual environment
    source .venv-inventory_service/bin/activate

    # Install dependencies
    log_info "Installing dependencies..."
    pip install -r requirements.txt

    # Build the package
    log_info "Building package..."
    python setup.py build

    log_success "Inventory service build completed"
}

# Test inventory service
test() {
    local test_target="$1"

    cd "$SCRIPT_DIR"

    # Create virtual environment if it doesn't exist
    if [[ ! -d ".venv-inventory_service" ]]; then
        log_info "Creating virtual environment..."
        python3 -m venv .venv-inventory_service
    fi

    # Activate virtual environment
    source .venv-inventory_service/bin/activate

    # Install dependencies if needed
    if ! pip show pytest &> /dev/null; then
        log_info "Installing dependencies..."
        pip install -r requirements.txt
    fi

    # Set up Python path for imports
    export PYTHONPATH="${PWD}/src:${PYTHONPATH:-}"

    # Run tests with coverage (respects pytest.ini configuration)
    if [[ -n "$test_target" ]]; then
        log_info "Running tests for: $test_target"
        python -m pytest "tests/$test_target" -v
    else
        log_info "Running all tests with coverage..."
        python -m pytest tests/ -v
    fi

    # Show coverage summary
    if [[ -d "htmlcov-inventory_service" ]]; then
        log_info "Coverage report generated: htmlcov-inventory_service/index.html"
    fi

    log_success "Inventory service tests completed"
}

# Clean build artifacts
clean() {
    log_info "Cleaning inventory service build artifacts..."

    cd "$SCRIPT_DIR"

    # Remove build directories
    if [[ -d "dist" ]]; then
        rm -rf dist
        log_info "Removed dist directory"
    fi

    if [[ -d "build" ]]; then
        rm -rf build
        log_info "Removed build directory"
    fi

    # Remove virtual environment (optional, uncomment if needed)
    # if [[ -d ".venv-inventory_service" ]]; then
    #     rm -rf .venv-inventory_service
    #     log_info "Removed virtual environment"
    # fi

    # Remove cache directories
    if [[ -d "__pycache__" ]]; then
        rm -rf __pycache__
        log_info "Removed __pycache__ directory"
    fi

    if [[ -d ".pytest_cache" ]]; then
        rm -rf .pytest_cache
        log_info "Removed .pytest_cache directory"
    fi

    # Remove coverage reports
    if [[ -d "htmlcov-inventory_service" ]]; then
        rm -rf htmlcov-inventory_service
        log_info "Removed coverage reports"
    fi

    log_success "Inventory service cleanup completed"
}

# Main function
main() {
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 1
    fi

    local command="$1"

    # Check prerequisites
    check_prerequisites

    # Execute command
    case $command in
        build)
            build
            ;;
        test)
            test "$2"
            ;;
        clean)
            clean
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Script execution
main "$@"
