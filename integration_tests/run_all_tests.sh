#!/bin/bash

# Simple script to run test cases with options
# Usage: ./run_all_tests.sh [all|smoke|inventory|user|order]

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
    echo "Usage: $0 [all|smoke|inventory|user|order]"
    echo "  all       - Run all tests (default)"
    echo "  smoke     - Run only smoke tests"
    echo "  inventory - Run only inventory service tests"
    echo "  user      - Run only user service tests"
    echo "  order     - Run only order service tests"
    echo ""
    echo "Examples:"
    echo "  $0          # Run all tests"
    echo "  $0 smoke    # Run only smoke tests"
    echo "  $0 inventory # Run only inventory tests"
    echo "  $0 order    # Run only order service tests"
}

run_smoke_tests() {
    echo "Running smoke tests..."
    python3 smoke/health_tests.py
}

run_inventory_tests() {
    echo "Running inventory service tests..."
    python3 inventory_service/inventory_tests.py
}

run_user_tests() {
    echo "Running user service tests..."
    echo "=== Running User Service Auth Tests ==="
    python3 user_services/auth/registration_tests.py
    python3 user_services/auth/login_tests.py
    python3 user_services/auth/profile_tests.py
    python3 user_services/auth/logout_tests.py
    echo "=== Running User Service Balance Tests ==="
    python3 user_services/balance/balance_tests.py
    python3 user_services/balance/deposit_tests.py
    python3 user_services/balance/withdraw_tests.py
    python3 user_services/balance/transaction_history_tests.py
}

run_order_tests() {
    echo "Running order service tests..."
    echo "=== Running Order Service Health Tests ==="
    python3 order_service/health/health_tests.py
    echo "=== Running Order Service Orders Tests ==="
    python3 order_service/orders/list_order_tests.py
    python3 order_service/orders/create_order_tests.py
    python3 order_service/orders/get_order_tests.py
    echo "=== Running Order Service Portfolio Tests ==="
    python3 order_service/portfolio_tests.py
    echo "=== Running Order Service Asset Balance Tests ==="
    python3 order_service/asset_balance_tests.py
    echo "=== Running Order Service Asset Transaction Tests ==="
    python3 order_service/asset_transaction_tests.py
}

# Default to all tests if no argument provided
if [ $# -eq 0 ]; then
    ARG="all"
else
    ARG="$1"
fi

# Install prerequisites before running tests
install_prerequisites

case $ARG in
    "all")
        echo "=== Running All Tests ==="
        run_smoke_tests
        run_inventory_tests
        run_user_tests
        run_order_tests
        echo "=== All tests completed ==="
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
    *)
        echo "Error: Invalid argument '$ARG'"
        show_usage
        exit 1
        ;;
esac