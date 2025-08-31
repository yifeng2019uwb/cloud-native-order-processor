#!/bin/bash
# frontend/dev.sh
# Frontend development script - build, test, clean
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
Frontend Development Script

Usage: $0 {build|test|clean|ci} [test_target]

Commands:
    build              Build the frontend application
    test [test_target] Run frontend tests (all or specific file/class)
    clean              Clean build artifacts

Examples:
    $0 build                    # Build frontend
    $0 test                     # Run all tests
    $0 test UserComponent      # Test specific component
    $0 test user.test.ts       # Test specific file
    $0 test "user.*"           # Test files matching pattern
    $0 clean                   # Clean build files

EOF
}

# Check prerequisites
check_prerequisites() {
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        exit 1
    fi

    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

# Build frontend
build() {
    log_info "Building frontend..."

    cd "$SCRIPT_DIR"

    # Install dependencies if needed
    if [[ ! -d "node_modules" ]]; then
        log_info "Installing dependencies..."
        npm install
    fi

    # Build the application
    log_info "Building application..."
    npm run build

    log_success "Frontend build completed"
}

# Test frontend
test() {
    local test_target="$1"

    cd "$SCRIPT_DIR"

    # Always ensure dependencies are up to date for CI/CD
    log_info "Installing/updating dependencies..."
    npm install

    # Check if test script exists
    if npm run | grep -q "test:run"; then
        # Run tests
        if [[ -n "$test_target" ]]; then
            log_info "Running tests for: $test_target"
            npm run test:run -- --testPathPattern="$test_target"
        else
            log_info "Running all tests..."
            npm run test:run
        fi
        log_success "Frontend tests completed"
    else
        log_error "Test script 'test:run' not found in package.json"
        log_info "Available scripts:"
        npm run
        exit 1
    fi
}

# Clean build artifacts
clean() {
    log_info "Cleaning frontend build artifacts..."

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

    # Remove node_modules (optional, uncomment if needed)
    # if [[ -d "node_modules" ]]; then
    #     rm -rf node_modules
    #     log_info "Removed node_modules directory"
    # fi

    log_success "Frontend cleanup completed"
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
        ci)
            test "$2"
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
