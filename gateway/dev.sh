#!/bin/bash
# gateway/dev.sh
# Gateway development script - build, test, clean
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

log_warning() {
    printf "${YELLOW}[WARNING]${NC} %s\n" "$1"
}

# Usage function
show_usage() {
    cat << EOF
Gateway Development Script

Usage: $0 {build|test|clean} [test_target]

Commands:
    build              Build the gateway binary
    test [test_target] Run gateway tests (all or specific package)
    clean              Clean build artifacts

Examples:
    $0 build                    # Build gateway
    $0 test                     # Run all tests
    $0 test internal/api        # Test specific package
    $0 test "internal/*"        # Test packages matching pattern
    $0 clean                    # Clean build files

EOF
}

# Check prerequisites
check_prerequisites() {
    if ! command -v go &> /dev/null; then
        log_error "Go is not installed. Please install Go 1.24+ first."
        exit 1
    fi

    local go_version=$(go version | awk '{print $3}' | sed 's/go//')
    log_info "Go version: $go_version"
}

# Build gateway
build() {
    log_info "Building gateway..."

    cd "$SCRIPT_DIR"

    # Install dependencies
    log_info "Installing Go dependencies..."
    go mod tidy
    go mod verify

    # Build the binary
    log_info "Building binary..."
    go build -o gateway cmd/gateway/main.go

    if [ -f "gateway" ]; then
        log_success "Gateway built successfully: ./gateway"
        ls -la gateway
    else
        log_error "Build failed"
        exit 1
    fi
}

# Test gateway
test() {
    local test_target="$1"

    cd "$SCRIPT_DIR"

    # Install dependencies if needed
    log_info "Installing Go dependencies..."
    go mod tidy

    # Run tests with coverage
    if [[ -n "$test_target" ]]; then
        log_info "Running tests for: $test_target"
        go test -cover ./$test_target
    else
        log_info "Running all tests..."
        go test -cover ./...
    fi



    log_success "Gateway tests completed"
}

# Clean build artifacts
clean() {
    log_info "Cleaning gateway build artifacts..."

    cd "$SCRIPT_DIR"

    # Remove binary
    if [[ -f "gateway" ]]; then
        rm -f gateway
        log_info "Removed gateway binary"
    fi

    # Remove test cache
    if [[ -d ".test-cache" ]]; then
        rm -rf .test-cache
        log_info "Removed test cache"
    fi

    log_success "Gateway cleanup completed"
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