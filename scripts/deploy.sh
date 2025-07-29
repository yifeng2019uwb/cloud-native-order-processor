#!/bin/bash
# scripts/deploy.sh
# Universal Deployment Script - Consolidates all deployment operations
# Handles: Service deployment, Infrastructure deployment, Kubernetes deployment

set -e

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="dev"
DEPLOY_TYPE=""
SERVICE_NAME=""
VERBOSE=false
DRY_RUN=false
NO_CACHE=false

# Usage function
show_usage() {
    cat << EOF
$(printf "${BLUE}🚀 Universal Deployment Script${NC}")

Usage: $0 --type {service|infra|k8s|all} [OPTIONS]

Deploy services, infrastructure, or Kubernetes resources.

REQUIRED:
    --type {service|infra|k8s|all}     Deployment type

OPTIONS:
    --environment {dev|prod}           Target environment (default: dev)
    --service {user|inventory}         Service name (for service deployment)
    -v, --verbose                      Enable verbose output
    --dry-run                          Show what would happen (terraform plan only)
    --no-cache                         Build Docker images without cache (k8s only)
    -h, --help                         Show this help message

EXAMPLES:
    # Deploy specific service
    $0 --type service --service user
    $0 --type service --service inventory

    # Deploy infrastructure
    $0 --type infra --environment dev
    $0 --type infra --environment prod --dry-run

    # Deploy to Kubernetes
    $0 --type k8s --environment dev
    $0 --type k8s --environment prod --no-cache

    # Deploy everything
    $0 --type all --environment dev

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
    printf "\n${PURPLE}=== %s ===${NC}\n" "$1"
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --type)
                DEPLOY_TYPE="$2"
                shift 2
                ;;
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --service)
                SERVICE_NAME="$2"
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
            --no-cache)
                NO_CACHE=true
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
    if [[ -z "$DEPLOY_TYPE" ]]; then
        errors+=("--type is required")
    fi

    # Validate deployment type
    if [[ -n "$DEPLOY_TYPE" ]]; then
        case $DEPLOY_TYPE in
            service|infra|k8s|all)
                ;;
            *)
                errors+=("Invalid deployment type: $DEPLOY_TYPE")
                ;;
        esac
    fi

    # Validate environment
    if [[ -n "$ENVIRONMENT" ]]; then
        case $ENVIRONMENT in
            dev|prod)
                ;;
            *)
                errors+=("Environment must be 'dev' or 'prod'")
                ;;
        esac
    fi

    # Validate service name for service deployment
    if [[ "$DEPLOY_TYPE" == "service" ]]; then
        if [[ -z "$SERVICE_NAME" ]]; then
            errors+=("--service is required for service deployment")
        elif [[ "$SERVICE_NAME" != "user" && "$SERVICE_NAME" != "inventory" ]]; then
            errors+=("Service must be 'user' or 'inventory'")
        fi
    fi

    # Show errors if any
    if [[ ${#errors[@]} -gt 0 ]]; then
        for error in "${errors[@]}"; do
            log_error "$error"
        done
        show_usage
        exit 1
    fi
}

# Deploy service function
deploy_service() {
    local service=$1
    log_step "Deploying $service service"

    local service_dir="$PROJECT_ROOT/services/${service}_service"
    if [[ ! -d "$service_dir" ]]; then
        log_error "Service directory not found: $service_dir"
        exit 1
    fi

    cd "$service_dir"

    # Check if main.py exists
    if [[ ! -f "src/main.py" ]]; then
        log_error "src/main.py not found in $service_dir"
        exit 1
    fi

    # Set service-specific variables
    local port=""
    case $service in
        user)
            port=8000
            ;;
        inventory)
            port=8001
            ;;
    esac

    # Check Python version
    local python_version="3.11"
    if ! command -v python${python_version} &> /dev/null; then
        log_error "Python ${python_version} is not installed"
        exit 1
    fi

    log_info "Python ${python_version} found"

    # Create virtual environment if it doesn't exist
    local venv_name=".venv-${service}_service"
    if [[ ! -d "$venv_name" ]]; then
        log_info "Creating virtual environment..."
        python${python_version} -m venv "$venv_name"
    fi

    # Activate virtual environment
    log_info "Activating virtual environment..."
    source "$venv_name/bin/activate"

    # Install dependencies
    if [[ -f "requirements.txt" ]]; then
        log_info "Installing dependencies..."
        pip install -r requirements.txt
    fi

    # Install common package if it exists
    if [[ -d "../common" ]]; then
        log_info "Installing common package..."
        pip install -e ../common
    fi

    # Check if port is available
    if lsof -Pi :${port} -sTCP:LISTEN -t >/dev/null ; then
        log_warning "Port ${port} is already in use"
        local pid=$(lsof -Pi :${port} -sTCP:LISTEN -t)
        if ps -p $pid | grep -q "uvicorn"; then
            log_success "Service already running on port ${port} (PID: ${pid})"
            log_info "Service URL: http://localhost:${port}"
            log_info "API Docs: http://localhost:${port}/docs"
            log_info "Health Check: http://localhost:${port}/health"
            return 0
        else
            log_error "Port ${port} is in use by another process (PID: ${pid})"
            exit 1
        fi
    fi

    # Set environment variables
    export PYTHONPATH="${service_dir}/src:${PYTHONPATH}"

    # Load environment variables from .env if it exists
    if [[ -f "../.env" ]]; then
        log_info "Loading environment variables from ../.env"
        export $(grep -v '^#' ../.env | xargs)
    fi

    # Start the service
    log_success "Starting ${service}_service on port ${port}..."
    log_info "Service URL: http://localhost:${port}"
    log_info "API Docs: http://localhost:${port}/docs"
    log_info "Health Check: http://localhost:${port}/health"

    # Start in background
    nohup uvicorn src.main:app --host 0.0.0.0 --port ${port} --reload > "${service}_service.log" 2>&1 &
    local pid=$!
    echo $pid > "${service}_service.pid"
    log_success "${service}_service started with PID: $pid"
}

# Deploy infrastructure function
deploy_infrastructure() {
    log_step "Deploying infrastructure (Terraform)"

    local terraform_dir="$PROJECT_ROOT/terraform"
    if [[ ! -d "$terraform_dir" ]]; then
        log_error "Terraform directory not found: $terraform_dir"
        exit 1
    fi

    cd "$terraform_dir"

    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed"
        exit 1
    fi

    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init

    # Set environment variables
    export TF_VAR_environment="$ENVIRONMENT"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Running Terraform plan (dry run)..."
        terraform plan -var-file="terraform.tfvars"
    else
        log_info "Running Terraform apply..."
        terraform apply -var-file="terraform.tfvars" -auto-approve
    fi

    log_success "Infrastructure deployment completed"
}

# Deploy Kubernetes function
deploy_kubernetes() {
    log_step "Deploying to Kubernetes"

    local k8s_dir="$PROJECT_ROOT/kubernetes"
    if [[ ! -d "$k8s_dir" ]]; then
        log_error "Kubernetes directory not found: $k8s_dir"
        exit 1
    fi

    cd "$k8s_dir"

    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi

    # Check if Kubernetes cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        log_error "No Kubernetes cluster is accessible"
        log_info "Please start a local cluster (e.g., kind create cluster --name order-processor)"
        exit 1
    fi

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Build Docker images
    log_info "Building Docker images..."
    local docker_args=""
    if [[ "$NO_CACHE" == "true" ]]; then
        docker_args="--no-cache"
    fi

    # Build frontend
    log_info "Building frontend image..."
    docker build $docker_args -t order-processor-frontend:latest -f ../docker/frontend/Dockerfile ../

    # Build services
    log_info "Building user service image..."
    docker build $docker_args -t order-processor-user_service:latest -f ../docker/user-service/Dockerfile ../

    log_info "Building inventory service image..."
    docker build $docker_args -t order-processor-inventory_service:latest -f ../docker/inventory-service/Dockerfile ../

    # Build gateway
    log_info "Building gateway image..."
    docker build $docker_args -t order-processor-gateway:latest -f ../docker/gateway/Dockerfile ../

    # Deploy to Kubernetes
    log_info "Deploying to Kubernetes..."

    # Apply base configuration first (creates namespace and other base resources)
    log_info "Applying base configuration..."
    kubectl apply -k base/

    # Deploy environment-specific configuration
    log_info "Deploying $ENVIRONMENT configuration..."
    kubectl apply -k "$ENVIRONMENT/"

    log_success "Kubernetes deployment completed"
}

# Main deployment function
main() {
    log_info "Starting deployment process..."
    log_info "Deployment type: $DEPLOY_TYPE"
    log_info "Environment: $ENVIRONMENT"

    case $DEPLOY_TYPE in
        service)
            deploy_service "$SERVICE_NAME"
            ;;
        infra)
            deploy_infrastructure
            ;;
        k8s)
            deploy_kubernetes
            ;;
        all)
            log_step "Deploying everything"
            deploy_infrastructure
            deploy_kubernetes
            log_info "Note: Services are deployed via Kubernetes"
            ;;
    esac

    log_success "Deployment completed successfully!"
}

# Script execution
parse_arguments "$@"
validate_arguments
main