#!/bin/bash

# Deploy Order Processor to Local Kubernetes (Kind)
# Usage: ./deploy-local.sh

set -e

echo "🚀 Deploying Order Processor to Local Kubernetes (Kind)..."

# Check if Kind cluster exists
if ! kind get clusters | grep -q "order-processor"; then
    echo "❌ Kind cluster 'order-processor' not found!"
    echo "Please create it first: kind create cluster --name order-processor"
    exit 1
fi

# Check if kubectl is configured for the cluster
if ! kubectl cluster-info --context kind-order-processor >/dev/null 2>&1; then
    echo "❌ kubectl not configured for kind-order-processor cluster!"
    exit 1
fi

# Build Docker images
echo "📦 Building Docker images..."
cd ../docker
docker-compose -f docker-compose.dev.yml build
cd ../kubernetes

# Load images into Kind cluster
echo "📥 Loading images into Kind cluster..."
kind load docker-image order-processor-user_service:latest --name order-processor
kind load docker-image order-processor-inventory_service:latest --name order-processor
kind load docker-image order-processor-frontend:latest --name order-processor

# Apply base configuration
echo "🔧 Applying base configuration..."
kubectl apply -k base

# Check if secrets need to be updated
echo "🔐 Checking secrets configuration..."
if grep -q "<base64-encoded-access-key>" local/secrets.yaml; then
    echo "⚠️  Please update local/secrets.yaml with your AWS credentials before deploying!"
    echo "   Run: echo -n 'your-access-key' | base64"
    echo "   Run: echo -n 'your-secret-key' | base64"
    echo "   Then update the secrets.yaml file"
    exit 1
fi

# Deploy to local cluster
echo "🚀 Deploying to local cluster..."
kubectl apply -k local

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/user-service -n order-processor
kubectl wait --for=condition=available --timeout=300s deployment/inventory-service -n order-processor
kubectl wait --for=condition=available --timeout=300s deployment/frontend -n order-processor

# Show deployment status
echo "📊 Deployment Status:"
kubectl get all -n order-processor

echo ""
echo "✅ Local deployment complete!"
echo ""
echo "🌐 Access Points:"
echo "   Frontend: http://localhost:30000"
echo "   User Service: http://localhost:30001"
echo "   Inventory Service: http://localhost:30002"
echo ""
echo "📋 Useful Commands:"
echo "   kubectl get pods -n order-processor"
echo "   kubectl logs <pod-name> -n order-processor"
echo "   kubectl describe pod <pod-name> -n order-processor"