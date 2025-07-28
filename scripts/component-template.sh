#!/bin/bash

# Universal Component Development Script
# Usage: ./scripts/component-template.sh [COMMAND] [OPTIONS]
#
# This script works from any component directory and auto-detects the component type.
# No need to copy or customize - just use it directly!

set -e  # Exit on any error

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    cat << EOF
Universal Component Development Script

Usage: $0 [COMMAND] [OPTIONS]

COMMANDS:
    help                    Show this help message
    install                 Install dependencies
    build                   Build the component
    run                     Run the component
    dev                     Run in development mode
    test                    Run tests
    test-coverage           Run tests with coverage
    lint                    Run linting checks
    format                  Format code
    clean                   Clean build artifacts
    docker-build            Build Docker image
    docker-run              Run in Docker container
    health-check            Check if component is running
    logs                    Show component logs

OPTIONS:
    -p, --port PORT         Set server port
    -h, --host HOST         Set server host
    -v, --verbose           Enable verbose output

EXAMPLES:
    $0 install              # Install dependencies
    $0 build                # Build component
    $0 run                  # Run component
    $0 dev                  # Run in development mode
    $0 test                 # Run tests
    $0 --port 9090 run      # Run on port 9090

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

# Function to detect component type and name
detect_component() {
    local current_dir=$(basename "$PWD")

    if [ -f "go.mod" ]; then
        COMPONENT_TYPE="go"
        COMPONENT_NAME="$current_dir"
        DEFAULT_PORT="8080"
    elif [ -f "package.json" ]; then
        COMPONENT_TYPE="node"
        COMPONENT_NAME="$current_dir"
        DEFAULT_PORT="3000"
    elif [ -f "setup.py" ] || [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
        COMPONENT_TYPE="python"
        COMPONENT_NAME="$current_dir"
        DEFAULT_PORT="8000"
    elif [ -f "Dockerfile" ]; then
        COMPONENT_TYPE="docker"
        COMPONENT_NAME="$current_dir"
        DEFAULT_PORT="8080"
    else
        print_error "No supported component detected in current directory"
        print_info "Supported: Go (go.mod), Node.js (package.json), Python (setup.py/requirements.txt), Docker (Dockerfile)"
        exit 1
    fi

    print_info "Detected: $COMPONENT_TYPE component '$COMPONENT_NAME' (port: $DEFAULT_PORT)"
}

# Function to install dependencies
install_deps() {
    print_info "Installing dependencies for $COMPONENT_TYPE component..."

    case $COMPONENT_TYPE in
        "go")
            go mod tidy
            go mod verify
            ;;
        "node")
            npm install
            ;;
        "python")
            if [ -f "requirements.txt" ]; then
                pip install -r requirements.txt
            elif [ -f "setup.py" ]; then
                pip install -e .
            fi
            ;;
        "docker")
            print_info "Docker component - no dependencies to install"
            ;;
    esac

    print_success "Dependencies installed successfully"
}

# Function to build component
build_component() {
    print_info "Building $COMPONENT_TYPE component..."

    case $COMPONENT_TYPE in
        "go")
            go build -o $COMPONENT_NAME cmd/*/main.go 2>/dev/null || go build -o $COMPONENT_NAME .
            ;;
        "node")
            npm run build
            ;;
        "python")
            if [ -f "setup.py" ]; then
                python setup.py build
            fi
            ;;
        "docker")
            docker build -t $COMPONENT_NAME:latest .
            ;;
    esac

    print_success "Component built successfully"
}

# Function to run component
run_component() {
    local port=${PORT:-$DEFAULT_PORT}
    local host=${HOST:-"0.0.0.0"}

    print_info "Starting $COMPONENT_TYPE component on $host:$port..."

    case $COMPONENT_TYPE in
        "go")
            ./$COMPONENT_NAME
            ;;
        "node")
            PORT=$port HOST=$host npm start
            ;;
        "python")
            if [ -f "main.py" ]; then
                python main.py
            elif [ -f "app.py" ]; then
                python app.py
            else
                print_error "No main entry point found"
                exit 1
            fi
            ;;
        "docker")
            docker run -p $port:$port $COMPONENT_NAME:latest
            ;;
    esac
}

# Function to run in development mode
run_dev() {
    print_info "Starting $COMPONENT_TYPE component in development mode..."

    case $COMPONENT_TYPE in
        "go")
            if command -v air &> /dev/null; then
                air
            else
                print_warning "air not found. Install with: go install github.com/cosmtrek/air@latest"
                run_component
            fi
            ;;
        "node")
            npm run dev
            ;;
        "python")
            if command -v uvicorn &> /dev/null; then
                uvicorn main:app --reload --host 0.0.0.0 --port ${PORT:-$DEFAULT_PORT}
            else
                print_warning "uvicorn not found. Install with: pip install uvicorn"
                run_component
            fi
            ;;
        "docker")
            docker run -p ${PORT:-$DEFAULT_PORT}:${PORT:-$DEFAULT_PORT} -v $(pwd):/app $COMPONENT_NAME:latest
            ;;
    esac
}

# Function to run tests
run_tests() {
    print_info "Running tests for $COMPONENT_TYPE component..."

    case $COMPONENT_TYPE in
        "go")
            go test ./... -v
            ;;
        "node")
            npm test
            ;;
        "python")
            if command -v pytest &> /dev/null; then
                pytest -v
            elif command -v python -m pytest &> /dev/null; then
                python -m pytest -v
            else
                print_warning "pytest not found. Install with: pip install pytest"
            fi
            ;;
        "docker")
            print_info "Docker component - no tests to run"
            ;;
    esac

    print_success "Tests completed"
}

# Function to run tests with coverage
run_tests_coverage() {
    print_info "Running tests with coverage for $COMPONENT_TYPE component..."

    mkdir -p coverage

    case $COMPONENT_TYPE in
        "go")
            go test ./... -v -coverprofile=coverage/coverage.out
            go tool cover -html=coverage/coverage.out -o coverage/coverage.html
            go tool cover -func=coverage/coverage.out
            ;;
        "node")
            npm run test:coverage 2>/dev/null || npm test -- --coverage
            ;;
        "python")
            if command -v pytest &> /dev/null; then
                pytest --cov=. --cov-report=html:coverage --cov-report=term
            else
                print_warning "pytest not found. Install with: pip install pytest pytest-cov"
            fi
            ;;
        "docker")
            print_info "Docker component - no coverage to run"
            ;;
    esac

    print_success "Coverage report generated"
}

# Function to run linting
run_lint() {
    print_info "Running linting for $COMPONENT_TYPE component..."

    case $COMPONENT_TYPE in
        "go")
            if command -v golangci-lint &> /dev/null; then
                golangci-lint run
            else
                print_warning "golangci-lint not found. Install with: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"
            fi
            ;;
        "node")
            npm run lint 2>/dev/null || echo "No lint script configured"
            ;;
        "python")
            if command -v flake8 &> /dev/null; then
                flake8 .
            elif command -v pylint &> /dev/null; then
                pylint .
            else
                print_warning "No linter found. Install with: pip install flake8 or pip install pylint"
            fi
            ;;
        "docker")
            if command -v hadolint &> /dev/null; then
                hadolint Dockerfile
            else
                print_warning "hadolint not found. Install with: brew install hadolint"
            fi
            ;;
    esac

    print_success "Linting completed"
}

# Function to format code
format_code() {
    print_info "Formatting code for $COMPONENT_TYPE component..."

    case $COMPONENT_TYPE in
        "go")
            go fmt ./...
            if command -v goimports &> /dev/null; then
                find . -name "*.go" -not -path "./vendor/*" -exec goimports -w {} \;
            fi
            ;;
        "node")
            npm run format 2>/dev/null || echo "No format script configured"
            ;;
        "python")
            if command -v black &> /dev/null; then
                black .
            elif command -v autopep8 &> /dev/null; then
                autopep8 --in-place --recursive .
            else
                print_warning "No formatter found. Install with: pip install black or pip install autopep8"
            fi
            ;;
        "docker")
            print_info "Docker component - no formatting needed"
            ;;
    esac

    print_success "Code formatting completed"
}

# Function to clean build artifacts
clean_build() {
    print_info "Cleaning build artifacts for $COMPONENT_TYPE component..."

    case $COMPONENT_TYPE in
        "go")
            rm -f $COMPONENT_NAME
            rm -rf coverage/
            go clean -cache -testcache
            ;;
        "node")
            rm -rf node_modules/
            rm -rf dist/
            rm -rf coverage/
            ;;
        "python")
            rm -rf build/
            rm -rf dist/
            rm -rf *.egg-info/
            rm -rf coverage/
            find . -type d -name "__pycache__" -exec rm -rf {} +
            find . -type f -name "*.pyc" -delete
            ;;
        "docker")
            docker rmi $COMPONENT_NAME:latest 2>/dev/null || true
            ;;
    esac

    print_success "Cleanup completed"
}

# Function to check if component is running
health_check() {
    local port=${PORT:-$DEFAULT_PORT}

    print_info "Checking component health on port $port..."

    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        print_success "Component is running and healthy"
        curl -s http://localhost:$port/health | jq . 2>/dev/null || curl -s http://localhost:$port/health
    else
        print_error "Component is not running or not responding"
        exit 1
    fi
}

# Function to build Docker image
docker_build() {
    if [ ! -f "Dockerfile" ]; then
        print_error "Dockerfile not found"
        exit 1
    fi

    print_info "Building Docker image..."
    docker build -t $COMPONENT_NAME:latest .
    print_success "Docker image built: $COMPONENT_NAME:latest"
}

# Function to run in Docker
docker_run() {
    local port=${PORT:-$DEFAULT_PORT}

    print_info "Running component in Docker on port $port..."

    docker run -d \
        --name $COMPONENT_NAME \
        -p $port:$port \
        $COMPONENT_NAME:latest

    print_success "Component running in Docker container"
    print_info "Access at: http://localhost:$port"
}

# Function to show logs
show_logs() {
    print_info "Showing component logs..."

    if docker ps | grep -q $COMPONENT_NAME; then
        docker logs -f $COMPONENT_NAME
    else
        print_warning "Component not running in Docker. Check if it's running locally."
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
        install|build|run|dev|test|test-coverage|lint|format|clean|docker-build|docker-run|health-check|logs)
            COMMAND="$1"
            shift
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -h|--host)
            HOST="$2"
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

# Auto-detect component
detect_component

# Execute command
case $COMMAND in
    install)
        install_deps
        ;;
    build)
        build_component
        ;;
    run)
        build_component
        run_component
        ;;
    dev)
        build_component
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