#!/bin/bash

# Simple Terraform deployment script
# Usage: ./terraform-deploy.sh [environment]
# Environment variables: AWS_REGION, PROJECT_NAME

set -e

# Get configuration from environment or defaults
ENVIRONMENT="${1:-${ENVIRONMENT:-prod}}"
AWS_REGION="${AWS_REGION:-us-west-2}"
PROJECT_NAME="${PROJECT_NAME:-order-processor}"

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    echo "Deploying AWS infrastructure for environment: $ENVIRONMENT"
    echo "Region: $AWS_REGION"
    echo "Project: $PROJECT_NAME"

    cd terraform

    # Initialize Terraform
    terraform init

    # Apply deployment
    terraform apply -var="environment=${ENVIRONMENT}" -var="project_name=${PROJECT_NAME}" -var="region=${AWS_REGION}" -auto-approve

    cd ..
    echo "Infrastructure deployed successfully!"
}

# Run deployment
deploy_infrastructure
