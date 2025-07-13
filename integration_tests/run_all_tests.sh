#!/bin/bash

# Simple script to run test cases with options
# Usage: ./run_all_tests.sh [all|smoke|inventory|user]

show_usage() {
    echo "Usage: $0 [all|smoke|inventory|user]"
    echo "  all       - Run all tests (default)"
    echo "  smoke     - Run only smoke tests"
    echo "  inventory - Run only inventory service tests"
    echo "  user      - Run only user service tests"
    echo ""
    echo "Examples:"
    echo "  $0          # Run all tests"
    echo "  $0 smoke    # Run only smoke tests"
    echo "  $0 inventory # Run only inventory tests"
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
    python3 user_services/user_tests.py
}

# Default to all tests if no argument provided
if [ $# -eq 0 ]; then
    ARG="all"
else
    ARG="$1"
fi

case $ARG in
    "all")
        echo "=== Running All Tests ==="
        run_smoke_tests
        run_inventory_tests
        run_user_tests
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
    *)
        echo "Error: Invalid argument '$ARG'"
        show_usage
        exit 1
        ;;
esac