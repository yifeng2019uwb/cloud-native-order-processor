#!/bin/bash

# Gateway Development Script
# Usage: ./dev.sh [COMMAND] [OPTIONS]
#
# This script provides convenient commands for developing the Go gateway service.
# It follows the same patterns as other components in the project.

set -e  # Exit on any error

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default configuration
DEFAULT_PORT="8080"
DEFAULT_HOST="0.0.0.0"
DEFAULT_REDIS_HOST="localhost"
DEFAULT_REDIS_PORT="6379"

# Function to show usage
show_usage() {
    cat << EOF
Gateway Development Script

Usage: $0 [COMMAND] [OPTIONS]

COMMANDS:
    help                    Show this help message
    install                 Install Go dependencies
    build                   Build the gateway binary
    run                     Run the gateway server
    dev                     Run in development mode
    test                    Run tests with coverage
    lint                    Run linting checks
    format                  Format Go code
    clean                   Clean build artifacts

OPTIONS:
    -p, --port PORT         Set server port (default: ${DEFAULT_PORT})
    -h, --host HOST         Set server host (default: ${DEFAULT_HOST})
    -v, --verbose           Enable verbose output

EXAMPLES:
    $0 install              # Install dependencies
    $0 build                # Build binary
    $0 run                  # Run server
    $0 dev                  # Run in development mode
    $0 test                 # Run tests
    $0 --port 9090 run      # Run on port 9090

ENVIRONMENT VARIABLES:
    GATEWAY_PORT            Server port
    GATEWAY_HOST            Server host
    REDIS_HOST              Redis host
    REDIS_PORT              Redis port
    REDIS_PASSWORD          Redis password
    REDIS_DB                Redis database number
    REDIS_SSL               Redis SSL (true/false)
    USER_SERVICE_URL        User service URL
    INVENTORY_SERVICE_URL   Inventory service URL

EOF
}

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if Go is installed
check_go() {
    if ! command -v go &> /dev/null; then
        print_error "Go is not installed. Please install Go 1.24+ first."
        exit 1
    fi

    local go_version=$(go version | awk '{print $3}' | sed 's/go//')
    print_info "Go version: $go_version"
}

# Function to install dependencies
install_deps() {
    print_info "Installing Go dependencies..."

    # Run go mod tidy to clean up dependencies
    go mod tidy

    # Verify dependencies
    go mod verify

    print_success "Dependencies installed successfully"
}

# Function to build the gateway
build_gateway() {
    print_info "Building gateway binary..."

    # Clean previous build
    rm -f gateway

    # Build the binary
    go build -o gateway cmd/gateway/main.go

    if [ -f "gateway" ]; then
        print_success "Gateway built successfully: ./gateway"
        ls -la gateway
    else
        print_error "Build failed"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    print_info "Running tests..."

    # Run all tests with coverage display (Go standard - tests alongside source)
    go test -cover ./...

    print_success "Tests completed"
}



# Function to run linting
run_lint() {
    print_info "Running linting checks..."

    # Check if golangci-lint is installed
    if ! command -v golangci-lint &> /dev/null; then
        print_warning "golangci-lint not found. Installing..."
        go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
    fi

    # Run linting
    golangci-lint run

    print_success "Linting completed"
}

# Function to format code
format_code() {
    print_info "Formatting Go code..."

    # Format all Go files
    go fmt ./...

    # Run goimports if available
    if command -v goimports &> /dev/null; then
        find . -name "*.go" -not -path "./vendor/*" -exec goimports -w {} \;
    else
        print_warning "goimports not found. Install with: go install golang.org/x/tools/cmd/goimports@latest"
    fi

    print_success "Code formatting completed"
}

# Function to clean build artifacts
clean_build() {
    print_info "Cleaning build artifacts..."

    # Remove binary
    rm -f gateway

    # Remove coverage files
    rm -rf coverage/

    # Clean Go cache
    go clean -cache -testcache

    print_success "Cleanup completed"
}



# Function to run the gateway
run_gateway() {
    local port=${GATEWAY_PORT:-$DEFAULT_PORT}
    local host=${GATEWAY_HOST:-$DEFAULT_HOST}

    print_info "Starting gateway on $host:$port..."

    # Set environment variables if provided
    if [ "$REDIS_HOST" != "" ]; then
        export REDIS_HOST
    fi
    if [ "$REDIS_PORT" != "" ]; then
        export REDIS_PORT
    fi
    if [ "$REDIS_PASSWORD" != "" ]; then
        export REDIS_PASSWORD
    fi
    if [ "$REDIS_DB" != "" ]; then
        export REDIS_DB
    fi
    if [ "$REDIS_SSL" != "" ]; then
        export REDIS_SSL
    fi
    if [ "$USER_SERVICE_URL" != "" ]; then
        export USER_SERVICE_URL
    fi
    if [ "$INVENTORY_SERVICE_URL" != "" ]; then
        export INVENTORY_SERVICE_URL
    fi

    # Run the gateway
    ./gateway
}

# Function to run in development mode
run_dev() {
    print_info "Starting gateway in development mode..."

    # Check if air is installed for hot reload
    if command -v air &> /dev/null; then
        print_info "Using air for hot reload..."
        air
    else
        print_warning "air not found. Install with: go install github.com/cosmtrek/air@latest"
        print_info "Running without hot reload..."
        run_gateway
    fi
}



# Parse command line arguments
COMMAND=""
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        help)
            show_usage
            exit 0
            ;;
        install|build|run|dev|test|lint|format|clean)
            COMMAND="$1"
            shift
            ;;
        -p|--port)
            GATEWAY_PORT="$2"
            shift 2
            ;;
        -h|--host)
            GATEWAY_HOST="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Set verbose mode
if [ "$VERBOSE" = true ]; then
    set -x
fi

# Check Go installation
check_go

# Execute command
case $COMMAND in
    install)
        install_deps
        ;;
    build)
        build_gateway
        ;;
    run)
        build_gateway
        run_gateway
        ;;
    dev)
        build_gateway
        run_dev
        ;;
    test)
        run_tests
        ;;
    lint)
        run_lint
        ;;
    format)
        format_code
        ;;
    clean)
        clean_build
        ;;

    "")
        print_error "No command specified"
        show_usage
        exit 1
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac