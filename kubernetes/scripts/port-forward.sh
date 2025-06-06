#!/bin/bash

# scripts/port-forward.sh - Port forward services for local development

set -e

NAMESPACE=${NAMESPACE:-order-processor}

echo "🔗 Setting up port forwarding for Order Processing System..."
echo "📦 Namespace: $NAMESPACE"

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
    echo "❌ Namespace '$NAMESPACE' does not exist"
    echo "   Deploy first with: make deploy"
    exit 1
fi

# Function to check if service exists
check_service() {
    local service=$1
    if ! kubectl get service "$service" -n "$NAMESPACE" >/dev/null 2>&1; then
        echo "⚠️  Service '$service' not found in namespace '$NAMESPACE'"
        return 1
    fi
    return 0
}

# Function to start port forwarding in background
start_port_forward() {
    local service=$1
    local local_port=$2
    local remote_port=$3
    local name=$4
    
    if check_service "$service"; then
        echo "🚀 Starting port forward: $name (localhost:$local_port -> $service:$remote_port)"
        kubectl port-forward "svc/$service" "$local_port:$remote_port" -n "$NAMESPACE" > "/tmp/pf-$service.log" 2>&1 &
        local pid=$!
        echo "$pid" > "/tmp/pf-$service.pid"
        echo "   PID: $pid"
    fi
}

# Kill existing port forwards
echo "🛑 Stopping existing port forwards..."
pkill -f "kubectl port-forward" || true
rm -f /tmp/pf-*.pid /tmp/pf-*.log

echo ""
echo "🚀 Starting port forwards..."

# Start port forwarding for each service
start_port_forward "order-api" 5000 5000 "Order API"