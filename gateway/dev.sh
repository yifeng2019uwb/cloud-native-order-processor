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
    install                 Install Go dependencies (go mod tidy)
    build                   Build the gateway binary
    run                     Run the gateway server
    dev                     Run in development mode with hot reload
    test                    Run tests
    test-coverage           Run tests with coverage report
    lint                    Run linting checks
    format                  Format Go code
    clean                   Clean build artifacts
    docker-build            Build Docker image
    docker-run              Run in Docker container
    health-check            Check if gateway is running
    logs                    Show gateway logs (if running in background)

OPTIONS:
    -p, --port PORT         Set server port (default: ${DEFAULT_PORT})
    -h, --host HOST         Set server host (default: ${DEFAULT_HOST})
    --redis-host HOST       Set Redis host (default: ${DEFAULT_REDIS_HOST})
    --redis-port PORT       Set Redis port (default: ${DEFAULT_REDIS_PORT})
    -v, --verbose           Enable verbose output
    --no-redis              Run without Redis (for testing)

EXAMPLES:
    $0 install              # Install dependencies
    $0 build                # Build binary
    $0 run                  # Run server
    $0 dev                  # Run in development mode
    $0 test                 # Run tests
    $0 --port 9090 run      # Run on port 9090
    $0 --no-redis run       # Run without Redis

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

    # Run all tests
    go test ./... -v

    print_success "Tests completed"
}

# Function to run tests with coverage
run_tests_coverage() {
    print_info "Running tests with coverage..."

    # Create coverage directory
    mkdir -p coverage

    # Run tests with coverage
    go test ./... -v -coverprofile=coverage/coverage.out

    # Generate coverage report
    go tool cover -html=coverage/coverage.out -o coverage/coverage.html

    # Show coverage summary
    go tool cover -func=coverage/coverage.out

    print_success "Coverage report generated: coverage/coverage.html"
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

# Function to check if gateway is running
health_check() {
    local port=${GATEWAY_PORT:-$DEFAULT_PORT}

    print_info "Checking gateway health on port $port..."

    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        print_success "Gateway is running and healthy"
        curl -s http://localhost:$port/health | jq . 2>/dev/null || curl -s http://localhost:$port/health
    else
        print_error "Gateway is not running or not responding"
        exit 1
    fi
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

# Function to build Docker image
docker_build() {
    print_info "Building Docker image..."

    # Check if Dockerfile exists
    if [ ! -f "Dockerfile" ]; then
        print_error "Dockerfile not found"
        exit 1
    fi

    # Build image
    docker build -t order-processor-gateway:latest .

    print_success "Docker image built: order-processor-gateway:latest"
}

# Function to run in Docker
docker_run() {
    local port=${GATEWAY_PORT:-$DEFAULT_PORT}

    print_info "Running gateway in Docker on port $port..."

    # Run container
    docker run -d \
        --name gateway \
        -p $port:8080 \
        -e REDIS_HOST=${REDIS_HOST:-$DEFAULT_REDIS_HOST} \
        -e REDIS_PORT=${REDIS_PORT:-$DEFAULT_REDIS_PORT} \
        -e USER_SERVICE_URL=${USER_SERVICE_URL:-http://user-service:8000} \
        -e INVENTORY_SERVICE_URL=${INVENTORY_SERVICE_URL:-http://inventory-service:8001} \
        order-processor-gateway:latest

    print_success "Gateway running in Docker container"
    print_info "Access at: http://localhost:$port"
}

# Function to show logs
show_logs() {
    print_info "Showing gateway logs..."

    # Check if running in Docker
    if docker ps | grep -q gateway; then
        docker logs -f gateway
    else
        print_warning "Gateway not running in Docker. Check if it's running locally."
    fi
}

# Parse command line arguments
COMMAND=""
VERBOSE=false
NO_REDIS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        help)
            show_usage
            exit 0
            ;;
        install|build|run|dev|test|test-coverage|lint|format|clean|docker-build|docker-run|health-check|logs)
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
        --redis-host)
            REDIS_HOST="$2"
            shift 2
            ;;
        --redis-port)
            REDIS_PORT="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-redis)
            NO_REDIS=true
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
    test-coverage)
        run_tests_coverage
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
    docker-build)
        docker_build
        ;;
    docker-run)
        docker_run
        ;;
    health-check)
        health_check
        ;;
    logs)
        show_logs
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