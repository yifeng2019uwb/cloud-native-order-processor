#!/bin/bash
# scripts/deploy-app.sh
# Application Deployment Script
# Deploys to EKS

set -e

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=""
VERBOSE=false
DRY_RUN=false
SKIP_BUILD=false

# Usage function
show_usage() {
    cat << EOF
$(printf "${BLUE}📦 Application Deployment Script${NC}")

Usage: $0 --environment {dev|prod} [OPTIONS]

Deploy application to AWS EKS infrastructure.

REQUIRED:
    --environment {dev|prod}           Target environment

OPTIONS:
    -v, --verbose                      Enable verbose output
    --dry-run                         Show what would happen (don't deploy)
    --skip-build                      Skip build step, use existing package
    -h, --help                        Show this help message

EXAMPLES:
    $0 --environment dev                # Deploy to EKS dev
    $0 --environment prod               # Deploy to EKS prod
    $0 --environment dev --dry-run      # Plan only
    $0 --environment dev --skip-build   # Deploy without rebuilding

PREREQUISITES:
    - Infrastructure must be deployed first (./scripts/deploy.sh)
    - Docker and kubectl

EOF
}

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
    printf "\n${BLUE}=== %s ===${NC}\n" "$1"
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Validate arguments
validate_arguments() {
    local errors=()

    # Check required arguments
    if [[ -z "$ENVIRONMENT" ]]; then
        errors+=("--environment is required")
    elif [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
        errors+=("--environment must be 'dev' or 'prod'")
    fi

    if [[ ${#errors[@]} -gt 0 ]]; then
        log_error "Validation failed:"
        for error in "${errors[@]}"; do
            log_error "  - $error"
        done
        echo
        show_usage
        exit 1
    fi
}

# Set environment variables
setup_environment() {
    log_step "🔧 Setting up application deployment environment"

    # Set base environment variables
    export ENVIRONMENT="$ENVIRONMENT"
    export AWS_DEFAULT_REGION="${AWS_REGION:-us-west-2}"

    # Load environment-specific configuration
    local env_config="$PROJECT_ROOT/config/environments/.env.defaults"
    if [[ -f "$env_config" ]]; then
        log_info "Loading configuration: $env_config"
        source "$env_config"
    fi

    if [[ "$VERBOSE" == "true" ]]; then
        log_info "Environment variables set:"
        log_info "  ENVIRONMENT: $ENVIRONMENT"
        log_info "  AWS_REGION: ${AWS_REGION:-us-west-2}"
    fi
}

# Check prerequisites
check_prerequisites() {
    log_step "🔍 Checking Prerequisites"

    local missing_tools=()
    local errors=()

    # Common tools
    local common_tools=("aws" "jq" "docker" "kubectl")
    for tool in "${common_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done

    # Check Docker daemon
    if command -v docker >/dev/null 2>&1; then
        if ! docker info >/dev/null 2>&1; then
            errors+=("Docker is installed but not running")
        fi
    fi

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        errors+=("Missing required tools: ${missing_tools[*]}")
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        errors+=("AWS credentials not configured or invalid")
    fi

    # Check if infrastructure is deployed
    cd "$PROJECT_ROOT/terraform"
    if [[ ! -f "terraform.tfstate" ]] && [[ ! -f ".terraform/terraform.tfstate" ]]; then
        errors+=("Infrastructure not deployed. Run ./scripts/deploy.sh first")
    fi

    # Get EKS cluster name
    if ! terraform output eks_cluster_name >/dev/null 2>&1; then
        errors+=("EKS cluster not found in terraform outputs. Check infrastructure deployment.")
    else
        export EKS_CLUSTER_NAME=$(terraform output -raw eks_cluster_name 2>/dev/null || echo "")
        log_info "Found EKS cluster: $EKS_CLUSTER_NAME"
    fi

    cd "$PROJECT_ROOT"

    if [[ ${#errors[@]} -gt 0 ]]; then
        log_error "Prerequisites check failed:"
        for error in "${errors[@]}"; do
            log_error "  - $error"
        done
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Build Docker image for Kubernetes
build_docker_image() {
    if [[ "$SKIP_BUILD" == "true" ]]; then
        log_info "Skipping Docker build (--skip-build specified)"
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would build and push Docker image"
        return 0
    fi

    log_step "🐳 Building and Pushing Docker Image"

    # Login to ECR
    log_info "Logging into Amazon ECR..."
    aws ecr get-login-password --region "${AWS_REGION:-us-west-2}" | \
        docker login --username AWS --password-stdin \
        "$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_REGION:-us-west-2}.amazonaws.com"

    # Build and push using existing script if available
    if [[ -f "$PROJECT_ROOT/scripts/quick_build.sh" ]]; then
        log_info "Using existing Docker build script..."
        cd "$PROJECT_ROOT"
        chmod +x scripts/quick_build.sh

        if [[ "$VERBOSE" == "true" ]]; then
            ./scripts/quick_build.sh
        else
            ./scripts/quick_build.sh > /dev/null 2>&1
        fi

        log_success "Docker image built and pushed to ECR"
        return 0
    fi

    # Fallback: Manual Docker build
    log_info "Building Docker image manually..."

    local ecr_registry="$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_REGION:-us-west-2}.amazonaws.com"
    local image_name="order-processor-order-api"
    local image_tag="${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"

    if [[ -f "$PROJECT_ROOT/docker/order-service/Dockerfile.simple" ]]; then
        cd "$PROJECT_ROOT"

        docker build -f docker/order-service/Dockerfile.simple \
            -t "$ecr_registry/$image_name:$image_tag" \
            -t "$ecr_registry/$image_name:latest" .

        docker push "$ecr_registry/$image_name:$image_tag"
        docker push "$ecr_registry/$image_name:latest"

        export IMAGE_URI="$ecr_registry/$image_name:$image_tag"
        log_success "Docker image built and pushed: $IMAGE_URI"
    else
        log_error "Dockerfile not found: docker/order-service/Dockerfile.simple"
        exit 1
    fi
}

# Deploy to Kubernetes
deploy_to_kubernetes() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would deploy application to Kubernetes"
        return 0
    fi

    log_step "☸️ Deploying Application to Kubernetes"

    # Update EKS kubeconfig
    log_info "Updating kubeconfig for EKS cluster: $EKS_CLUSTER_NAME"
    aws eks update-kubeconfig \
        --region "${AWS_REGION:-us-west-2}" \
        --name "$EKS_CLUSTER_NAME"

    # Test kubectl connectivity
    if kubectl get nodes >/dev/null 2>&1; then
        log_success "kubectl connected to EKS cluster"
    else
        log_error "Failed to connect to EKS cluster"
        exit 1
    fi

    # Check if dedicated EKS deployment script exists
    if [[ -f "$PROJECT_ROOT/kubernetes/scripts/deploy-to-eks.sh" ]]; then
        log_info "Using existing EKS deployment script..."
        cd "$PROJECT_ROOT/kubernetes/scripts"
        chmod +x deploy-to-eks.sh

        if [[ "$VERBOSE" == "true" ]]; then
            ./deploy-to-eks.sh
        else
            ./deploy-to-eks.sh > /dev/null 2>&1
        fi

        log_success "Application deployed using EKS deployment script"
        return 0
    fi

    # Fallback: Deploy basic Kubernetes manifests
    log_info "Using basic Kubernetes manifest deployment..."
    cd "$PROJECT_ROOT/kubernetes"

    # Deploy manifests in order
    local manifests=("namespace.yaml" "deployment.yaml" "service.yaml")

    for manifest in "${manifests[@]}"; do
        if [[ -f "$manifest" ]]; then
            log_info "Applying $manifest..."
            kubectl apply -f "$manifest"
        else
            log_warning "Manifest not found: $manifest"
        fi
    done

    # Wait for deployment to be ready
    log_info "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/order-service -n order-processor 2>/dev/null || {
        log_warning "Deployment readiness check timed out or failed"
    }

    # Get service URL if available
    local service_url=""
    service_url=$(kubectl get service order-service -n order-processor -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")

    if [[ -n "$service_url" ]]; then
        export SERVICE_URL="http://$service_url"
        log_info "Service URL: $SERVICE_URL"
    else
        log_info "Service URL not yet available (LoadBalancer provisioning)"
    fi

    cd "$PROJECT_ROOT"
    log_success "Application deployed to Kubernetes successfully"
}

# Verify deployment
verify_deployment() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would verify application deployment"
        return 0
    fi

    log_step "✅ Verifying Application Deployment"

    # Verify Kubernetes deployment
    log_info "Checking pod status..."
    kubectl get pods -n order-processor 2>/dev/null || {
        log_warning "Could not get pod status"
    }

    log_info "Checking service status..."
    kubectl get services -n order-processor 2>/dev/null || {
        log_warning "Could not get service status"
    }

    if [[ -n "$SERVICE_URL" ]]; then
        log_info "Kubernetes Service URL: $SERVICE_URL"
    fi

    log_success "Application deployment verification completed"
}

# Generate deployment summary
generate_summary() {
    log_step "📊 Application Deployment Summary"

    log_info "Deployment Details:"
    log_info "  Environment: $ENVIRONMENT"
    log_info "  Deployment Type: EKS + Kubernetes"
    log_info "  EKS Cluster: ${EKS_CLUSTER_NAME:-unknown}"
    log_info "  Docker Image: ${IMAGE_URI:-existing}"
    log_info "  Service URL: ${SERVICE_URL:-pending}"

    if [[ "$DRY_RUN" == "false" ]]; then
        log_success "✅ Application deployment completed successfully!"
        log_info "Next steps:"
        log_info "  1. Run integration tests: ./scripts/test-integration.sh --environment $ENVIRONMENT"
        log_info "  2. Monitor pods: kubectl get pods -n order-processor"
        log_info "  3. When done, cleanup: ./scripts/destroy.sh --environment $ENVIRONMENT --force"
    else
        log_success "✅ Application deployment plan validated!"
        log_info "Remove --dry-run flag to deploy application"
    fi
}

# Main execution
main() {
    # Parse arguments
    parse_arguments "$@"

    # Validate arguments
    validate_arguments

    # Print header
    echo
    printf "${BLUE}📦 Application Deployment Script${NC}\n"
    printf "${BLUE}================================${NC}\n"
    echo
    log_info "Deploying application to: $ENVIRONMENT environment"
    echo

    # Execute deployment steps
    setup_environment
    check_prerequisites
    build_docker_image
    deploy_to_kubernetes
    verify_deployment
    generate_summary

    # Return to original directory
    cd "$PROJECT_ROOT"
}

# Run main function
main "$@"