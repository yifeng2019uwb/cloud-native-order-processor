#!/bin/bash

# Gateway Build Script
# Usage: ./build.sh [OPTIONS]

set -e  # Exit on any error

# Default configuration
DEFAULT_GO_VERSION="1.24"
DEFAULT_BUILD_OS="linux"
DEFAULT_BUILD_ARCH="amd64"

# Function to show usage
show_usage() {
    cat << EOF
Gateway Build Script

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -b, --build-only        Build only, skip tests
    -t, --test-only         Run tests only, skip building
    -v, --verbose           Enable verbose output

Examples:
    $0                      # Build and test gateway (default)
    $0 --build-only         # Build only
    $0 --test-only          # Run tests only
    $0 -v                   # Verbose output

EOF
}

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

log_warning() {
    printf "${YELLOW}[WARNING]${NC} %s\n" "$1"
}

log_error() {
    printf "${RED}[ERROR]${NC} %s\n" "$1"
}

log_step() {
    printf "\n${BLUE}=== %s ===${NC}\n" "$1"
}

# Function to check Go installation
check_go() {
    if ! command -v go &> /dev/null; then
        log_error "Go is not installed. Please install Go ${DEFAULT_GO_VERSION}+"
        exit 1
    fi

    local go_version=$(go version | awk '{print $3}' | sed 's/go//')
    log_info "Go version: $go_version"

    # Check if version meets minimum requirement
    local required_version=${GO_VERSION:-$DEFAULT_GO_VERSION}
    if [[ "$(printf '%s\n' "$required_version" "$go_version" | sort -V | head -n1)" != "$required_version" ]]; then
        log_warning "Go version $go_version is older than recommended $required_version"
    fi
}

# Function to clean build artifacts
clean_build() {
    log_step "Cleaning build artifacts"

    if [[ -f "gateway" ]]; then
        rm -f gateway
        log_success "Removed gateway binary"
    fi

    if [[ -d "dist" ]]; then
        rm -rf dist
        log_success "Removed dist directory"
    fi

    # Clean Go cache if requested
    if [[ "$CLEAN_CACHE" == "true" ]]; then
        go clean -cache -modcache -testcache
        log_success "Cleaned Go cache"
    fi
}

# Function to install dependencies
install_deps() {
    log_step "Installing dependencies"

    if [[ "$VERBOSE" == "true" ]]; then
        go mod download
        go mod verify
    else
        go mod download -x
        go mod verify
    fi

    log_success "Dependencies installed and verified"
}

# Function to run code formatting
run_format() {
    log_step "Running code formatting"

    if [[ "$VERBOSE" == "true" ]]; then
        go fmt ./...
    else
        go fmt ./... > /dev/null 2>&1
    fi

    log_success "Code formatting completed"
}

# Function to run linting
run_lint() {
    log_step "Running linting"

    # Check if golangci-lint is available
    if command -v golangci-lint &> /dev/null; then
        if [[ "$VERBOSE" == "true" ]]; then
            golangci-lint run
        else
            golangci-lint run --quiet
        fi
        log_success "Linting completed with golangci-lint"
    else
        log_warning "golangci-lint not found, using go vet instead"
        run_vet
    fi
}

# Function to run go vet
run_vet() {
    log_step "Running go vet"

    if [[ "$VERBOSE" == "true" ]]; then
        go vet ./...
    else
        go vet ./... > /dev/null 2>&1
    fi

    log_success "Go vet completed"
}

# Function to build gateway
build_gateway() {
    log_step "Building gateway"

    local build_flags=""
    if [[ "$VERBOSE" == "true" ]]; then
        build_flags="-v"
    fi

    # Set build environment variables for cross-compilation
    export CGO_ENABLED=0
    export GOOS=${BUILD_OS:-$DEFAULT_BUILD_OS}
    export GOARCH=${BUILD_ARCH:-$DEFAULT_BUILD_ARCH}

    log_info "Building for $GOOS/$GOARCH"

    # Build the binary
    if go build $build_flags -o gateway cmd/gateway/main.go; then
        if [[ -f "gateway" ]]; then
            local binary_size=$(du -h gateway | cut -f1)
            log_success "Gateway built successfully: ./gateway ($binary_size)"
            log_info "Binary info: $(file gateway)"
        else
            log_error "Build failed - gateway binary not found"
            exit 1
        fi
    else
        log_error "Build failed"
        exit 1
    fi

    # Reset environment variables for tests
    unset GOOS
    unset GOARCH
}

# Function to run tests
run_tests() {
    log_step "Running tests"

    local test_flags=""
    if [[ "$VERBOSE" == "true" ]]; then
        test_flags="-v"
    fi

    # Run tests with coverage
    if go test $test_flags -cover ./...; then
        log_success "Tests completed"

        # Generate coverage report if requested
        if [[ "$COVERAGE_REPORT" == "true" ]]; then
            go test -coverprofile=coverage.out ./...
            go tool cover -func=coverage.out
            log_success "Coverage report generated: coverage.out"
        fi
    else
        log_error "Tests failed"
        exit 1
    fi
}

# Function to run gateway
run_gateway() {
    log_step "Starting gateway"

    if [[ ! -f "gateway" ]]; then
        log_error "Gateway binary not found. Please build first."
        exit 1
    fi

    log_info "Starting gateway on port ${GATEWAY_PORT:-8080}"
    log_info "Press Ctrl+C to stop"

    # Set environment variables if provided
    if [[ -n "$REDIS_HOST" ]]; then
        export REDIS_HOST
    fi
    if [[ -n "$REDIS_PORT" ]]; then
        export REDIS_PORT
    fi
    if [[ -n "$USER_SERVICE_URL" ]]; then
        export USER_SERVICE_URL
    fi
    if [[ -n "$INVENTORY_SERVICE_URL" ]]; then
        export INVENTORY_SERVICE_URL
    fi

    # Run the gateway
    ./gateway
}

# Function to build Docker image
build_docker() {
    log_step "Building Docker image"

    if [[ ! -f "gateway" ]]; then
        log_error "Gateway binary not found. Please build first."
        exit 1
    fi

    local image_name="order-processor-gateway"
    local tag="latest"

    if [[ -n "$DOCKER_TAG" ]]; then
        tag="$DOCKER_TAG"
    fi

    log_info "Building Docker image: $image_name:$tag"

    if docker build -f ../docker/gateway/Dockerfile -t "$image_name:$tag" ..; then
        log_success "Docker image built: $image_name:$tag"
        log_info "Image info: $(docker images $image_name:$tag --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}')"
    else
        log_error "Docker build failed"
        exit 1
    fi
}

# Parse command line arguments
TEST_ONLY=false
BUILD_ONLY=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -t|--test-only)
            TEST_ONLY=true
            shift
            ;;
        -b|--build-only)
            BUILD_ONLY=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Set verbose mode
if [[ "$VERBOSE" == "true" ]]; then
    set -x
fi

# Check prerequisites
log_step "Checking prerequisites"
check_go

# Change to gateway directory
cd "$(dirname "$0")"
log_info "Working directory: $(pwd)"

# Main execution logic
if [[ "$TEST_ONLY" == "true" ]]; then
    # For test-only, assume code is already built, just run tests
    run_tests
    exit 0
fi

if [[ "$BUILD_ONLY" == "true" ]]; then
    # For build-only, install deps, format, lint, and build
    install_deps
    run_format
    run_lint
    build_gateway
    exit 0
fi

# Default: build and test (full process)
install_deps
run_format
run_lint
build_gateway
run_tests

log_success "Gateway build and test completed successfully!"