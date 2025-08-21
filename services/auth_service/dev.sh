#!/bin/bash
# services/auth_service/dev.sh
# Auth Service development script - build, test, clean
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
Auth Service Development Script

Usage: $0 {build|test|clean} [test_target]

Commands:
    build              Build the auth service package
    test [test_target] Run auth service tests (all or specific file/class)
    clean              Clean build artifacts

Examples:
    $0 build                    # Build auth service
    $0 test                     # Run all tests
    $0 test test_validate       # Test specific test file
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

# Build auth service
build() {
    log_info "Building auth service..."

    cd "$SCRIPT_DIR"

    # Create virtual environment if it doesn't exist
    if [[ ! -d ".venv-auth_service" ]]; then
        log_info "Creating virtual environment..."
        python3 -m venv .venv-auth_service
    fi

    # Activate virtual environment
    source .venv-auth_service/bin/activate

    # Install dependencies
    log_info "Installing dependencies..."
    pip install -r requirements.txt

    # Build the package
    log_info "Building package..."
    python setup.py build

    log_success "Auth service build completed"
}

# Test auth service
test() {
    local test_target="$1"

    cd "$SCRIPT_DIR"

    # Check if virtual environment exists
    if [[ ! -d ".venv-auth_service" ]]; then
        log_error "Virtual environment not found. Run 'build' first."
        exit 1
    fi

    # Activate virtual environment
    source .venv-auth_service/bin/activate

    # Run tests
    if [[ -n "$test_target" ]]; then
        log_info "Running tests for: $test_target"
        python -m pytest "tests/$test_target" -v
    else
        log_info "Running all tests..."
        python -m pytest tests/ -v
    fi

    log_success "Tests completed"
}

# Clean build artifacts
clean() {
    log_info "Cleaning auth service..."

    cd "$SCRIPT_DIR"

    # Remove virtual environment
    if [[ -d ".venv-auth_service" ]]; then
        log_info "Removing virtual environment..."
        rm -rf .venv-auth_service
    fi

    # Remove build artifacts
    if [[ -d "build" ]]; then
        log_info "Removing build directory..."
        rm -rf build
    fi

    if [[ -d "dist" ]]; then
        log_info "Removing dist directory..."
        rm -rf dist
    fi

    if [[ -d "*.egg-info" ]]; then
        log_info "Removing egg-info directories..."
        rm -rf *.egg-info
    fi

    if [[ -d "htmlcov-auth_service" ]]; then
        log_info "Removing coverage reports..."
        rm -rf htmlcov-auth_service
    fi

    if [[ -d ".pytest_cache" ]]; then
        log_info "Removing pytest cache..."
        rm -rf .pytest_cache
    fi

    if [[ -d ".coverage" ]]; then
        log_info "Removing coverage file..."
        rm -f .coverage
    fi

    log_success "Clean completed"
}

# Main script logic
main() {
    case "${1:-}" in
        build)
            check_prerequisites
            build
            ;;
        test)
            check_prerequisites
            test "$2"
            ;;
        clean)
            clean
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
