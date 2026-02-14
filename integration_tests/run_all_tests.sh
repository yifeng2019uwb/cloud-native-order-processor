#!/bin/bash

# Simple script to run test cases with options
# Usage: ./run_all_tests.sh [all|smoke|inventory|user|order|load]

# Global exit code tracking
OVERALL_EXIT_CODE=0

# Install prerequisites
install_prerequisites() {
    echo "Installing prerequisites..."

    # Check if virtual environment exists, create if not
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment and install requirements
    echo "Activating virtual environment and installing requirements..."
    source venv/bin/activate
    pip install -r requirements.txt

    echo "Prerequisites installed successfully!"
}

show_usage() {
    echo "Usage: $0 [all|auth|smoke|inventory|user|order|insights]"
    echo "  all       - Run all tests (default)"
    echo "  auth      - Run only auth requirement tests"
    echo "  smoke     - Run only smoke tests"
    echo "  inventory - Run only inventory service tests"
    echo "  user      - Run only user service tests"
    echo "  order     - Run only order service tests"
    echo "  insights  - Run only insights service tests"
    echo ""
    echo "Examples:"
    echo "  $0          # Run all tests"
    echo "  $0 auth     # Run only auth tests"
    echo "  $0 smoke    # Run only smoke tests"
    echo "  $0 inventory # Run only inventory tests"
    echo "  $0 order    # Run only order service tests"
}

# Helper function to run tests and track exit codes
run_test_suite() {
    local test_name="$1"
    local test_command="$2"

    echo "Running $test_name..."
    eval "$test_command"
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

run_auth_tests() {
    run_test_suite "auth requirement tests" "python3 auth/test_gateway_auth.py"
}

run_smoke_tests() {
    run_test_suite "smoke tests" "python3 smoke/health_tests.py"
}

run_inventory_tests() {
    run_test_suite "inventory service tests" "python3 inventory_service/inventory_tests.py"
}

run_user_tests() {
    echo "=== Running User Service Tests ==="

    echo "=== Running User Service Auth Tests ==="
    run_test_suite "user registration tests" "python3 user_services/auth/registration_tests.py"
    run_test_suite "user login tests" "python3 user_services/auth/login_tests.py"
    run_test_suite "user profile tests" "python3 user_services/auth/profile_tests.py"
    run_test_suite "user logout tests" "python3 user_services/auth/logout_tests.py"

    echo "=== Running User Service Balance Tests ==="
    run_test_suite "user balance tests" "python3 user_services/balance/balance_tests.py"
    run_test_suite "user deposit tests" "python3 user_services/balance/deposit_tests.py"
    run_test_suite "user withdraw tests" "python3 user_services/balance/withdraw_tests.py"
    run_test_suite "user transaction history tests" "python3 user_services/balance/transaction_history_tests.py"

    echo "=== Running User Service Portfolio Tests ==="
    run_test_suite "user portfolio tests" "python3 user_services/portfolio/portfolio_tests.py"
    run_test_suite "user asset balance tests" "python3 user_services/portfolio/asset_balance_tests.py"
}

run_insights_tests() {
    echo "=== Running Insights Service Tests ==="
    run_test_suite "insights tests" "python3 user_services/insights/insights_tests.py"
}

run_order_tests() {
    echo "=== Running Order Service Tests ==="

    echo "=== Running Order Service Health Tests ==="
    run_test_suite "order health tests" "python3 order_service/health/health_tests.py"

    echo "=== Running Order Service Orders Tests ==="
    run_test_suite "order list tests" "python3 order_service/orders/list_order_tests.py"
    run_test_suite "order create tests" "python3 order_service/orders/create_order_tests.py"
    run_test_suite "order get tests" "python3 order_service/orders/get_order_tests.py"

    echo "=== Running Order Service Asset Transaction Tests ==="
    run_test_suite "order asset transaction tests" "python3 order_service/asset_transaction_tests.py"
}

run_load_tests() {
    echo "=== Running Load Tests ==="

    # Check if load tests directory exists
    if [ -d "load_tests" ]; then
        echo "Running load test suite..."
        cd load_tests
        chmod +x run_load_tests.sh
        ./run_load_tests.sh
        cd ..
    else
        echo "❌ Load tests directory not found"
        OVERALL_EXIT_CODE=1
    fi
}

# Default to all tests if no argument provided
if [ $# -eq 0 ]; then
    ARG="all"
else
    ARG="$1"
fi

# Install prerequisites before running tests
install_prerequisites

# Activate virtual environment for all test execution
echo "Activating virtual environment for test execution..."
source venv/bin/activate

case $ARG in
    "all")
        echo "=== Running All Tests ==="
        run_auth_tests
        run_smoke_tests
        run_inventory_tests
        run_user_tests
        run_order_tests
        run_insights_tests
        echo "=== All tests completed ==="
        ;;
    "auth")
        echo "=== Running Auth Tests ==="
        run_auth_tests
        echo "=== Auth tests completed ==="
        ;;
    "smoke")
        echo "=== Running Smoke Tests ==="
        run_smoke_tests
        echo "=== Smoke tests completed ==="
        ;;
    "inventory")
        echo "=== Running Inventory Tests ==="
        run_inventory_tests
        echo "=== Inventory tests completed ==="
        ;;
    "user")
        echo "=== Running User Tests ==="
        run_user_tests
        echo "=== User tests completed ==="
        ;;
    "order")
        echo "=== Running Order Tests ==="
        run_order_tests
        echo "=== Order tests completed ==="
        ;;
    "insights")
        echo "=== Running Insights Tests ==="
        run_insights_tests
        echo "=== Insights tests completed ==="
        ;;
    "load")
        echo "=== Running Load Tests ==="
        run_load_tests
        echo "=== Load tests completed ==="
        ;;
    *)
        echo "Error: Invalid argument '$ARG'"
        show_usage
        exit 1
        ;;
esac

# Final exit code check
if [ $OVERALL_EXIT_CODE -ne 0 ]; then
    echo "❌ Some tests failed. Overall exit code: $OVERALL_EXIT_CODE"
    exit $OVERALL_EXIT_CODE
else
    echo "🎉 All tests passed successfully!"
    exit 0
fi