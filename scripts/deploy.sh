#!/bin/bash
# scripts/deploy.sh
# Enhanced Infrastructure Deployment Script
# Supports environments (dev/prod)

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

# Usage function
show_usage() {
    cat << EOF
$(printf "${BLUE}🚀 Infrastructure Deployment Script${NC}")

Usage: $0 --environment {dev|prod} [OPTIONS]

Deploy AWS infrastructure using Terraform with environment support.

REQUIRED:
    --environment {dev|prod}           Target environment

OPTIONS:
    -v, --verbose                      Enable verbose output
    --dry-run                         Show what would happen (terraform plan only)
    -h, --help                        Show this help message

EXAMPLES:
    $0 --environment dev     # Deploy development setup
    $0 --environment prod    # Deploy production setup

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

# Set environment variables based on environment
setup_environment() {
    log_step "🔧 Setting up environment: $ENVIRONMENT"

    # Set base environment variables
    export ENVIRONMENT="$ENVIRONMENT"
    export TF_VAR_environment="$ENVIRONMENT"

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

    if [[ "$VERBOSE" == "true" ]]; then
        log_info "Environment variables set:"
        log_info "  ENVIRONMENT: $ENVIRONMENT"
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

    if [[ "$DRY_RUN" == "false" ]]; then
        echo
        log_info "💡 Cost Control Tips:"
        log_info "  - Use --dry-run to preview changes"
        log_info "  - Run destroy.sh --force when done testing"
        log_info "  - Use devfor daily development"
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
    local plan_args="-var=environment=$ENVIRONMENT"

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
    log_info "  Region: ${TF_VAR_region}"
    log_info "  Terraform State: $(pwd)/terraform.tfstate"

    # Show key outputs if available
    if terraform output >/dev/null 2>&1; then
        echo
        log_info "Key Infrastructure Outputs:"

        # Common outputs
        if terraform output database_endpoint >/dev/null 2>&1; then
            local db_endpoint=$(terraform output -raw database_endpoint)
            log_info "  Database: $db_endpoint"
        fi
    fi

    if [[ "$DRY_RUN" == "false" ]]; then
        log_success "✅ Infrastructure deployment completed successfully!"
        log_info "Next steps:"
        log_info "  3. Run integration tests: ./scripts/test-integration.sh --environment $ENVIRONMENT"
        log_info "  4. When done, cleanup: ./scripts/destroy.sh --environment $ENVIRONMENT --force"
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
    log_info "Deploying to: $ENVIRONMENT environment"
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