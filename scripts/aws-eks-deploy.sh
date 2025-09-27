#!/bin/bash

# AWS EKS Deployment Script
# Deploys the Order Processor to AWS EKS with full automation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"
AWS_REGION="us-west-2"
PROJECT_NAME="order-processor"
ENVIRONMENT="prod"
CLUSTER_NAME="${PROJECT_NAME}-${ENVIRONMENT}-cluster"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed"
        exit 1
    fi

    log_success "All prerequisites met"
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    log_info "Deploying AWS infrastructure with Terraform..."

    cd terraform
    # Use the comprehensive apply script
    ./apply.sh ${ENVIRONMENT} ${PROJECT_NAME} ${AWS_REGION}
    cd ..

    log_success "Infrastructure deployed successfully"
}

# Build and push Docker images to ECR
build_and_push_specific_images() {
    local services=("$@")
    log_info "Building and pushing specific Docker images to ECR..."

    # Get ECR login token
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

    for service in "${services[@]}"; do
        log_info "Building and pushing ${service}..."

        # Build and push directly to ECR using buildx (no local images needed)
        docker buildx build --platform linux/amd64 \
          -t ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-prod-${service}:latest \
          -f docker/${service}/Dockerfile \
          --push .

        log_success "${service} pushed to ECR"
    done
}

build_and_push_images() {
    log_info "Building and pushing all Docker images to ECR..."

    # Get ECR login token
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

    # Services to build
    services=("user-service" "inventory-service" "order-service" "auth-service" "gateway" "frontend")

    for service in "${services[@]}"; do
        log_info "Building and pushing ${service}..."

        # Build and push directly to ECR using buildx (no local images needed)
        docker buildx build --platform linux/amd64 \
          -t ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-prod-${service}:latest \
          -f docker/${service}/Dockerfile \
          --push .

        log_success "${service} pushed to ECR"
    done
}

# Configure kubectl for EKS
configure_kubectl() {
    log_info "Configuring kubectl for EKS cluster..."

    aws eks update-kubeconfig --region ${AWS_REGION} --name ${CLUSTER_NAME}

    log_success "kubectl configured for EKS cluster"
}

# Deploy to Kubernetes
deploy_to_kubernetes() {
    log_info "Deploying services to Kubernetes..."

    # Set environment variables for kustomize
    export AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}
    export AWS_REGION=${AWS_REGION}
    export IMAGE_TAG=${IMAGE_TAG:-latest}

    # Create ECR registry secret for image pulling
    log_info "Creating ECR registry secret..."
    kubectl create secret docker-registry ecr-registry-secret \
        --docker-server=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com \
        --docker-username=AWS \
        --docker-password=$(aws ecr get-login-password --region ${AWS_REGION}) \
        --namespace=order-processor \
        --dry-run=client -o yaml | kubectl apply -f -

    # Create app secrets (JWT secret and Redis endpoint)
    log_info "Creating app secrets..."
    # Get Redis endpoint from Terraform output
    REDIS_ENDPOINT=$(cd terraform && terraform output -raw redis_endpoint)
    # Get JWT secret from environment or generate a random one
    JWT_SECRET="${JWT_SECRET:-$(openssl rand -base64 32)}"

    kubectl create secret generic app-secrets \
        --from-literal=jwt-secret="${JWT_SECRET}" \
        --from-literal=redis-endpoint="${REDIS_ENDPOINT}" \
        --namespace=order-processor \
        --dry-run=client -o yaml | kubectl apply -f -

    # Deploy to production namespace using envsubst for variable substitution
    log_info "Substituting environment variables in kustomization..."
    mkdir -p /tmp/k8s
    cp -r kubernetes/base /tmp/k8s/
    cp -r kubernetes/prod/* /tmp/k8s/
    # Update the base path in kustomization
    sed 's|../base|./base|g' kubernetes/prod/kustomization.yaml | envsubst > /tmp/k8s/kustomization.yaml
    kubectl apply -k /tmp/k8s/

    # Wait for deployments to be ready
    log_info "Waiting for deployments to be ready..."
    kubectl rollout status deployment/user-service -n order-processor --timeout=300s
    kubectl rollout status deployment/inventory-service -n order-processor --timeout=300s
    kubectl rollout status deployment/order-service -n order-processor --timeout=300s
    kubectl rollout status deployment/auth-service -n order-processor --timeout=300s
    kubectl rollout status deployment/gateway -n order-processor --timeout=300s

    log_success "All services deployed successfully"
}

# Get service endpoints
get_endpoints() {
    log_info "Getting service endpoints..."

    # Get LoadBalancer endpoints
    kubectl get services -n order-processor

    # Get ingress endpoints
    kubectl get ingress -n order-processor

    log_success "Service endpoints retrieved"
}

# Main deployment function
main() {
    log_info "Starting AWS EKS deployment for Order Processor"
    log_info "Account: ${AWS_ACCOUNT_ID}"
    log_info "Region: ${AWS_REGION}"
    log_info "Cluster: ${CLUSTER_NAME}"

    check_prerequisites
    deploy_infrastructure
    build_and_push_images
    configure_kubectl
    deploy_to_kubernetes
    get_endpoints

    log_success "AWS EKS deployment completed successfully!"
    log_info "You can now run integration tests against the AWS deployment"
}

# Infrastructure only deployment
deploy_infrastructure_only() {
    log_info "Deploying AWS infrastructure only..."
    check_prerequisites
    deploy_infrastructure
    log_success "AWS infrastructure deployed successfully!"
    log_info "Next steps:"
    log_info "1. Run: ./scripts/aws-eks-deploy.sh --images-only"
    log_info "2. Run: ./scripts/aws-eks-deploy.sh --k8s-only"
}

# Destroy infrastructure
destroy_infrastructure() {
    log_info "Destroying AWS infrastructure..."
    check_prerequisites

    cd terraform
    # Use the comprehensive destroy script
    ./destroy.sh ${ENVIRONMENT} ${PROJECT_NAME} ${AWS_REGION}
    cd ..

    log_success "AWS infrastructure destroyed successfully!"
}

# Images only deployment
deploy_images_only() {
    log_info "Building and pushing Docker images only..."
    check_prerequisites
    build_and_push_images
    log_success "Docker images pushed successfully!"
}

# Specific images deployment
deploy_specific_images() {
    local services=("$@")
    log_info "Building and pushing specific Docker images..."
    check_prerequisites
    build_and_push_specific_images "${services[@]}"
    log_success "Specific Docker images pushed successfully!"
}

# Kubernetes only deployment
deploy_k8s_only() {
    log_info "Deploying to Kubernetes only..."
    check_prerequisites
    configure_kubectl
    deploy_to_kubernetes
    get_endpoints
    log_success "Kubernetes deployment completed successfully!"
}

# Parse command line arguments
case "${1:-}" in
    --infrastructure-only)
        deploy_infrastructure_only
        ;;
    --images-only)
        deploy_images_only
        ;;
    --k8s-only)
        deploy_k8s_only
        ;;
    --services)
        shift
        deploy_specific_images "$@"
        ;;
    --destroy)
        destroy_infrastructure
        ;;
    --help|-h)
        echo "Usage: $0 [OPTION] [SERVICES...]"
        echo "Options:"
        echo "  --infrastructure-only    Deploy AWS infrastructure only (Terraform)"
        echo "  --images-only           Build and push Docker images only"
        echo "  --k8s-only              Deploy to Kubernetes only"
        echo "  --services SERVICE...   Build and push specific services only"
        echo "  --destroy               Destroy AWS infrastructure (Terraform)"
        echo "  --help, -h              Show this help message"
        echo ""
        echo "Available services: user-service, inventory-service, order-service, auth-service, gateway, frontend"
        echo "Default: Deploy everything (infrastructure + images + k8s)"
        ;;
    *)
        main "$@"
        ;;
esac