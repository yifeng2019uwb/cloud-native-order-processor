#!/bin/bash

# Deploy to local Kubernetes (Kind) with STS role assumption
# This script gets the role ARN from Terraform and updates Kubernetes deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_step() {
    echo -e "${BLUE}🔧 $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "terraform/terraform.tfvars" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check prerequisites
print_step "Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

if ! command -v terraform &> /dev/null; then
    print_error "terraform is not installed or not in PATH"
    exit 1
fi

# Check if Kind cluster exists
if ! kubectl cluster-info &> /dev/null; then
    print_error "No Kubernetes cluster found. Please create a Kind cluster first:"
    print_info "  kind create cluster --name order-processor"
    exit 1
fi

# Check AWS credentials (using existing configuration)
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS credentials not configured. Please configure AWS CLI first:"
    print_info "  aws configure"
    exit 1
fi

print_success "Prerequisites check passed"

# Get Terraform outputs
print_step "Getting Terraform outputs..."

cd terraform

# Check if Terraform is initialized
if [ ! -d ".terraform" ]; then
    print_info "Initializing Terraform..."
    terraform init
fi

# Get outputs
print_info "Getting Terraform outputs..."
ROLE_ARN=$(terraform output -raw application_role_arn 2>/dev/null || echo "")
AWS_ACCOUNT_ID=$(terraform output -raw aws_account_id 2>/dev/null || echo "")
AWS_REGION=$(terraform output -raw aws_region 2>/dev/null || echo "")

cd ..

if [ -z "$ROLE_ARN" ] || [ -z "$AWS_ACCOUNT_ID" ]; then
    print_error "Failed to get Terraform outputs. Please run 'terraform apply' first."
    print_info "Expected outputs:"
    print_info "  - application_role_arn"
    print_info "  - aws_account_id"
    print_info "  - aws_region"
    exit 1
fi

print_success "Terraform outputs retrieved:"
print_info "  Role ARN: $ROLE_ARN"
print_info "  Account ID: $AWS_ACCOUNT_ID"
print_info "  Region: $AWS_REGION"

# Update Kubernetes deployment files
print_step "Updating Kubernetes deployment files..."

# Create a temporary deployment file with substituted values
TEMP_DEPLOYMENT=$(mktemp)
cat kubernetes/local/deployment.yaml | \
    sed "s|\${AWS_ACCOUNT_ID}|$AWS_ACCOUNT_ID|g" | \
    sed "s|\${AWS_REGION}|$AWS_REGION|g" > "$TEMP_DEPLOYMENT"

# Backup original deployment
cp kubernetes/local/deployment.yaml kubernetes/local/deployment.yaml.backup

# Replace with updated deployment
mv "$TEMP_DEPLOYMENT" kubernetes/local/deployment.yaml

print_success "Kubernetes deployment files updated"

# Apply base configuration
print_step "Applying base Kubernetes configuration..."
kubectl apply -k kubernetes/base

# Apply local configuration
print_step "Applying local Kubernetes configuration..."
kubectl apply -k kubernetes/local

# Wait for pods to be ready
print_step "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=order-processor -n order-processor --timeout=300s

# Show deployment status
print_step "Deployment status:"
kubectl get pods -n order-processor

print_success "✅ Local Kubernetes deployment complete!"

# Show access information
print_step "Access Information:"
print_info "Frontend: http://localhost:30000"
print_info "User Service: http://localhost:30001"
print_info "Inventory Service: http://localhost:30002"

print_info ""
print_info "🔐 AWS Configuration:"
print_info "  Role ARN: $ROLE_ARN"
print_info "  Account ID: $AWS_ACCOUNT_ID"
print_info "  Region: $AWS_REGION"
print_info "  Environment: local"
print_info "  Credentials: Using existing AWS configuration"

print_info ""
print_info "📋 Next Steps:"
print_info "  1. Run integration tests: ./scripts/test-local.sh"
print_info "  2. Check logs: kubectl logs -n order-processor -l app=order-processor"
print_info "  3. Access services at the URLs above"

print_success "🎉 Deployment successful! Your services are now using STS role assumption."