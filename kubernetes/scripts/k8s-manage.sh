#!/bin/bash
# kubernetes/scripts/k8s-manage.sh
# Simple Kubernetes Management Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${K8S_ROOT}/.." && pwd)"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Default values
ENVIRONMENT="dev"
SERVICE_NAME=""

show_usage() {
    echo "Usage: $0 {deploy|stop|status|port-forward} [--environment dev|prod] [--service name]"
    echo "  deploy       - Deploy all services to K8s"
    echo "  stop         - Stop all services"
    echo "  status       - Show service status"
    echo "  port-forward - Set up port forwarding for frontend (localhost:3000)"
    echo "  --environment dev|prod (default: dev)"
    echo "  --service name (optional: user, inventory, order, gateway, frontend)"
}

check_prerequisites() {
    if ! command -v kubectl &> /dev/null; then
        echo "❌ kubectl not found"
        exit 1
    fi

    if [[ "$ENVIRONMENT" == "dev" ]] && ! command -v kind &> /dev/null; then
        echo "❌ kind not found"
        exit 1
    fi
}

create_cluster() {
    if [[ "$ENVIRONMENT" == "dev" ]]; then
        if ! kind get clusters | grep -q "order-processor"; then
            echo "Creating Kind cluster..."
            kind create cluster --name order-processor --config "${K8S_ROOT}/kind-config.yaml"
        fi
    fi
}

build_images() {
    echo "🔨 Building Docker images..."

    cd "${PROJECT_ROOT}"

    # Build frontend
    echo "Building frontend..."
    docker build --no-cache -t order-processor-frontend:latest -f docker/frontend/Dockerfile .

    # Build services
    echo "Building user service..."
    docker build --no-cache -t order-processor-user_service:latest -f docker/user-service/Dockerfile .

    echo "Building inventory service..."
    docker build --no-cache -t order-processor-inventory_service:latest -f docker/inventory-service/Dockerfile .

    echo "Building order service..."
    docker build --no-cache -t order-processor-order_service:latest -f docker/order-service/Dockerfile .

    # Build gateway
    echo "Building gateway..."
    docker build --no-cache -t order-processor-gateway:latest -f docker/gateway/Dockerfile .

    echo "✅ Images built successfully"
}

load_images_to_kind() {
    if [[ "$ENVIRONMENT" == "dev" ]]; then
        echo "📦 Loading images to Kind cluster..."

        kind load docker-image order-processor-frontend:latest --name order-processor
        kind load docker-image order-processor-user_service:latest --name order-processor
        kind load docker-image order-processor-inventory_service:latest --name order-processor
        kind load docker-image order-processor-order_service:latest --name order-processor
        kind load docker-image order-processor-gateway:latest --name order-processor

        echo "✅ Images loaded to Kind cluster"
    fi
}

deploy() {
    echo "🚀 Deploying to Kubernetes..."

    check_prerequisites
    create_cluster
    build_images
    load_images_to_kind

    # Apply base configuration first
    echo "Applying base configuration..."
    kubectl apply -k "${K8S_ROOT}/base/"

    # Deploy environment-specific configuration
    cd "${K8S_ROOT}/${ENVIRONMENT}"
    kubectl apply -k .

    echo "✅ Deployment completed"
    echo "🔗 Frontend accessible at: http://localhost:30003"
    echo "🔗 Starting automatic port forwarding to localhost:3000..."

    # Start port forwarding in background
    kubectl port-forward -n order-processor service/frontend 3000:80 &
    PF_PID=$!
    echo "🔗 Port forwarding started (PID: $PF_PID)"
    echo "🔗 Frontend now accessible at: http://localhost:3000"
    echo "🔗 To stop port forwarding, run: kill $PF_PID"
}

stop() {
    echo "🛑 Stopping services..."

    # Stop any running port forwarding
    pkill -f "kubectl port-forward.*frontend" 2>/dev/null || true

    cd "${K8S_ROOT}/${ENVIRONMENT}"
    kubectl delete -k . --ignore-not-found=true

    echo "✅ Services stopped"
    echo "✅ Port forwarding stopped"
}

status() {
    echo "📊 Service Status:"
    kubectl get pods -n order-processor 2>/dev/null || echo "No pods found"
    kubectl get services -n order-processor 2>/dev/null || echo "No services found"
}

port_forward() {
    echo "🔗 Setting up port forwarding for frontend..."
    echo "Frontend will be accessible at: http://localhost:3000"
    echo "Press Ctrl+C to stop port forwarding"

    kubectl port-forward -n order-processor service/frontend 3000:80
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --service)
            SERVICE_NAME="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            COMMAND="$1"
            shift
            ;;
    esac
done

# Execute command
case "$COMMAND" in
    deploy)
        deploy
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    port-forward)
        port_forward
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
