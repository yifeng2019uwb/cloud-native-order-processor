#!/bin/bash

# EKS Deployment Script for Order Processor
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
CLUSTER_NAME="order-processor-dev"
AWS_REGION="us-west-2"
NAMESPACE="order-processor"

print_status "🚀 Starting EKS Deployment for Order Processor"
print_status "=============================================="

# Step 1: Update kubeconfig
print_status "📋 Updating kubeconfig for EKS cluster..."
aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME

if [ $? -eq 0 ]; then
    print_success "Successfully connected to EKS cluster: $CLUSTER_NAME"
else
    print_error "Failed to connect to EKS cluster"
    exit 1
fi

# Step 2: Verify cluster access
print_status "🔍 Verifying cluster access..."
kubectl cluster-info
kubectl get nodes

# Step 3: Install AWS Load Balancer Controller (if not already installed)
print_status "⚖️ Checking AWS Load Balancer Controller..."
if ! kubectl get deployment -n kube-system aws-load-balancer-controller &>/dev/null; then
    print_warning "AWS Load Balancer Controller not found. Installing..."

    # Download IAM policy
    curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.7.2/docs/install/iam_policy.json

    # Create IAM policy
    aws iam create-policy \
        --policy-name AWSLoadBalancerControllerIAMPolicy \
        --policy-document file://iam_policy.json || true

    # Create service account
    eksctl create iamserviceaccount \
        --cluster=$CLUSTER_NAME \
        --namespace=kube-system \
        --name=aws-load-balancer-controller \
        --role-name AmazonEKSLoadBalancerControllerRole \
        --attach-policy-arn=arn:aws:iam::940482447349:policy/AWSLoadBalancerControllerIAMPolicy \
        --approve

    # Install controller using Helm
    helm repo add eks https://aws.github.io/eks-charts
    helm repo update
    helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
        -n kube-system \
        --set clusterName=$CLUSTER_NAME \
        --set serviceAccount.create=false \
        --set serviceAccount.name=aws-load-balancer-controller

    print_success "AWS Load Balancer Controller installed"
else
    print_success "AWS Load Balancer Controller already installed"
fi

# Step 4: Install AWS Secrets Store CSI Driver (if not already installed)
print_status "🔐 Checking AWS Secrets Store CSI Driver..."
if ! kubectl get daemonset -n kube-system secrets-store-csi-driver &>/dev/null; then
    print_warning "Secrets Store CSI Driver not found. Installing..."

    # Install Secrets Store CSI Driver
    helm repo add secrets-store-csi-driver https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts
    helm install csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver --namespace kube-system

    # Install AWS Provider
    kubectl apply -f https://raw.githubusercontent.com/aws/secrets-store-csi-driver-provider-aws/main/deployment/aws-provider-installer.yaml

    print_success "Secrets Store CSI Driver installed"
else
    print_success "Secrets Store CSI Driver already installed"
fi

# Step 5: Generate dynamic configuration from Terraform outputs
print_status "🔧 Generating configuration from Terraform outputs..."
./scripts/generate-k8s-config.sh

# Step 6: Create namespace
print_status "📁 Creating namespace: $NAMESPACE"
kubectl apply -f kubernetes/namespace.yaml

# Step 7: Apply service account and RBAC (generated)
print_status "👤 Creating service account and RBAC..."
kubectl apply -f kubernetes/service-account-generated.yaml

# Step 8: Apply secrets and config (generated)
print_status "🔐 Creating secrets and configuration..."
kubectl apply -f kubernetes/secrets-config-generated.yaml

# Step 8: Apply deployment
print_status "🚀 Deploying order service..."
kubectl apply -f kubernetes/deployment.yaml

# Step 9: Apply service and ingress
print_status "🌐 Creating service and ingress..."
kubectl apply -f kubernetes/service-ingress.yaml

# Step 10: Wait for deployment to be ready
print_status "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/order-service -n $NAMESPACE

# Step 11: Get status
print_status "📊 Deployment Status"
print_status "==================="
kubectl get all -n $NAMESPACE

# Step 12: Get Load Balancer URL
print_status "🌍 Getting Load Balancer URL..."
sleep 30  # Wait for load balancer to be provisioned

LB_URL=$(kubectl get ingress order-service-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

if [ -n "$LB_URL" ]; then
    print_success "🎉 Deployment completed successfully!"
    print_success "Your application is available at: http://$LB_URL"
    print_status "Health check: http://$LB_URL/health"
    print_status "API docs: http://$LB_URL/docs"
else
    print_warning "Load balancer URL not yet available. Check in a few minutes:"
    print_status "kubectl get ingress order-service-ingress -n $NAMESPACE"
fi

print_status ""
print_status "🔧 Useful commands:"
print_status "==================="
print_status "View pods:           kubectl get pods -n $NAMESPACE"
print_status "View logs:           kubectl logs -f deployment/order-service -n $NAMESPACE"
print_status "Describe deployment: kubectl describe deployment order-service -n $NAMESPACE"
print_status "Port forward:        kubectl port-forward service/order-service 8080:80 -n $NAMESPACE"
print_status ""
print_success "🎯 Deployment completed!"