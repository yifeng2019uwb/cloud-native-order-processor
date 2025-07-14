#!/bin/bash

# Simple script to run test cases with options
# Usage: ./run_all_tests.sh [all|smoke|inventory|user]

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

# Setup Kubernetes port forwarding
setup_k8s_port_forward() {
    echo "Setting up Kubernetes port forwarding..."

    # Check if services exist in order-processor namespace
    if kubectl get svc user-service -n order-processor >/dev/null 2>&1; then
        echo "✅ Kubernetes services detected, setting up port forwarding..."

        # Kill any existing port-forward processes
        pkill -f "kubectl port-forward" || true

        # Start port forwarding for user service
        kubectl port-forward svc/user-service 8000:8000 -n order-processor >/dev/null 2>&1 &
        USER_PF_PID=$!
        echo "   User service port-forward started (PID: $USER_PF_PID)"

        # Start port forwarding for inventory service
        kubectl port-forward svc/inventory-service 8001:8001 -n order-processor >/dev/null 2>&1 &
        INVENTORY_PF_PID=$!
        echo "   Inventory service port-forward started (PID: $INVENTORY_PF_PID)"

        # Wait a moment for port forwarding to establish
        sleep 2

        # Store PIDs for cleanup
        echo $USER_PF_PID > .user_pf_pid
        echo $INVENTORY_PF_PID > .inventory_pf_pid

        echo "✅ Port forwarding setup complete"
    else
        echo "⚠️  Kubernetes services not found, skipping port forwarding"
    fi
}

# Cleanup port forwarding
cleanup_port_forward() {
    echo "Cleaning up port forwarding..."

    # Kill port-forward processes if PID files exist
    if [ -f .user_pf_pid ]; then
        USER_PID=$(cat .user_pf_pid)
        kill $USER_PID 2>/dev/null || true
        rm -f .user_pf_pid
        echo "   User service port-forward stopped"
    fi

    if [ -f .inventory_pf_pid ]; then
        INVENTORY_PID=$(cat .inventory_pf_pid)
        kill $INVENTORY_PID 2>/dev/null || true
        rm -f .inventory_pf_pid
        echo "   Inventory service port-forward stopped"
    fi

    # Kill any remaining kubectl port-forward processes
    pkill -f "kubectl port-forward" 2>/dev/null || true
}

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

# Install prerequisites before running tests
install_prerequisites

# Setup Kubernetes port forwarding if services are available
setup_k8s_port_forward

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

# Cleanup port forwarding
cleanup_port_forward