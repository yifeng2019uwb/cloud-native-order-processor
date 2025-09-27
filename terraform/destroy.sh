#!/bin/bash
# terraform/destroy.sh
# Comprehensive Terraform destroy script that handles AWS dependencies

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

log_info "Starting Terraform destroy for environment: $ENVIRONMENT"

# Step 1: Delete LoadBalancers first (they have network interface dependencies)
log_info "Step 1: Deleting LoadBalancers..."
aws elbv2 describe-load-balancers --query 'LoadBalancers[?contains(LoadBalancerName, `order-processor`) || contains(LoadBalancerName, `prod`)].LoadBalancerArn' --output text | while read lb_arn; do
    if [ ! -z "$lb_arn" ]; then
        log_info "Deleting LoadBalancer: $lb_arn"
        aws elbv2 delete-load-balancer --load-balancer-arn "$lb_arn"
    fi
done

# Step 2: Wait for LoadBalancer network interfaces to be released
log_info "Step 2: Waiting for LoadBalancer dependencies to clear..."
sleep 60

# Step 3: Delete ECR repositories with force (if they contain images)
log_info "Step 3: Deleting ECR repositories..."
aws ecr describe-repositories --query 'repositories[?contains(repositoryName, `order-processor`)].repositoryName' --output text | while read repo_name; do
    if [ ! -z "$repo_name" ]; then
        log_info "Deleting ECR repository: $repo_name"
        aws ecr delete-repository --repository-name "$repo_name" --force 2>/dev/null || true
    fi
done

# Step 4: Run Terraform destroy
log_info "Step 4: Running Terraform destroy..."
terraform destroy \
    -var="environment=$ENVIRONMENT" \
    -var="project_name=$PROJECT_NAME" \
    -var="region=$AWS_REGION" \
    -auto-approve

# Step 5: Verify cleanup
log_info "Step 5: Verifying cleanup..."
remaining_vpcs=$(aws ec2 describe-vpcs --filters "Name=tag:Project,Values=$PROJECT_NAME" --query 'Vpcs[*].VpcId' --output text)
remaining_repos=$(aws ecr describe-repositories --query 'repositories[?contains(repositoryName, `order-processor`)].repositoryName' --output text)

if [ -z "$remaining_vpcs" ] && [ -z "$remaining_repos" ]; then
    log_success "All resources successfully destroyed!"
else
    log_error "Some resources may still exist:"
    [ ! -z "$remaining_vpcs" ] && echo "VPCs: $remaining_vpcs"
    [ ! -z "$remaining_repos" ] && echo "ECR repos: $remaining_repos"
fi

log_success "Terraform destroy completed!"
