#!/bin/bash

# ECR Build and Push Script for Order Processor
# This script builds Docker images and pushes them to your ECR repository

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Configuration - Update these based on your Terraform outputs
AWS_REGION="us-west-2"  # Update to match your region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

if [ -z "$AWS_ACCOUNT_ID" ]; then
    print_error "Failed to get AWS Account ID. Ensure AWS CLI is configured."
    exit 1
fi

ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_REPOSITORY="order-processor-dev"  # From your Terraform

print_status "Starting Docker build and push process..."
print_status "AWS Account ID: $AWS_ACCOUNT_ID"
print_status "ECR Registry: $ECR_REGISTRY"
print_status "ECR Repository: $ECR_REPOSITORY"

# Step 1: Login to ECR
print_status "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

if [ $? -eq 0 ]; then
    print_success "Successfully logged into ECR"
else
    print_error "Failed to login to ECR"
    exit 1
fi

# Step 2: Create ECR repository if it doesn't exist
print_status "Ensuring ECR repository exists..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION > /dev/null 2>&1 || {
    print_warning "Repository $ECR_REPOSITORY not found, creating..."
    aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION
    print_success "Created ECR repository: $ECR_REPOSITORY"
}

# Step 3: Build and push services
# Get current timestamp for tagging
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "local")

build_and_push_service() {
    local service_name=$1
    local dockerfile_path=$2
    local context_path=$3

    print_status "Building $service_name..."

    # Create tags
    local image_name="$ECR_REGISTRY/$ECR_REPOSITORY:$service_name-latest"
    local image_name_timestamped="$ECR_REGISTRY/$ECR_REPOSITORY:$service_name-$TIMESTAMP"
    local image_name_commit="$ECR_REGISTRY/$ECR_REPOSITORY:$service_name-$COMMIT_SHA"

    # Build the Docker image
    if docker build -f "$dockerfile_path" -t "$image_name" -t "$image_name_timestamped" -t "$image_name_commit" "$context_path"; then
        print_success "Successfully built $service_name"

        # Push all tags
        print_status "Pushing $service_name to ECR..."
        docker push "$image_name"
        docker push "$image_name_timestamped"
        docker push "$image_name_commit"

        print_success "Successfully pushed $service_name to ECR"
        print_status "Available tags for $service_name:"
        print_status "  - $service_name-latest"
        print_status "  - $service_name-$TIMESTAMP"
        print_status "  - $service_name-$COMMIT_SHA"
    else
        print_error "Failed to build $service_name"
        return 1
    fi
}

# Build Order Service
print_status "=== Building Order Service ==="
build_and_push_service "order-service" "docker/order-service/Dockerfile" "."

# Build Frontend (if you want to containerize it)
print_status "=== Building Frontend ==="
build_and_push_service "frontend" "docker/frontend/Dockerfile" "docker/frontend"

# Optional: Build other services if they have proper Dockerfiles
# Uncomment and modify these as you implement other services

# print_status "=== Building Inventory Service ==="
# build_and_push_service "inventory_service" "docker/inventory_service/Dockerfile" "."

# print_status "=== Building Payment Service ==="
# build_and_push_service "payment-service" "docker/payment-service/Dockerfile" "."

# print_status "=== Building Notification Service ==="
# build_and_push_service "notification-service" "docker/notification-service/Dockerfile" "."

# Step 4: List all images in ECR
print_status "=== ECR Repository Contents ==="
aws ecr list-images --repository-name $ECR_REPOSITORY --region $AWS_REGION --output table

# Step 5: Clean up local Docker images (optional)
read -p "Clean up local Docker images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Cleaning up local Docker images..."
    docker image prune -f
    print_success "Local Docker cleanup completed"
fi

print_success "=== Build and Push Process Completed! ==="
print_status "Your images are now available in ECR at:"
print_status "  $ECR_REGISTRY/$ECR_REPOSITORY"
print_status ""
print_status "Next steps:"
print_status "1. Update your Kubernetes manifests to use these image URIs"
print_status "2. Deploy to your EKS cluster"
print_status "3. Test your applications"