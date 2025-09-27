#!/bin/bash
# terraform/apply.sh
# Comprehensive Terraform apply script for Order Processor

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get environment from argument or default to prod
ENVIRONMENT=${1:-prod}
PROJECT_NAME=${2:-order-processor}
AWS_REGION=${3:-us-west-2}

log_info "Starting Terraform apply for environment: $ENVIRONMENT"

# Step 1: Initialize Terraform
log_info "Step 1: Initializing Terraform..."
terraform init

# Step 2: Validate configuration
log_info "Step 2: Validating Terraform configuration..."
terraform validate

# Step 3: Plan deployment
log_info "Step 3: Planning Terraform deployment..."
terraform plan \
    -var="environment=$ENVIRONMENT" \
    -var="project_name=$PROJECT_NAME" \
    -var="region=$AWS_REGION"

# Step 4: Apply deployment
log_info "Step 4: Applying Terraform configuration..."
terraform apply \
    -var="environment=$ENVIRONMENT" \
    -var="project_name=$PROJECT_NAME" \
    -var="region=$AWS_REGION" \
    -auto-approve

# Step 5: Display outputs
log_info "Step 5: Displaying Terraform outputs..."
terraform output

log_success "Terraform apply completed successfully!"
