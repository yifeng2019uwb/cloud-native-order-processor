#!/bin/bash
# scripts/deploy.sh
# Enhanced Infrastructure Deployment Script
# Supports environments (dev/prod) and profiles (learning/minimum/prod)

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

# Usage function
show_usage() {
    cat << EOF
$(printf "${BLUE}🚀 Infrastructure Deployment Script${NC}")

Usage: $0 --environment {dev|prod} --profile {learning|minimum|prod} [OPTIONS]

Deploy AWS infrastructure using Terraform with environment and profile support.

REQUIRED:
    --environment {dev|prod}           Target environment
    --profile {learning|minimum|prod}  Resource profile

OPTIONS:
    -v, --verbose                      Enable verbose output
    --dry-run                         Show what would happen (terraform plan only)
    -h, --help                        Show this help message

EXAMPLES:
    $0 --environment dev --profile learning     # Deploy to dev with cost-optimized resources
    $0 --environment dev --profile minimum      # Deploy to dev with minimal resources
    $0 --environment prod --profile prod        # Deploy to prod with production resources
    $0 --environment dev --profile learning --dry-run  # Plan only, don't apply

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

    # Validate environment/profile combinations
    if [[ "$ENVIRONMENT" == "prod" && "$PROFILE" != "prod" ]]; then
        errors+=("prod environment must use prod profile")
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

# Set environment variables based on environment and profile
setup_environment() {
    log_step "🔧 Setting up environment: $ENVIRONMENT with profile: $PROFILE"

    # Set base environment variables
    export ENVIRONMENT="$ENVIRONMENT"
    export COST_PROFILE="$PROFILE"
    export TF_VAR_environment="$ENVIRONMENT"
    export TF_VAR_cost_profile="$PROFILE"

    # Load environment-specific configuration
    local env_config="$PROJECT_ROOT/config/environments/${ENVIRONMENT}.env"
    if [[ -f "$env_config" ]]; then
        log_info "Loading environment config: $env_config"
        source "$env_config"
    else
        log_warning "Environment config not found: $env_config"
    fi

    # Load profile-specific configuration
    local profile_config="$PROJECT_ROOT/config/profiles/${PROFILE}.env"
    if [[ -f "$profile_config" ]]; then
        log_info "Loading profile config: $profile_config"
        source "$profile_config"
    else
        log_warning "Profile config not found: $profile_config"
    fi

    # Set additional Terraform variables
    export TF_VAR_region="${AWS_REGION:-us-west-2}"
    export TF_IN_AUTOMATION=true

    if [[ "$VERBOSE" == "true" ]]; then
        log_info "Environment variables set:"
        log_info "  ENVIRONMENT: $ENVIRONMENT"
        log_info "  COST_PROFILE: $PROFILE"
        log_info "  AWS_REGION: ${AWS_REGION:-us-west-2}"
        log_info "  AWS_PROFILE: ${AWS_PROFILE:-default}"
    fi
}

# Check prerequisites
check_prerequisites() {
    log_step "🔍 Checking Prerequisites"

    local missing_tools=()

    # Check required tools
    local tools=("terraform" "aws" "jq")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Install missing tools:"
        log_info "  - Terraform: https://developer.hashicorp.com/terraform/downloads"
        log_info "  - AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        log_info "  - jq: apt install jq / brew install jq"
        exit 1
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        log_error "AWS credentials not configured or invalid"
        log_info "Configure AWS credentials:"
        log_info "  - aws configure"
        log_info "  - or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
        exit 1
    fi

    # Check Terraform directory
    if [[ ! -d "$PROJECT_ROOT/terraform" ]]; then
        log_error "Terraform directory not found: $PROJECT_ROOT/terraform"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Deploy infrastructure
deploy_infrastructure() {
    log_step "🚀 Deploying Infrastructure with Terraform"

    cd "$PROJECT_ROOT/terraform"

    # Initialize Terraform
    log_info "Initializing Terraform..."
    if [[ "$VERBOSE" == "true" ]]; then
        terraform init
    else
        terraform init > /dev/null
    fi

    # Validate configuration
    log_info "Validating Terraform configuration..."
    terraform validate

    # Create execution plan
    log_info "Creating Terraform execution plan..."
    local plan_args="-var=cost_profile=$PROFILE -var=environment=$ENVIRONMENT"

    if [[ "$VERBOSE" == "true" ]]; then
        terraform plan $plan_args
    else
        terraform plan $plan_args > /dev/null
    fi

    # Apply changes (unless dry-run)
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Terraform plan completed, skipping apply"
        log_success "Infrastructure plan validation completed"
        return 0
    fi

    log_info "Applying Terraform changes..."
    if [[ "$VERBOSE" == "true" ]]; then
        terraform apply -auto-approve $plan_args
    else
        terraform apply -auto-approve $plan_args
    fi

    log_success "Infrastructure deployment completed"
}

# Deploy Kubernetes resources (if not dry-run)
deploy_kubernetes() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Skipping Kubernetes deployment"
        return 0
    fi

    log_step "☸️ Deploying Kubernetes Resources"

    cd "$PROJECT_ROOT/kubernetes"

    # Check if kubectl is available
    if ! command -v kubectl >/dev/null 2>&1; then
        log_warning "kubectl not found, skipping Kubernetes deployment"
        return 0
    fi

    # Deploy basic Kubernetes resources
    log_info "Applying Kubernetes manifests..."

    if [[ -f "namespace.yaml" ]]; then
        kubectl apply -f namespace.yaml
    fi

    if [[ -f "deployment.yaml" ]]; then
        kubectl apply -f deployment.yaml
    fi

    if [[ -f "service.yaml" ]]; then
        kubectl apply -f service.yaml
    fi

    log_success "Kubernetes deployment completed"
}

# Generate deployment summary
generate_summary() {
    log_step "📊 Deployment Summary"

    cd "$PROJECT_ROOT/terraform"

    log_info "Deployment Details:"
    log_info "  Environment: $ENVIRONMENT"
    log_info "  Profile: $PROFILE"
    log_info "  Region: ${AWS_REGION:-us-west-2}"
    log_info "  Terraform State: $(pwd)/terraform.tfstate"

    # Show key outputs if available
    if terraform output >/dev/null 2>&1; then
        echo
        log_info "Key Infrastructure Outputs:"
        terraform output 2>/dev/null | head -10 || true
    fi

    if [[ "$DRY_RUN" == "false" ]]; then
        log_success "✅ Infrastructure deployment completed successfully!"
        log_info "Next steps:"
        log_info "  1. Deploy application: ./scripts/deploy-app.sh --environment $ENVIRONMENT --profile $PROFILE"
        log_info "  2. Run integration tests: ./scripts/test-integration.sh --environment $ENVIRONMENT"
        log_info "  3. When done, cleanup: ./scripts/destroy.sh --environment $ENVIRONMENT --profile $PROFILE"
    else
        log_success "✅ Infrastructure plan validation completed!"
        log_info "Remove --dry-run flag to apply changes"
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
    printf "${BLUE}🚀 Infrastructure Deployment Script${NC}\n"
    printf "${BLUE}===================================${NC}\n"
    echo
    log_info "Deploying to: $ENVIRONMENT environment with $PROFILE profile"
    echo

    # Execute deployment steps
    setup_environment
    check_prerequisites
    deploy_infrastructure
    deploy_kubernetes
    generate_summary

    # Return to original directory
    cd "$PROJECT_ROOT"
}

# Run main function
main "$@"