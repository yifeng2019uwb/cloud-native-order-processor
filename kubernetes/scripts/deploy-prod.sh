#!/bin/bash

# Deploy Order Processor to AWS EKS Production
# Usage: ./deploy-prod.sh

set -e

echo "🚀 Deploying Order Processor to AWS EKS Production..."

# Check required environment variables
if [ -z "$AWS_ACCOUNT_ID" ] || [ -z "$AWS_REGION" ]; then
    echo "❌ Required environment variables not set!"
    echo "Please set:"
    echo "  export AWS_ACCOUNT_ID='your-account-id'"
    echo "  export AWS_REGION='us-east-1'"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS CLI not configured!"
    echo "Please run: aws configure"
    exit 1
fi

# Check if EKS cluster exists
echo "🔍 Checking EKS cluster..."
if ! aws eks describe-cluster --name order-processor-prod --region $AWS_REGION >/dev/null 2>&1; then
    echo "❌ EKS cluster 'order-processor-prod' not found!"
    echo "Please create it first using Terraform or AWS CLI"
    exit 1
fi

# Update kubeconfig
echo "🔧 Updating kubeconfig..."
aws eks update-kubeconfig --name order-processor-prod --region $AWS_REGION

# Build Docker images
echo "📦 Building Docker images..."
cd ../docker
docker-compose -f docker-compose.dev.yml build
cd ../kubernetes

# Tag images for ECR
echo "🏷️  Tagging images for ECR..."
docker tag docker-user_service:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/order-processor-user-service:latest
docker tag docker-inventory_service:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/order-processor-inventory-service:latest
docker tag docker-frontend-dev:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/order-processor-frontend:latest

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Push images to ECR
echo "📤 Pushing images to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/order-processor-user-service:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/order-processor-inventory-service:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/order-processor-frontend:latest

# Check if secrets need to be updated
echo "🔐 Checking secrets configuration..."
if grep -q "<base64-encoded-production-access-key>" prod/secrets.yaml; then
    echo "⚠️  Please update prod/secrets.yaml with your production AWS credentials before deploying!"
    echo "   Run: echo -n 'your-production-access-key' | base64"
    echo "   Run: echo -n 'your-production-secret-key' | base64"
    echo "   Then update the secrets.yaml file"
    exit 1
fi

# Apply base configuration
echo "🔧 Applying base configuration..."
kubectl apply -k base

# Deploy to production cluster
echo "🚀 Deploying to production cluster..."
kubectl apply -k prod

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=600s deployment/user-service -n order-processor
kubectl wait --for=condition=available --timeout=600s deployment/inventory-service -n order-processor
kubectl wait --for=condition=available --timeout=600s deployment/frontend -n order-processor

# Wait for ingress to be ready
echo "⏳ Waiting for ingress to be ready..."
kubectl wait --for=condition=ready --timeout=300s ingress/order-processor-ingress -n order-processor

# Show deployment status
echo "📊 Deployment Status:"
kubectl get all -n order-processor

echo ""
echo "🌐 Ingress Status:"
kubectl get ingress -n order-processor

echo ""
echo "✅ Production deployment complete!"
echo ""
echo "📋 Useful Commands:"
echo "   kubectl get pods -n order-processor"
echo "   kubectl logs <pod-name> -n order-processor"
echo "   kubectl describe ingress order-processor-ingress -n order-processor"
echo ""
echo "🔍 Get Load Balancer URL:"
echo "   kubectl get ingress order-processor-ingress -n order-processor -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'"