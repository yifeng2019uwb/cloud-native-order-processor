#!/bin/bash

# kubernetes/deploy.sh
# Main K8s deployment script that handles all K8s-specific operations
# Usage: ./kubernetes/deploy.sh [--environment dev|prod] [--no-cache] [--verbose] [--step STEP_NAME]

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
STEP=""

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
        --step)
            STEP="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--environment dev|prod] [--no-cache] [--verbose] [--step STEP_NAME]"
            echo "  --environment: Target environment (default: dev)"
            echo "  --no-cache: Build Docker images without cache"
            echo "  --verbose: Enable verbose output"
            echo "  --step: Run specific step only (prerequisites|cluster|credentials|build|deploy|status)"
            echo ""
            echo "Available steps:"
            echo "  prerequisites - Check required tools"
            echo "  cluster       - Create/check Kind cluster"
            echo "  credentials   - Setup AWS credentials"
            echo "  build         - Build and load Docker images"
            echo "  deploy        - Deploy to Kubernetes"
            echo "  status        - Show deployment status"
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

# Validate step if provided
if [[ -n "$STEP" ]]; then
    case $STEP in
        prerequisites|cluster|credentials|build|deploy|status)
            ;;
        *)
            log_error "Invalid step: $STEP"
            echo "Available steps: prerequisites, cluster, credentials, build, deploy, status"
            exit 1
            ;;
    esac
fi

log_step "Deploying to Kubernetes (Environment: $ENVIRONMENT)"

# Step 1: Check prerequisites
check_prerequisites() {
    log_step "Checking Prerequisites"
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
}

# Step 2: Setup cluster
setup_cluster() {
    log_step "Setting up Kind Cluster"

    # Check if Kind cluster exists
    if kind get clusters | grep -q "order-processor"; then
        log_info "Kind cluster 'order-processor' already exists"

        # Check cluster health and worker nodes
        log_info "Checking cluster health..."
        if ! kubectl cluster-info --context kind-order-processor >/dev/null 2>&1; then
            log_error "kubectl not configured for kind-order-processor cluster!"
            exit 1
        fi

        # Check worker nodes
        log_info "Checking worker nodes..."
        NODE_COUNT=$(kubectl get nodes --context kind-order-processor --no-headers | wc -l)
        log_info "Found $NODE_COUNT nodes in cluster"

        # Check if nodes are ready
        READY_NODES=$(kubectl get nodes --context kind-order-processor --no-headers | grep -c "Ready")
        if [[ "$READY_NODES" -lt "$NODE_COUNT" ]]; then
            log_warning "Some nodes are not ready. Ready: $READY_NODES/$NODE_COUNT"
            log_info "Attempting to restart unhealthy nodes..."

            # Get unhealthy nodes
            UNHEALTHY_NODES=$(kubectl get nodes --context kind-order-processor --no-headers | grep -v "Ready" | awk '{print $1}')
            for node in $UNHEALTHY_NODES; do
                log_info "Restarting node: $node"
                docker restart "$node" 2>/dev/null || log_warning "Could not restart node $node"
            done

            # Wait a bit and check again
            sleep 10
            READY_NODES=$(kubectl get nodes --context kind-order-processor --no-headers | grep -c "Ready")
            if [[ "$READY_NODES" -lt "$NODE_COUNT" ]]; then
                log_warning "Some nodes still not ready after restart. Ready: $READY_NODES/$NODE_COUNT"
            else
                log_success "All nodes are now ready after restart"
            fi
        else
            log_success "All nodes are ready"
        fi

        # Check cluster version and update if needed
        log_info "Checking cluster version..."
        CLUSTER_VERSION=$(kubectl version --context kind-order-processor --short 2>/dev/null | grep "Server Version" | cut -d' ' -f3 || echo "unknown")
        log_info "Current cluster version: $CLUSTER_VERSION"

        # Check if we need to update the cluster configuration
        log_info "Checking if cluster configuration needs updates..."
        # This could be expanded to check for specific configuration changes

    else
        log_info "Kind cluster 'order-processor' does not exist"

        # Clean up Docker cache before creating new cluster
        log_info "Cleaning up Docker cache before creating new cluster..."

        # Remove any existing order-processor related images
        log_info "Removing existing order-processor Docker images..."
        docker rmi order-processor-user_service:latest order-processor-inventory_service:latest order-processor-frontend:latest 2>/dev/null || true

        # Clean up unused Docker resources
        log_info "Cleaning up unused Docker resources..."
        docker system prune -f

        # Clean up any dangling images
        log_info "Cleaning up dangling images..."
        docker image prune -f

        # Create new multi-node Kind cluster
        log_info "Creating multi-node Kind cluster 'order-processor'..."
        kind create cluster --name order-processor --config kubernetes/kind-config.yaml

        # Verify cluster creation
        if kind get clusters | grep -q "order-processor"; then
            log_success "Multi-node Kind cluster created successfully!"
        else
            log_error "Failed to create Kind cluster"
            exit 1
        fi

        # Wait for cluster to be ready
        log_info "Waiting for cluster to be ready..."
        sleep 10

        # Check cluster health
        log_info "Checking cluster health..."
        if ! kubectl cluster-info --context kind-order-processor >/dev/null 2>&1; then
            log_error "kubectl not configured for kind-order-processor cluster!"
            exit 1
        fi

        # Check worker nodes
        log_info "Checking worker nodes..."
        NODE_COUNT=$(kubectl get nodes --context kind-order-processor --no-headers | wc -l)
        log_info "Found $NODE_COUNT nodes in cluster"

        # Wait for all nodes to be ready
        log_info "Waiting for all nodes to be ready..."
        kubectl wait --for=condition=ready --timeout=300s node --all --context kind-order-processor

        READY_NODES=$(kubectl get nodes --context kind-order-processor --no-headers | grep -c "Ready")
        if [[ "$READY_NODES" -eq "$NODE_COUNT" ]]; then
            log_success "All nodes are ready"
        else
            log_error "Not all nodes are ready. Ready: $READY_NODES/$NODE_COUNT"
            exit 1
        fi
    fi

    # Final cluster status check
    log_info "Final cluster status:"
    kubectl get nodes --context kind-order-processor
    log_success "Cluster setup complete"
}

# Step 3: Setup credentials
setup_credentials() {
    log_step "Setting up AWS Credentials"

    # Update AWS credentials from Terraform outputs
    log_info "Setting up AWS credentials from Terraform outputs..."
    if [[ -f "kubernetes/scripts/setup-aws-credentials.sh" ]]; then
        ./kubernetes/scripts/setup-aws-credentials.sh
    else
        log_warning "AWS credentials setup script not found, using existing configuration"
    fi
}

# Step 4: Build images
build_images() {
    log_step "Building Docker Images"

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
}

# Step 5: Deploy to Kubernetes
deploy_to_k8s() {
    log_step "Deploying to Kubernetes"

    # Apply base configuration
    log_info "Applying base configuration..."
    kubectl apply -k kubernetes/base

    # Clean up any conflicting DaemonSets before deployment
    log_info "Cleaning up any conflicting DaemonSets..."
    kubectl delete daemonset fluent-bit -n kube-system 2>/dev/null || true
    kubectl delete daemonset fluent-bit -n order-processor 2>/dev/null || true

    # Ensure aws-credentials secret is up-to-date in the cluster
    kubectl create secret generic aws-credentials \
      --from-literal=aws-access-key-id="$AWS_ACCESS_KEY_ID" \
      --from-literal=aws-secret-access-key="$AWS_SECRET_ACCESS_KEY" \
      -n order-processor --dry-run=client -o yaml | kubectl apply -f -

    # Deploy to local cluster (updates existing deployments if they exist)
    log_info "Deploying to local cluster..."
    kubectl apply -k kubernetes/dev

    # Wait for deployments to be ready
    log_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/user-service -n order-processor
    kubectl wait --for=condition=available --timeout=300s deployment/inventory-service -n order-processor
    kubectl wait --for=condition=available --timeout=300s deployment/frontend -n order-processor
}

# Step 6: Show status
show_status() {
    log_step "Deployment Status"

    # Show deployment status
    log_info "Deployment Status:"
    kubectl get all -n order-processor

    log_success "Local deployment complete!"
    echo ""
    echo "🌐 Access Points:"
    echo "   Frontend: http://localhost:30000"
    echo "   User Service: http://localhost:30001"
    echo "   Inventory Service: http://localhost:30002"
}

# Main execution logic
if [[ "$ENVIRONMENT" == "dev" ]]; then
    if [[ -n "$STEP" ]]; then
        # Run specific step only
        case $STEP in
            prerequisites)
                check_prerequisites
                ;;
            cluster)
                check_prerequisites
                setup_cluster
                ;;
            credentials)
                setup_credentials
                ;;
            build)
                check_prerequisites
                setup_cluster
                build_images
                ;;
            deploy)
                check_prerequisites
                setup_cluster
                setup_credentials
                build_images
                deploy_to_k8s
                ;;
            status)
                show_status
                ;;
        esac
    else
        # Run all steps
        check_prerequisites
        setup_cluster
        setup_credentials
        build_images
        deploy_to_k8s
        show_status
    fi

elif [[ "$ENVIRONMENT" == "prod" ]]; then
    log_step "Production Deployment (EKS) - DISABLED"
    log_warning "Production deployment is currently disabled/not implemented"
    log_info "This section will be implemented when production deployment is ready"
    exit 1

    # TODO: Implement production deployment when ready
    # The following code is commented out until production deployment is implemented

    # log_step "Production Deployment (EKS)"
    #
    # # Check if kubectl is configured for EKS
    # if ! kubectl cluster-info >/dev/null 2>&1; then
    #     log_error "kubectl not configured for EKS cluster!"
    #     exit 1
    # fi
    #
    # # Build and push to ECR
    # log_info "Building and pushing images to ECR..."
    # if [[ -f "scripts/ecr_build_push.sh" ]]; then
    #     ./scripts/ecr_build_push.sh
    # else
    #     log_error "ECR build script not found"
    #     exit 1
    # fi
    #
    # # Apply production configuration
    # log_info "Applying production configuration..."
    # kubectl apply -k kubernetes/prod
    #
    # # Wait for deployments to be ready
    # log_info "Waiting for deployments to be ready..."
    # kubectl wait --for=condition=available --timeout=600s deployment/user-service -n order-processor
    # kubectl wait --for=condition=available --timeout=600s deployment/inventory-service -n order-processor
    # kubectl wait --for=condition=available --timeout=600s deployment/frontend -n order-processor
    #
    # # Show deployment status
    # log_info "Deployment Status:"
    # kubectl get all -n order-processor
    #
    # log_success "Production deployment complete!"
fi

log_success "✅ Kubernetes deployment successful!"