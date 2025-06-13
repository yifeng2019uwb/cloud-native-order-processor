#!/bin/bash
# scripts/deploy.sh
# Enhanced Infrastructure Deployment Script
# Supports environments (dev/prod) and profiles (minimum/regular)

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

Usage: $0 --environment {dev|prod} --profile {minimum|regular} [OPTIONS]

Deploy AWS infrastructure using Terraform with environment and profile support.

REQUIRED:
    --environment {dev|prod}           Target environment
    --profile {minimum|regular}        Resource profile

PROFILES:
    minimum    - Lambda + API Gateway (cheapest for testing)
    regular    - EKS + Kubernetes (full production-like)

OPTIONS:
    -v, --verbose                      Enable verbose output
    --dry-run                         Show what would happen (terraform plan only)
    -h, --help                        Show this help message

EXAMPLES:
    $0 --environment dev --profile minimum      # Deploy cheap Lambda setup
    $0 --environment dev --profile regular      # Deploy full EKS setup
    $0 --environment prod --profile regular     # Deploy production setup
    $0 --environment dev --profile minimum --dry-run  # Plan only

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
    elif [[ "$PROFILE" != "minimum" && "$PROFILE" != "regular" ]]; then
        errors+=("--profile must be 'minimum' or 'regular'")
    fi

    # Validate environment/profile combinations
    if [[ "$ENVIRONMENT" == "prod" && "$PROFILE" != "regular" ]]; then
        log_warning "Production environment with minimum profile - are you sure?"
        log_warning "Consider using regular profile for production-like testing"
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
    export PROFILE="$PROFILE"
    export TF_VAR_environment="$ENVIRONMENT"
    export TF_VAR_profile="$PROFILE"

    # Load environment-specific configuration
    local env_config="$PROJECT_ROOT/config/environments/.env.defaults"
    if [[ -f "$env_config" ]]; then
        log_info "Loading default configuration: $env_config"
        source "$env_config"
    else
        log_warning "Default configuration not found: $env_config"
    fi

    # Load environment-specific overrides
    local env_override="$PROJECT_ROOT/config/environments/.env.${ENVIRONMENT}"
    if [[ -f "$env_override" ]]; then
        log_info "Loading environment overrides: $env_override"
        source "$env_override"
    fi

    # Set additional Terraform variables
    export TF_VAR_region="${AWS_REGION:-us-west-2}"
    export TF_IN_AUTOMATION=true

    # Profile-specific settings
    case "$PROFILE" in
        "minimum")
            export TF_VAR_compute_type="lambda"
            export TF_VAR_instance_sizes="micro"
            log_info "Using Lambda + API Gateway (minimum cost)"
            ;;
        "regular")
            export TF_VAR_compute_type="kubernetes"
            export TF_VAR_instance_sizes="small"
            log_info "Using EKS + Kubernetes (full infrastructure)"
            ;;
    esac

    if [[ "$VERBOSE" == "true" ]]; then
        log_info "Environment variables set:"
        log_info "  ENVIRONMENT: $ENVIRONMENT"
        log_info "  PROFILE: $PROFILE"
        log_info "  COMPUTE_TYPE: ${TF_VAR_compute_type}"
        log_info "  AWS_REGION: ${TF_VAR_region}"
    fi
}

# Install Terraform if not already installed
install_terraform() {
    log_step "🔧 Installing Terraform"

    # Check if terraform is already installed
    if command -v terraform &> /dev/null; then
        local terraform_version=$(terraform version -json | jq -r '.terraform_version' 2>/dev/null || terraform version | head -1 | cut -d' ' -f2 | sed 's/v//')
        log_info "Terraform already installed: $terraform_version"
        return 0
    fi

    log_info "Terraform not found, installing..."

    # Detect OS and architecture
    local os=$(uname -s | tr '[:upper:]' '[:lower:]')
    local arch=$(uname -m)

    # Map architecture names
    case $arch in
        x86_64) arch="amd64" ;;
        aarch64|arm64) arch="arm64" ;;
        armv7l) arch="arm" ;;
        *)
            log_error "Unsupported architecture: $arch"
            exit 1
            ;;
    esac

    # Set Terraform version
    local terraform_version="1.7.5"
    local download_url="https://releases.hashicorp.com/terraform/${terraform_version}/terraform_${terraform_version}_${os}_${arch}.zip"
    local install_dir="/usr/local/bin"

    # For CI environments, use local bin directory
    if [[ "$CI" == "true" || "$GITHUB_ACTIONS" == "true" ]]; then
        install_dir="$HOME/.local/bin"
        mkdir -p "$install_dir"
        export PATH="$install_dir:$PATH"
    fi

    log_info "Downloading Terraform $terraform_version for $os/$arch..."

    # Create temporary directory
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"

    # Download and install
    if command -v curl &> /dev/null; then
        curl -sL "$download_url" -o terraform.zip
    elif command -v wget &> /dev/null; then
        wget -q "$download_url" -O terraform.zip
    else
        log_error "Neither curl nor wget found. Cannot download Terraform."
        exit 1
    fi

    # Verify download succeeded
    if [[ ! -f terraform.zip ]]; then
        log_error "Failed to download Terraform"
        exit 1
    fi

    # Extract and install
    unzip -q terraform.zip

    # Install with appropriate permissions
    if [[ "$install_dir" == "/usr/local/bin" ]]; then
        sudo mv terraform "$install_dir/"
        sudo chmod +x "$install_dir/terraform"
    else
        mv terraform "$install_dir/"
        chmod +x "$install_dir/terraform"
    fi

    # Cleanup
    cd - > /dev/null
    rm -rf "$temp_dir"

    # Verify installation
    if command -v terraform &> /dev/null; then
        local installed_version=$(terraform version -json | jq -r '.terraform_version' 2>/dev/null || terraform version | head -1 | cut -d' ' -f2 | sed 's/v//')
        log_info "✅ Terraform installed successfully: $installed_version"
    else
        log_error "❌ Terraform installation failed"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_step "🔍 Checking Prerequisites"

    # Debug: Show current PATH and terraform status
    if [[ "$VERBOSE" == "true" ]]; then
        log_info "Current PATH: $PATH"
        log_info "Checking terraform availability..."
    fi

    if ! command -v terraform &> /dev/null; then
        log_info "Terraform not found, installing..."
        install_terraform

        # Verify terraform is now available
        if command -v terraform &> /dev/null; then
            log_success "✅ Terraform now available at: $(which terraform)"
        else
            log_error "❌ Terraform still not found after installation"
            exit 1
        fi
    else
        log_success "✅ Terraform available at: $(which terraform)"
    fi

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

# Show cost estimate
show_cost_estimate() {
    log_step "💰 Cost Estimate"

    case "$PROFILE" in
        "minimum")
            log_info "Lambda + API Gateway Profile:"
            log_info "  💸 Lambda: ~$0.01/day (usage-based)"
            log_info "  💸 API Gateway: ~$0.01/day (usage-based)"
            log_info "  💸 RDS: ~$0.50-1.00/day (db.t3.micro)"
            log_info "  💸 Total: ~$0.52-1.02/day"
            log_success "✅ Cost-optimized for testing"
            ;;
        "regular")
            log_warning "EKS + Kubernetes Profile:"
            log_warning "  💸 EKS Cluster: ~$17.52/day ($0.73/hour)"
            log_warning "  💸 Worker Nodes: ~$1.20-2.40/day"
            log_warning "  💸 RDS: ~$0.50-1.00/day"
            log_warning "  💸 Load Balancer: ~$0.50/day"
            log_warning "  💸 Total: ~$19.72-21.42/day"
            log_warning "⚠️  Higher cost for full infrastructure testing"
            ;;
    esac

    if [[ "$DRY_RUN" == "false" ]]; then
        echo
        log_info "💡 Cost Control Tips:"
        log_info "  - Use --dry-run to preview changes"
        log_info "  - Run destroy.sh --force when done testing"
        log_info "  - Use minimum profile for daily development"
        log_info "  - Use regular profile for pre-push validation"
    fi
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
    local plan_args="-var=profile=$PROFILE -var=environment=$ENVIRONMENT -var=compute_type=${TF_VAR_compute_type}"

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

# Generate deployment summary
generate_summary() {
    log_step "📊 Deployment Summary"

    cd "$PROJECT_ROOT/terraform"

    log_info "Deployment Details:"
    log_info "  Environment: $ENVIRONMENT"
    log_info "  Profile: $PROFILE"
    log_info "  Compute Type: ${TF_VAR_compute_type}"
    log_info "  Region: ${TF_VAR_region}"
    log_info "  Terraform State: $(pwd)/terraform.tfstate"

    # Show key outputs if available
    if terraform output >/dev/null 2>&1; then
        echo
        log_info "Key Infrastructure Outputs:"

        # Profile-specific outputs
        case "$PROFILE" in
            "minimum")
                if terraform output api_gateway_url >/dev/null 2>&1; then
                    local api_url=$(terraform output -raw api_gateway_url)
                    log_info "  API Gateway URL: $api_url"
                fi
                if terraform output lambda_function_name >/dev/null 2>&1; then
                    local lambda_name=$(terraform output -raw lambda_function_name)
                    log_info "  Lambda Function: $lambda_name"
                fi
                ;;
            "regular")
                if terraform output eks_cluster_name >/dev/null 2>&1; then
                    local cluster_name=$(terraform output -raw eks_cluster_name)
                    log_info "  EKS Cluster: $cluster_name"
                fi
                if terraform output eks_cluster_endpoint >/dev/null 2>&1; then
                    local cluster_endpoint=$(terraform output -raw eks_cluster_endpoint)
                    log_info "  EKS Endpoint: $cluster_endpoint"
                fi
                ;;
        esac

        # Common outputs
        if terraform output database_endpoint >/dev/null 2>&1; then
            local db_endpoint=$(terraform output -raw database_endpoint)
            log_info "  Database: $db_endpoint"
        fi
    fi

    if [[ "$DRY_RUN" == "false" ]]; then
        log_success "✅ Infrastructure deployment completed successfully!"
        log_info "Next steps:"
        case "$PROFILE" in
            "minimum")
                log_info "  1. Deploy application: ./scripts/deploy-app.sh --environment $ENVIRONMENT --profile $PROFILE"
                log_info "  2. Test via API Gateway URL"
                ;;
            "regular")
                log_info "  1. Deploy application: ./scripts/deploy-app.sh --environment $ENVIRONMENT --profile $PROFILE"
                log_info "  2. Configure kubectl for EKS cluster"
                ;;
        esac
        log_info "  3. Run integration tests: ./scripts/test-integration.sh --environment $ENVIRONMENT --profile $PROFILE"
        log_info "  4. When done, cleanup: ./scripts/destroy.sh --environment $ENVIRONMENT --profile $PROFILE --force"
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

    # Show cost estimate
    show_cost_estimate

    # Execute deployment steps
    setup_environment
    check_prerequisites
    deploy_infrastructure
    generate_summary

    # Return to original directory
    cd "$PROJECT_ROOT"
}

# Run main function
main "$@"