#!/bin/bash

# kubernetes/scripts/deploy-dev.sh
# Usage: ./deploy-dev.sh

set -e

echo "🚀 Deploying Order Processor to Local Kubernetes (Kind)..."

# Check if Kind cluster exists, create multi-node if not
if ! kind get clusters | grep -q "order-processor"; then
    echo "❌ Kind cluster 'order-processor' not found!"
    echo "🔧 Creating multi-node Kind cluster 'order-processor'..."
    kind create cluster --name order-processor --config ../kind-config.yaml
    echo "✅ Multi-node Kind cluster created successfully!"
else
    echo "✅ Kind cluster 'order-processor' already exists"
fi

# Check if kubectl is configured for the cluster
if ! kubectl cluster-info --context kind-order-processor >/dev/null 2>&1; then
    echo "❌ kubectl not configured for kind-order-processor cluster!"
    exit 1
fi

# Update AWS credentials from Terraform outputs
echo "🔐 Updating AWS credentials from Terraform outputs..."
./setup-aws-credentials.sh

# Build Docker images with cache cleanup
echo "📦 Building Docker images (with cache cleanup)..."
cd ../../docker

# Remove old images to ensure fresh builds
echo "🧹 Cleaning up old images..."
docker rmi order-processor-user_service:latest order-processor-inventory_service:latest order-processor-frontend:latest 2>/dev/null || true

# Build with no cache to ensure fresh builds
echo "🔨 Building images with --no-cache..."
docker-compose -f docker-compose.dev.yml build --no-cache

cd ../kubernetes

# Load images into Kind cluster
echo "📥 Loading images into Kind cluster..."
kind load docker-image order-processor-user_service:latest --name order-processor
kind load docker-image order-processor-inventory_service:latest --name order-processor
kind load docker-image order-processor-frontend:latest --name order-processor

# Apply base configuration
echo "🔧 Applying base configuration..."
kubectl apply -k base

# Deploy to local cluster
echo "🚀 Deploying to local cluster..."
kubectl apply -k dev

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