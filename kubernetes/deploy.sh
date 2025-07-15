#!/bin/bash

# kubernetes/deploy.sh
# Main K8s deployment script that handles all K8s-specific operations
# Usage: ./kubernetes/deploy.sh [--environment dev|prod] [--no-cache] [--verbose]

set -e

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="dev"
NO_CACHE=false
VERBOSE=false

# Logging functions
log_info() {
    printf "${BLUE}[INFO]${NC} %s\n" "$1"
}

log_success() {
    printf "${GREEN}[SUCCESS]${NC} %s\n" "$1"
}

log_warning() {
    printf "${YELLOW}[WARNING]${NC} %s\n" "$1"
}

log_error() {
    printf "${RED}[ERROR]${NC} %s\n" "$1"
}

log_step() {
    printf "\n${PURPLE}=== %s ===${NC}\n" "$1"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--environment dev|prod] [--no-cache] [--verbose]"
            echo "  --environment: Target environment (default: dev)"
            echo "  --no-cache: Build Docker images without cache"
            echo "  --verbose: Enable verbose output"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    log_error "Environment must be 'dev' or 'prod'"
    exit 1
fi

log_step "Deploying to Kubernetes (Environment: $ENVIRONMENT)"

# Check prerequisites
log_info "Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    log_error "kubectl is not installed or not in PATH"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    log_error "docker is not installed or not in PATH"
    exit 1
fi

if ! command -v kind &> /dev/null; then
    log_error "kind is not installed or not in PATH"
    exit 1
fi

log_success "Prerequisites check passed"

# Environment-specific deployment
if [[ "$ENVIRONMENT" == "dev" ]]; then
    log_step "Local Development Deployment (Kind)"

    # Check if Kind cluster exists, create multi-node if not
    if ! kind get clusters | grep -q "order-processor"; then
        log_info "Creating multi-node Kind cluster 'order-processor'..."
        kind create cluster --name order-processor --config kubernetes/kind-config.yaml
        log_success "Multi-node Kind cluster created successfully!"
    else
        log_info "Kind cluster 'order-processor' already exists"
    fi

    # Check if kubectl is configured for the cluster
    if ! kubectl cluster-info --context kind-order-processor >/dev/null 2>&1; then
        log_error "kubectl not configured for kind-order-processor cluster!"
        exit 1
    fi

    # Update AWS credentials from Terraform outputs
    log_info "Setting up AWS credentials from Terraform outputs..."
    if [[ -f "kubernetes/scripts/setup-aws-credentials.sh" ]]; then
        ./kubernetes/scripts/setup-aws-credentials.sh
    else
        log_warning "AWS credentials setup script not found, using existing configuration"
    fi

    # Build Docker images with cache cleanup
    log_info "Building Docker images..."
    cd docker

    if [[ "$NO_CACHE" == "true" ]]; then
        log_info "Removing old images to ensure fresh builds..."
        docker rmi order-processor-user_service:latest order-processor-inventory_service:latest order-processor-frontend:latest 2>/dev/null || true

        log_info "Building images with --no-cache..."
        docker-compose -f docker-compose.dev.yml build --no-cache
    else
        log_info "Building images (using cache)..."
        docker-compose -f docker-compose.dev.yml build
    fi

    cd ..

    # Load images into Kind cluster
    log_info "Loading images into Kind cluster..."
    kind load docker-image order-processor-user_service:latest --name order-processor
    kind load docker-image order-processor-inventory_service:latest --name order-processor
    kind load docker-image order-processor-frontend:latest --name order-processor

    # Apply base configuration
    log_info "Applying base configuration..."
    kubectl apply -k kubernetes/base

    # Deploy to local cluster
    log_info "Deploying to local cluster..."
    kubectl apply -k kubernetes/local

    # Wait for deployments to be ready
    log_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/user-service -n order-processor
    kubectl wait --for=condition=available --timeout=300s deployment/inventory-service -n order-processor
    kubectl wait --for=condition=available --timeout=300s deployment/frontend -n order-processor

    # Show deployment status
    log_info "Deployment Status:"
    kubectl get all -n order-processor

    log_success "Local deployment complete!"
    echo ""
    echo "🌐 Access Points:"
    echo "   Frontend: http://localhost:30000"
    echo "   User Service: http://localhost:30001"
    echo "   Inventory Service: http://localhost:30002"

elif [[ "$ENVIRONMENT" == "prod" ]]; then
    log_step "Production Deployment (EKS)"

    # Check if kubectl is configured for EKS
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "kubectl not configured for EKS cluster!"
        exit 1
    fi

    # Build and push to ECR
    log_info "Building and pushing images to ECR..."
    if [[ -f "scripts/ecr_build_push.sh" ]]; then
        ./scripts/ecr_build_push.sh
    else
        log_error "ECR build script not found"
        exit 1
    fi

    # Apply production configuration
    log_info "Applying production configuration..."
    kubectl apply -k kubernetes/prod

    # Wait for deployments to be ready
    log_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=600s deployment/user-service -n order-processor
    kubectl wait --for=condition=available --timeout=600s deployment/inventory-service -n order-processor
    kubectl wait --for=condition=available --timeout=600s deployment/frontend -n order-processor

    # Show deployment status
    log_info "Deployment Status:"
    kubectl get all -n order-processor

    log_success "Production deployment complete!"
fi

log_success "✅ Kubernetes deployment successful!"