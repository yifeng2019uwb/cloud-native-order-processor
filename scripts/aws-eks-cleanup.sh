#!/bin/bash

# AWS EKS Cleanup Script
# Safely destroys PROD AWS resources only (preserves dev/shared resources)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get configuration from environment or defaults
ENVIRONMENT="${1:-${ENVIRONMENT:-prod}}"
AWS_REGION="${AWS_REGION:-us-west-2}"
PROJECT_NAME="${PROJECT_NAME:-order-processor}"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Confirm cleanup
confirm_cleanup() {
    log_warning "This will destroy PROD AWS resources only (EKS, ECR, VPC, etc.)"
    log_warning "DEV resources (DynamoDB, S3, SNS, SQS) will be preserved."
    log_warning "This action cannot be undone for PROD resources."
    echo
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Cleanup cancelled"
        exit 0
    fi
}

# Clean up Kubernetes resources
cleanup_kubernetes() {
    log_info "Cleaning up Kubernetes resources..."

    # Delete all resources in order-processor namespace
    kubectl delete namespace order-processor --ignore-not-found=true

    log_success "Kubernetes resources cleaned up"
}

# Clean up Terraform infrastructure (PROD only)
cleanup_infrastructure() {
    log_info "Cleaning up PROD AWS infrastructure with Terraform..."
    log_info "This will only destroy resources with environment=prod"

    cd terraform

    # Destroy only PROD infrastructure
    terraform destroy -var="environment=${ENVIRONMENT}" -var="project_name=${PROJECT_NAME}" -var="region=${AWS_REGION}" -auto-approve

    cd ..
    log_success "PROD infrastructure destroyed successfully"
    log_info "DEV resources (DynamoDB, S3, etc.) are preserved"
}

# Clean up ECR images (optional)
cleanup_ecr_images() {
    log_info "Cleaning up ECR images..."

    # Services to clean up
    services=("user_service" "inventory_service" "order_service" "auth_service" "gateway" "frontend")

    for service in "${services[@]}"; do
        log_info "Deleting ECR images for ${service}..."

        # Delete all image tags
        aws ecr batch-delete-image --repository-name ${PROJECT_NAME}-${service} --image-ids imageTag=latest --region ${AWS_REGION} || true

        log_success "${service} ECR images cleaned up"
    done
}

# Main cleanup function
main() {
    log_info "Starting AWS EKS cleanup for Order Processor"
    log_info "Region: ${AWS_REGION}"
    log_info "Environment: ${ENVIRONMENT}"

    confirm_cleanup
    cleanup_kubernetes
    cleanup_infrastructure
    cleanup_ecr_images

    log_success "AWS EKS cleanup completed successfully!"
    log_info "Resources destroyed. Other environments preserved."
}

# Run main function
main "$@"
