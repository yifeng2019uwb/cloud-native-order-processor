#!/bin/bash
# scripts/deploy-app.sh
# Application Deployment Script
# Deploys Docker images and Kubernetes applications to AWS EKS

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
PROFILE=""
VERBOSE=false
DRY_RUN=false
SKIP_BUILD=false

# Usage function
show_usage() {
    cat << EOF
$(printf "${BLUE}📦 Application Deployment Script${NC}")

Usage: $0 --environment {dev|prod} --profile {learning|minimum|prod} [OPTIONS]

Deploy application (Docker + Kubernetes) to AWS EKS infrastructure.

REQUIRED:
    --environment {dev|prod}           Target environment
    --profile {learning|minimum|prod}  Resource profile

OPTIONS:
    -v, --verbose                      Enable verbose output
    --dry-run                         Show what would happen (don't deploy)
    --skip-build                      Skip Docker build, use existing images
    -h, --help                        Show this help message

EXAMPLES:
    $0 --environment dev --profile learning        # Deploy app to dev environment
    $0 --environment prod --profile prod           # Deploy app to prod environment
    $0 --environment dev --profile learning --dry-run  # Plan only, don't deploy
    $0 --environment dev --profile learning --skip-build  # Deploy without rebuilding

PREREQUISITES:
    - Infrastructure must be deployed first (./scripts/deploy.sh)
    - Docker must be installed and running
    - AWS CLI configured with appropriate permissions
    - kubectl configured for target EKS cluster

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
            --profile)
                PROFILE="$2"
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

    if [[ -z "$PROFILE" ]]; then
        errors+=("--profile is required")
    elif [[ "$PROFILE" != "learning" && "$PROFILE" != "minimum" && "$PROFILE" != "prod" ]]; then
        errors+=("--profile must be 'learning', 'minimum', or 'prod'")
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
    export COST_PROFILE="$PROFILE"
    export AWS_DEFAULT_REGION="${AWS_REGION:-us-west-2}"

    # Load environment-specific configuration
    local env_config="$PROJECT_ROOT/config/environments/${ENVIRONMENT}.env"
    if [[ -f "$env_config" ]]; then
        log_info "Loading environment config: $env_config"
        source "$env_config"
    fi

    # Load profile-specific configuration
    local profile_config="$PROJECT_ROOT/config/profiles/${PROFILE}.env"
    if [[ -f "$profile_config" ]]; then
        log_info "Loading profile config: $profile_config"
        source "$profile_config"
    fi

    if [[ "$VERBOSE" == "true" ]]; then
        log_info "Environment variables set:"
        log_info "  ENVIRONMENT: $ENVIRONMENT"
        log_info "  COST_PROFILE: $PROFILE"
        log_info "  AWS_REGION: ${AWS_REGION:-us-west-2}"
    fi
}

# Check prerequisites
check_prerequisites() {
    log_step "🔍 Checking Prerequisites"

    local missing_tools=()
    local errors=()

    # Check required tools
    local tools=("docker" "aws" "kubectl")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        errors+=("Missing required tools: ${missing_tools[*]}")
    fi

    # Check Docker daemon
    if command -v docker >/dev/null 2>&1; then
        if ! docker info >/dev/null 2>&1; then
            errors+=("Docker daemon is not running")
        fi
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

    # Try to get EKS cluster info
    local cluster_name=""
    if terraform output eks_cluster_name >/dev/null 2>&1; then
        cluster_name=$(terraform output -raw eks_cluster_name 2>/dev/null || echo "")
    fi

    if [[ -z "$cluster_name" ]]; then
        errors+=("EKS cluster not found in terraform outputs")
    else
        export EKS_CLUSTER_NAME="$cluster_name"
        log_info "Found EKS cluster: $cluster_name"
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

# Build and push Docker images
build_and_push_images() {
    if [[ "$SKIP_BUILD" == "true" ]]; then
        log_info "Skipping Docker build (--skip-build specified)"
        return 0
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would build and push Docker images"
        return 0
    fi

    log_step "🐳 Building and Pushing Docker Images"

    # Check if ECR build script exists
    if [[ -f "$PROJECT_ROOT/scripts/ecr_build_push.sh" ]]; then
        log_info "Using existing ECR build script..."
        cd "$PROJECT_ROOT"
        chmod +x scripts/ecr_build_push.sh

        if [[ "$VERBOSE" == "true" ]]; then
            ./scripts/ecr_build_push.sh
        else
            ./scripts/ecr_build_push.sh > /dev/null 2>&1
        fi

        log_success "Docker images built and pushed to ECR"
        return 0
    fi

    # Fallback: Manual Docker build and push
    log_info "Using manual Docker build process..."

    # Login to ECR
    log_info "Logging into Amazon ECR..."
    aws ecr get-login-password --region "${AWS_REGION:-us-west-2}" | \
        docker login --username AWS --password-stdin \
        "$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_REGION:-us-west-2}.amazonaws.com"

    # Build and push order-service image
    local ecr_registry="$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_REGION:-us-west-2}.amazonaws.com"
    local image_name="order-processor-order-api"
    local image_tag="${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"

    if [[ -f "$PROJECT_ROOT/docker/order-service/Dockerfile.simple" ]]; then
        log_info "Building order-service Docker image..."
        cd "$PROJECT_ROOT"

        docker build -f docker/order-service/Dockerfile.simple \
            -t "$ecr_registry/$image_name:$image_tag" \
            -t "$ecr_registry/$image_name:latest" .

        log_info "Pushing image to ECR..."
        docker push "$ecr_registry/$image_name:$image_tag"
        docker push "$ecr_registry/$image_name:latest"

        # Store image URI for Kubernetes deployment
        export IMAGE_URI="$ecr_registry/$image_name:$image_tag"

        log_success "Docker image built and pushed: $IMAGE_URI"
    else
        log_error "Dockerfile not found: docker/order-service/Dockerfile.simple"
        exit 1
    fi
}

# Update EKS kubeconfig
update_kubeconfig() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would update kubeconfig for EKS cluster"
        return 0
    fi

    log_step "☸️ Updating Kubernetes Configuration"

    log_info "Updating kubeconfig for EKS cluster: $EKS_CLUSTER_NAME"
    aws eks update-kubeconfig \
        --region "${AWS_REGION:-us-west-2}" \
        --name "$EKS_CLUSTER_NAME"

    # Test kubectl connectivity
    log_info "Testing kubectl connectivity..."
    if kubectl get nodes >/dev/null 2>&1; then
        log_success "kubectl connected to EKS cluster"
    else
        log_error "Failed to connect to EKS cluster"
        exit 1
    fi
}

# Deploy to Kubernetes
deploy_to_kubernetes() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would deploy application to Kubernetes"
        return 0
    fi

    log_step "🚀 Deploying Application to Kubernetes"

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

    log_success "Application deployed to Kubernetes"
}

# Verify deployment
verify_deployment() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would verify application deployment"
        return 0
    fi

    log_step "✅ Verifying Application Deployment"

    # Check pod status
    log_info "Checking pod status..."
    kubectl get pods -n order-processor 2>/dev/null || {
        log_warning "Could not get pod status"
        return 0
    }

    # Check service status
    log_info "Checking service status..."
    kubectl get services -n order-processor 2>/dev/null || {
        log_warning "Could not get service status"
        return 0
    }

    # Get service endpoints if available
    local service_url=""
    service_url=$(kubectl get service order-service -n order-processor -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")

    if [[ -n "$service_url" ]]; then
        log_info "Service URL: http://$service_url"
        export SERVICE_URL="http://$service_url"
    else
        log_info "Service URL not yet available (LoadBalancer provisioning)"
    fi

    log_success "Application deployment verification completed"
}

# Generate deployment summary
generate_summary() {
    log_step "📊 Application Deployment Summary"

    log_info "Deployment Details:"
    log_info "  Environment: $ENVIRONMENT"
    log_info "  Profile: $PROFILE"
    log_info "  EKS Cluster: ${EKS_CLUSTER_NAME:-unknown}"
    log_info "  Docker Image: ${IMAGE_URI:-existing}"
    log_info "  Service URL: ${SERVICE_URL:-pending}"

    if [[ "$DRY_RUN" == "false" ]]; then
        log_success "✅ Application deployment completed successfully!"
        log_info "Next steps:"
        log_info "  1. Run integration tests: ./scripts/test-integration.sh --environment $ENVIRONMENT"
        log_info "  2. Monitor deployment: kubectl get pods -n order-processor"
        log_info "  3. When done, cleanup: ./scripts/destroy.sh --environment $ENVIRONMENT --profile $PROFILE"
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
    log_info "Deploying application to: $ENVIRONMENT environment with $PROFILE profile"
    echo

    # Execute deployment steps
    setup_environment
    check_prerequisites
    build_and_push_images
    update_kubeconfig
    deploy_to_kubernetes
    verify_deployment
    generate_summary

    # Return to original directory
    cd "$PROJECT_ROOT"
}

# Run main function
main "$@"