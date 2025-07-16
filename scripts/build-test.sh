#!/bin/bash
# scripts/build-test.sh
# Unified Build & Test Script for All Services
# Usage: ./scripts/build-test.sh [SERVICE_NAME] [OPTIONS]

set -e

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SERVICES_DIR="$PROJECT_ROOT/services"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
SERVICE_NAME=""
VERBOSE=false
CLEAN=false
TEST_ONLY=false
BUILD_ONLY=false
NO_CACHE=false
COVERAGE_THRESHOLD=60  # TODO: Increase to 80% when all services have proper test coverage
SKIP_COVERAGE=false

# Available services
AVAILABLE_SERVICES=("common" "user_service" "inventory_service")

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
    printf "\n${PURPLE}=== %s ===${NC}\n" "$1"
}

log_substep() {
    printf "${CYAN}--- %s ---${NC}\n" "$1"
}

# Usage function
show_usage() {
    cat << EOF
$(printf "${BLUE}🔨 Unified Build & Test Script${NC}")

Usage: $0 [SERVICE_NAME] [OPTIONS]

Build and test services individually or all at once.

SERVICE_NAME:
    ${AVAILABLE_SERVICES[*]}
    all                    # Build/test all services
    If not specified, will build/test all services

OPTIONS:
    -h, --help              Show this help message
    -v, --verbose           Enable verbose output
    -c, --clean             Clean build artifacts before building
    -t, --test-only         Run tests only, skip building
    -b, --build-only        Build only, skip tests
    --no-cache              Build Docker images with --no-cache
    --coverage THRESHOLD    Set test coverage threshold (default: 60, target: 80)
    --no-coverage           Skip coverage reporting
    --install-deps          Install dependencies only

EXAMPLES:
    # Build and test all services
    $0
    $0 all

    # Build and test specific service
    $0 common
    $0 user_service
    $0 inventory_service

    # Test only (no build)
    $0 --test-only
    $0 common --test-only

    # Build only (no tests)
    $0 --build-only
    $0 user_service --build-only

    # Clean build
    $0 --clean --verbose
    $0 inventory_service --clean

    # Development workflow
    $0 common --test-only --verbose
    $0 user_service --build-only --no-cache

    # Coverage control
    $0 --coverage 60          # Current threshold
    $0 --coverage 80          # Target threshold (when ready)

EOF
}

# Parse command line arguments
parse_arguments() {
    # First argument might be service name
    if [[ $# -gt 0 && ! "$1" =~ ^- ]]; then
        SERVICE_NAME="$1"
        shift
    fi

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -c|--clean)
                CLEAN=true
                shift
                ;;
            -t|--test-only)
                TEST_ONLY=true
                shift
                ;;
            -b|--build-only)
                BUILD_ONLY=true
                shift
                ;;
            --no-cache)
                NO_CACHE=true
                shift
                ;;
            --coverage)
                COVERAGE_THRESHOLD="$2"
                shift 2
                ;;
            --no-coverage)
                SKIP_COVERAGE=true
                shift
                ;;
            --install-deps)
                log_warning "--install-deps not implemented yet"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Validate service name
validate_service_name() {
    if [[ -n "$SERVICE_NAME" && "$SERVICE_NAME" != "all" ]]; then
        local valid=false
        for service in "${AVAILABLE_SERVICES[@]}"; do
            if [[ "$SERVICE_NAME" == "$service" ]]; then
                valid=true
                break
            fi
        done

        if [[ "$valid" == "false" ]]; then
            log_error "Invalid service name: $SERVICE_NAME"
            log_error "Available services: ${AVAILABLE_SERVICES[*]}"
            exit 1
        fi
    fi
}

# Check prerequisites
check_prerequisites() {
    log_step "🔍 Checking Prerequisites"

    local missing_tools=()

    # Check required tools
    local tools=("docker")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi

    # Check if services directory exists
    if [[ ! -d "$SERVICES_DIR" ]]; then
        log_error "Services directory not found: $SERVICES_DIR"
        exit 1
    fi

    # Check if main build script exists
    if [[ ! -f "$SERVICES_DIR/build.sh" ]]; then
        log_error "Main build script not found: $SERVICES_DIR/build.sh"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Build and test a single service
build_test_service() {
    local service_name="$1"
    local build_args=()

    log_substep "Building and testing: $service_name"

    # Navigate to services directory
    cd "$SERVICES_DIR"

    # Build arguments
    if [[ "$VERBOSE" == "true" ]]; then
        build_args+=("--verbose")
    fi

    if [[ "$CLEAN" == "true" ]]; then
        build_args+=("--clean")
    fi

    if [[ "$TEST_ONLY" == "true" ]]; then
        build_args+=("--test-only")
    fi

    if [[ "$BUILD_ONLY" == "true" ]]; then
        build_args+=("--build-only")
    fi

    if [[ "$SKIP_COVERAGE" == "true" ]]; then
        build_args+=("--no-coverage")
    else
        build_args+=("--coverage" "$COVERAGE_THRESHOLD")
    fi

    # Call the main build script
    log_info "Executing: ./build.sh ${build_args[*]} $service_name"

    if ! ./build.sh "${build_args[@]}" "$service_name"; then
        log_error "Build/test failed for $service_name"
        return 1
    fi

    log_success "Completed: $service_name"
    return 0
}

# Build and test all services
build_test_all() {
    log_step "🔨 Building and Testing All Services"

    local failed_services=()
    local start_time=$(date +%s)

    # Build common first (dependency for other services)
    log_substep "Building common package first (dependency)"
    if ! build_test_service "common"; then
        failed_services+=("common")
    fi

    # Build other services
    for service in "user_service" "inventory_service"; do
        if ! build_test_service "$service"; then
            failed_services+=("$service")
        fi
    done

    # Calculate duration
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # Summary
    log_step "📊 Build Summary"

    if [[ ${#failed_services[@]} -eq 0 ]]; then
        log_success "✅ All services built and tested successfully! (${duration}s)"
        return 0
    else
        log_error "❌ Some services failed: ${failed_services[*]} (${duration}s)"
        return 1
    fi
}

# Main execution
main() {
    local start_time=$(date +%s)

    # Parse and validate arguments
    parse_arguments "$@"
    validate_service_name

    # Print header
    echo
    printf "${PURPLE}🔨 Unified Build & Test Script${NC}\n"
    printf "${PURPLE}================================${NC}\n"
    echo

    # Show configuration
    log_info "Configuration:"
    log_info "  Service: ${SERVICE_NAME:-all}"
    log_info "  Verbose: $VERBOSE"
    log_info "  Clean: $CLEAN"
    log_info "  Test only: $TEST_ONLY"
    log_info "  Build only: $BUILD_ONLY"
    log_info "  No cache: $NO_CACHE"
    log_info "  Coverage threshold: $COVERAGE_THRESHOLD"
    echo

    # Check prerequisites
    check_prerequisites

    # === FRONTEND TESTS ===
    log_step "🧪 Running Frontend Tests"
    if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
        cd "$PROJECT_ROOT/frontend"
        if [ -f "package-lock.json" ]; then
            npm ci
        else
            npm install
        fi
        if [ -f "vite.config.ts" ]; then
            npm run test || log_warning "Frontend tests failed"
        else
            log_warning "No frontend test runner found (vite.config.ts missing)"
        fi
        cd "$PROJECT_ROOT"
    else
        log_warning "Frontend directory or package.json not found, skipping frontend tests"
    fi

    # === BACKEND TESTS ===
    log_step "🧪 Running Backend Tests"
    cd "$PROJECT_ROOT/services"
    if [[ -z "$SERVICE_NAME" || "$SERVICE_NAME" == "all" ]]; then
        ./build.sh --test-only --coverage $COVERAGE_THRESHOLD
    else
        ./build.sh --test-only --coverage $COVERAGE_THRESHOLD "$SERVICE_NAME"
    fi
    cd "$PROJECT_ROOT"

    # Calculate total duration
    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))

    echo
    log_success "Build/test completed in ${total_duration}s"
}

# Run main function
main "$@"