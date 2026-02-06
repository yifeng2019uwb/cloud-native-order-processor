#!/bin/bash

# Run Load Tests
# Comprehensive load testing suite for security feature validation
# Usage: ./run_load_tests.sh [all|rate-limiting|circuit-breaker|lock-management|latency]

# Global exit code tracking
OVERALL_EXIT_CODE=0

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTEGRATION_TESTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Docker Compose configuration
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker/docker-compose.yml"
CIRCUIT_BREAKER_TEST_SERVICE="inventory_service" # Service to stop for circuit breaker testing
CIRCUIT_BREAKER_TIMEOUT=60 # Circuit breaker timeout in seconds (matches gateway config)
CIRCUIT_BREAKER_TIMEOUT=60 # Circuit breaker timeout in seconds (matches gateway config)

# Install prerequisites
install_prerequisites() {
    echo "📦 Installing prerequisites..."
    
    # Install Python dependencies (reuse integration_tests venv)
    if [ ! -d "$INTEGRATION_TESTS_DIR/venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv "$INTEGRATION_TESTS_DIR/venv"
    fi
    
    echo "Activating virtual environment and installing Python requirements..."
    source "$INTEGRATION_TESTS_DIR/venv/bin/activate"
    pip install -q -r "$INTEGRATION_TESTS_DIR/requirements.txt"
    
    # Install k6 dependencies
    echo "Installing k6 dependencies..."
    if [ -f "$SCRIPT_DIR/setup/install_dependencies.sh" ]; then
        chmod +x "$SCRIPT_DIR/setup/install_dependencies.sh"
        "$SCRIPT_DIR/setup/install_dependencies.sh"
        if [ $? -ne 0 ]; then
            echo "❌ k6 installation failed"
            return 1
        fi
    else
        echo "⚠️  install_dependencies.sh not found, skipping k6 installation"
    fi
    
    echo "✅ Prerequisites installed successfully!"
    return 0
}

# Create or update load test users
create_load_test_users() {
    echo "👤 Creating/updating load test users..."
    
    # Activate venv if not already activated
    if [ -z "$VIRTUAL_ENV" ]; then
        if [ -d "$INTEGRATION_TESTS_DIR/venv" ]; then
            source "$INTEGRATION_TESTS_DIR/venv/bin/activate"
        else
            echo "❌ Virtual environment not found. Run install_prerequisites first."
            return 1
        fi
    fi
    
    if [ -f "$SCRIPT_DIR/setup/create_load_test_users.py" ]; then
        python3 "$SCRIPT_DIR/setup/create_load_test_users.py"
        if [ $? -ne 0 ]; then
            echo "❌ Failed to create/update load test users"
            return 1
        fi
    else
        echo "❌ create_load_test_users.py not found"
        return 1
    fi
    
    echo "✅ Load test users ready!"
    return 0
}

# Helper function to ensure prerequisites are met before each test
ensure_prerequisites() {
    # Check if k6 is installed
    if ! command -v k6 &> /dev/null; then
        echo "⚠️  k6 not found. Installing dependencies..."
        install_prerequisites
        if [ $? -ne 0 ]; then
            echo "❌ Failed to install prerequisites"
            return 1
        fi
    fi
    
    # Always update/create load test users before each test
    # This ensures tokens are fresh and users exist
    echo "🔄 Ensuring load test users are ready..."
    create_load_test_users
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create/update load test users"
        return 1
    fi
    
    return 0
}

# Helper function to run k6 tests and track exit codes
run_k6_test() {
    local test_name="$1"
    local test_script="$2"
    
    echo "🧪 Running $test_name..."
    
    # Ensure prerequisites are met before each test
    ensure_prerequisites
    if [ $? -ne 0 ]; then
        echo "❌ Prerequisites check failed for $test_name"
        OVERALL_EXIT_CODE=1
        return 1
    fi
    
    # Ensure we're in the load_tests directory (k6 needs correct working directory)
    cd "$SCRIPT_DIR"
    
    if [ ! -f "$SCRIPT_DIR/k6/$test_script" ]; then
        echo "❌ Test script not found: k6/$test_script"
        OVERALL_EXIT_CODE=1
        return 1
    fi
    
    # Run k6 test (log file only - sufficient for personal project)
    k6 run "k6/$test_script" 2>&1 | tee "$RESULTS_DIR/${test_name}_${TIMESTAMP}.log"
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "❌ $test_name failed with exit code $exit_code"
        OVERALL_EXIT_CODE=$exit_code
        return $exit_code
    else
        echo "✅ $test_name completed successfully"
        return 0
    fi
}

show_usage() {
    echo "Usage: $0 [all|rate-limiting|circuit-breaker|lock-management|latency]"
    echo "  all              - Run all load tests (default)"
    echo "  rate-limiting    - Run rate limiting tests (TC-RL-001, TC-RL-002)"
    echo "  circuit-breaker  - Run circuit breaker tests (TC-CB-001, TC-CB-002)"
    echo "  lock-management  - Run lock management tests (TC-LOCK-001)"
    echo "  latency          - Run latency tests (TC-LATENCY-001)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 rate-limiting     # Run only rate limiting tests"
    echo "  $0 lock-management   # Run only lock management tests"
    echo ""
    echo "Note: Monitoring, audit-logs, and resilience tests are excluded/skipped for simplicity."
}

# Individual test functions
run_rate_limiting_tests() {
    run_k6_test "rate-limiting" "rate-limiting.js"
}

# Helper function to control Docker services for circuit breaker testing
stop_service_for_circuit_breaker() {
    local service_name="$1"
    echo "🛑 Stopping $service_name for circuit breaker test..."
    
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        echo "⚠️  docker-compose.yml not found at $DOCKER_COMPOSE_FILE"
        echo "   Skipping service stop - you may need to stop service manually"
        return 1
    fi
    
    cd "$PROJECT_ROOT/docker"
    docker-compose stop "$service_name" > /dev/null 2>&1
    local exit_code=$?
    cd "$SCRIPT_DIR"
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ Service $service_name stopped"
        return 0
    else
        echo "⚠️  Failed to stop $service_name (may not be running or wrong name)"
        return 1
    fi
}

start_service_for_circuit_breaker() {
    local service_name="$1"
    echo "▶️  Starting $service_name..."
    
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        echo "⚠️  docker-compose.yml not found at $DOCKER_COMPOSE_FILE"
        echo "   Skipping service start - you may need to start service manually"
        return 1
    fi
    
    cd "$PROJECT_ROOT/docker"
    docker-compose start "$service_name" > /dev/null 2>&1
    local exit_code=$?
    cd "$SCRIPT_DIR"
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ Service $service_name started"
        # Wait for service to be ready (health check)
        wait_for_service_ready "$service_name"
        return $?
    else
        echo "⚠️  Failed to start $service_name"
        return 1
    fi
}

wait_for_service_ready() {
    local service_name="$1"
    
    echo "⏳ Waiting for $service_name to be ready (backoff: 5s, 10s, 20s, then 30s intervals)..."
    
    # First check if container is running
    cd "$PROJECT_ROOT/docker"
    local container_status=$(docker-compose ps -q "$service_name" 2>/dev/null)
    if [ -z "$container_status" ]; then
        echo "⚠️  Container for $service_name not found"
        cd "$SCRIPT_DIR"
        return 1
    fi
    cd "$SCRIPT_DIR"
    
    # Exponential backoff initially, then fixed intervals for faster detection
    # Pattern: 5s, 10s, 20s (exponential), then 30s, 30s, 30s, 30s, 30s (fixed)
    local wait_times=(5 10 20 30 30 30 30 30)
    local attempt=1
    local total_wait=0
    local health_status=""
    local max_attempts=${#wait_times[@]}
    
    for wait_time in "${wait_times[@]}"; do
        echo "   Check attempt $attempt/$max_attempts: waiting ${wait_time}s (total waited: ${total_wait}s)..."
        sleep $wait_time
        total_wait=$((total_wait + wait_time))
        
        # Check container status
        cd "$PROJECT_ROOT/docker"
        health_status=$(docker inspect --format='{{.State.Status}}' "$container_status" 2>/dev/null)
        cd "$SCRIPT_DIR"
        
        if [ "$health_status" = "running" ]; then
            echo "✅ Service $service_name container is running (after ${total_wait}s)"
            echo "   Allowing additional 3 seconds for service initialization..."
            sleep 3
            return 0
        else
            echo "   Container status: ${health_status:-unknown}, continuing to wait..."
        fi
        
        attempt=$((attempt + 1))
    done
    
    echo "⚠️  Service $service_name did not become ready after ${total_wait}s (~3 minutes)"
    echo "   Container status: ${health_status:-unknown}"
    echo "   Proceeding anyway - service may still be starting"
    return 1
}

run_circuit_breaker_tests() {
    echo "🔌 Circuit Breaker Test - Automated Service Control"
    echo "=================================================="
    
    # Ensure prerequisites
    ensure_prerequisites
    if [ $? -ne 0 ]; then
        echo "❌ Prerequisites check failed for circuit breaker test"
        OVERALL_EXIT_CODE=1
        return 1
    fi
    
    # Phase 1: Stop service and test circuit breaker trip
    echo ""
    echo "📋 Phase 1: Testing Circuit Breaker Trip (TC-CB-001)"
    echo "---------------------------------------------------"
    
    stop_service_for_circuit_breaker "$CIRCUIT_BREAKER_TEST_SERVICE"
    
    echo "🧪 Running circuit breaker trip test..."
    cd "$SCRIPT_DIR"
    CIRCUIT_BREAKER_PHASE=trip k6 run "k6/circuit-breaker.js" 2>&1 | tee "$RESULTS_DIR/circuit-breaker-trip_${TIMESTAMP}.log"
    local trip_exit_code=$?
    
    if [ $trip_exit_code -ne 0 ]; then
        echo "❌ Circuit breaker trip test failed"
        OVERALL_EXIT_CODE=$trip_exit_code
        # Cleanup: Ensure service is started even if test failed
        echo ""
        echo "🧹 Cleanup: Starting service after test failure..."
        start_service_for_circuit_breaker "$CIRCUIT_BREAKER_TEST_SERVICE"
        return $trip_exit_code
    fi
    
    echo "✅ Circuit breaker trip test completed"
    
    # Wait for circuit breaker timeout (60 seconds)
    echo ""
    echo "⏳ Waiting ${CIRCUIT_BREAKER_TIMEOUT}s for circuit breaker timeout..."
    echo "   (Circuit breaker timeout period)"
    sleep ${CIRCUIT_BREAKER_TIMEOUT}
    echo "✅ Timeout complete - circuit breaker should be HALF-OPEN"
    
    # Phase 2: Start service and test circuit breaker recovery
    echo ""
    echo "📋 Phase 2: Testing Circuit Breaker Recovery (TC-CB-002)"
    echo "--------------------------------------------------------"
    
    start_service_for_circuit_breaker "$CIRCUIT_BREAKER_TEST_SERVICE"
    local service_start_exit_code=$?
    
    if [ $service_start_exit_code -ne 0 ]; then
        echo "⚠️  Service start had issues, but proceeding with recovery test..."
    fi
    
    # Additional wait to ensure service is fully initialized and circuit breaker can transition
    echo "⏳ Waiting additional 3 seconds for service to stabilize..."
    sleep 3
    
    echo "🧪 Running circuit breaker recovery test..."
    cd "$SCRIPT_DIR"
    CIRCUIT_BREAKER_PHASE=recover k6 run "k6/circuit-breaker.js" 2>&1 | tee "$RESULTS_DIR/circuit-breaker-recover_${TIMESTAMP}.log"
    local recover_exit_code=$?
    
    if [ $recover_exit_code -ne 0 ]; then
        echo "❌ Circuit breaker recovery test failed"
        OVERALL_EXIT_CODE=$recover_exit_code
        # Cleanup: Ensure service is started even if test failed
        echo ""
        echo "🧹 Cleanup: Ensuring service is running after test failure..."
        start_service_for_circuit_breaker "$CIRCUIT_BREAKER_TEST_SERVICE"
        return $recover_exit_code
    fi
    
    echo "✅ Circuit breaker recovery test completed"
    
    # Cleanup: Ensure service is running after test completes
    echo ""
    echo "🧹 Cleanup: Ensuring service is running..."
    start_service_for_circuit_breaker "$CIRCUIT_BREAKER_TEST_SERVICE"
    
    echo ""
    echo "✅ All circuit breaker tests completed successfully"
    return 0
}

run_lock_management_tests() {
    run_k6_test "lock-management" "lock-management.js"
}

run_latency_tests() {
    run_k6_test "latency" "latency.js"
}

# Main execution
main() {
    # Default to all tests if no argument provided
    if [ $# -eq 0 ]; then
        ARG="all"
    else
        ARG="$1"
    fi
    
    # Show usage if help requested
    if [ "$ARG" = "-h" ] || [ "$ARG" = "--help" ]; then
        show_usage
        exit 0
    fi
    
    echo "🚀 Order Processor Load Test Suite"
    echo "=================================="
    echo ""
    
    # Create results directory first
    mkdir -p "$RESULTS_DIR"
    echo "📁 Results will be saved to: $RESULTS_DIR"
    echo "⏰ Test run timestamp: $TIMESTAMP"
    echo ""
    
    # Note: Prerequisites and users will be ensured before each test
    # This allows individual tests to be run independently
    
    # Run tests based on argument
    case "$ARG" in
        "all")
            echo "=== Running All Load Tests ==="
            run_rate_limiting_tests
            run_circuit_breaker_tests
            run_lock_management_tests
            run_latency_tests
            ;;
        "rate-limiting")
            run_rate_limiting_tests
            ;;
        "circuit-breaker")
            run_circuit_breaker_tests
            ;;
        "lock-management")
            run_lock_management_tests
            ;;
        "latency")
            run_latency_tests
            ;;
        *)
            echo "❌ Unknown test suite: $ARG"
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    echo "📋 Load Test Summary"
    echo "==================="
    echo "📁 Results saved to: $RESULTS_DIR"
    
    if [ $OVERALL_EXIT_CODE -eq 0 ]; then
        echo "✅ All tests completed successfully"
        exit 0
    else
        echo "❌ Some tests failed (exit code: $OVERALL_EXIT_CODE)"
        exit $OVERALL_EXIT_CODE
    fi
}

# Run main function
main "$@"
