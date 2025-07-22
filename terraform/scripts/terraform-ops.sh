#!/bin/bash
# File: terraform/scripts/terraform-ops.sh
# Terraform Operations Script - Convenient commands for common Terraform tasks
# Usage: ./terraform-ops.sh [command] [options]

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${TERRAFORM_DIR}/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Default values
ENVIRONMENT="dev"
VERBOSE="false"
AUTO_APPROVE="false"
PLAN_ONLY="false"

# Help function
show_help() {
    cat << EOF
Terraform Operations Script

Usage: $0 [COMMAND] [OPTIONS]

COMMANDS:
    init          Initialize Terraform workspace
    plan          Create Terraform plan
    apply         Apply Terraform changes
    destroy       Destroy Terraform resources
    validate      Validate Terraform configuration
    fmt           Format Terraform files
    refresh       Refresh Terraform state
    output        Show Terraform outputs
    state         Manage Terraform state
    test          Run infrastructure tests
    clean         Clean Terraform files and state

OPTIONS:
    -e, --environment ENV    Environment (dev/prod) [default: dev]
    -v, --verbose           Enable verbose output
    -y, --auto-approve      Auto-approve changes (use with caution)
    -p, --plan-only         Only create plan, don't apply
    -h, --help              Show this help message

EXAMPLES:
    $0 init -e dev
    $0 plan -e prod -v
    $0 apply -e dev -y
    $0 destroy -e dev -v
    $0 test -e dev

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            init|plan|apply|destroy|validate|fmt|refresh|output|state|test|clean)
                COMMAND="$1"
                shift
                ;;
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            -y|--auto-approve)
                AUTO_APPROVE="true"
                shift
                ;;
            -p|--plan-only)
                PLAN_ONLY="true"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Validate environment
validate_environment() {
    if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
        log_error "Invalid environment: $ENVIRONMENT. Must be 'dev' or 'prod'"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if terraform is installed
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed"
        exit 1
    fi

    # Check terraform version
    local tf_version=$(terraform version -json | jq -r '.terraform_version')
    log_info "Terraform version: $tf_version"

    # Check if we're in the right directory
    if [[ ! -f "${TERRAFORM_DIR}/main.tf" ]]; then
        log_error "Not in Terraform directory. Please run from terraform/ directory"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Initialize Terraform
terraform_init() {
    log_info "Initializing Terraform for environment: $ENVIRONMENT"

    cd "$TERRAFORM_DIR"

    # Initialize with backend configuration
    terraform init \
        -backend-config="key=${ENVIRONMENT}/terraform.tfstate" \
        -backend-config="bucket=order-processor-terraform-state" \
        -backend-config="region=us-west-2"

    log_success "Terraform initialized successfully"
}

# Create Terraform plan
terraform_plan() {
    log_info "Creating Terraform plan for environment: $ENVIRONMENT"

    cd "$TERRAFORM_DIR"

    local plan_file="terraform-${ENVIRONMENT}.plan"

    # Create plan
    terraform plan \
        -var="environment=${ENVIRONMENT}" \
        -out="$plan_file"

    log_success "Plan created: $plan_file"

    if [[ "$PLAN_ONLY" == "true" ]]; then
        log_info "Plan-only mode: stopping here"
        exit 0
    fi
}

# Apply Terraform changes
terraform_apply() {
    log_info "Applying Terraform changes for environment: $ENVIRONMENT"

    cd "$TERRAFORM_DIR"

    local plan_file="terraform-${ENVIRONMENT}.plan"

    # Check if plan file exists
    if [[ ! -f "$plan_file" ]]; then
        log_warning "Plan file not found. Creating new plan..."
        terraform_plan
    fi

    # Apply changes
    if [[ "$AUTO_APPROVE" == "true" ]]; then
        terraform apply -auto-approve "$plan_file"
    else
        terraform apply "$plan_file"
    fi

    # Clean up plan file
    rm -f "$plan_file"

    log_success "Terraform changes applied successfully"
}

# Destroy Terraform resources
terraform_destroy() {
    log_warning "Destroying Terraform resources for environment: $ENVIRONMENT"

    if [[ "$AUTO_APPROVE" != "true" ]]; then
        read -p "Are you sure you want to destroy all resources? (yes/no): " confirm
        if [[ "$confirm" != "yes" ]]; then
            log_info "Destroy cancelled"
            exit 0
        fi
    fi

    cd "$TERRAFORM_DIR"

    terraform destroy \
        -var="environment=${ENVIRONMENT}" \
        -auto-approve
}

# Validate Terraform configuration
terraform_validate() {
    log_info "Validating Terraform configuration"

    cd "$TERRAFORM_DIR"

    terraform validate

    log_success "Terraform configuration is valid"
}

# Format Terraform files
terraform_fmt() {
    log_info "Formatting Terraform files"

    cd "$TERRAFORM_DIR"

    terraform fmt -recursive

    log_success "Terraform files formatted"
}

# Refresh Terraform state
terraform_refresh() {
    log_info "Refreshing Terraform state"

    cd "$TERRAFORM_DIR"

    terraform refresh -var="environment=${ENVIRONMENT}"

    log_success "Terraform state refreshed"
}

# Show Terraform outputs
terraform_output() {
    log_info "Showing Terraform outputs for environment: $ENVIRONMENT"

    cd "$TERRAFORM_DIR"

    terraform output
}

# Manage Terraform state
terraform_state() {
    log_info "Managing Terraform state"

    cd "$TERRAFORM_DIR"

    terraform state list
}

# Run infrastructure tests
terraform_test() {
    log_info "Running infrastructure tests for environment: $ENVIRONMENT"

    # Run the infrastructure test script
    if [[ -f "${TERRAFORM_DIR}/run-infrastructure-tests.sh" ]]; then
        "${TERRAFORM_DIR}/run-infrastructure-tests.sh" \
            --environment "$ENVIRONMENT" \
            --verbose
    else
        log_error "Infrastructure test script not found"
        exit 1
    fi
}

# Clean Terraform files
terraform_clean() {
    log_info "Cleaning Terraform files and state"

    cd "$TERRAFORM_DIR"

    # Remove plan files
    rm -f terraform-*.plan

    # Remove .terraform directory
    rm -rf .terraform

    # Remove terraform.tfstate files (be careful!)
    if [[ "$AUTO_APPROVE" == "true" ]]; then
        rm -f terraform.tfstate*
    else
        log_warning "To remove state files, use --auto-approve flag"
    fi

    log_success "Terraform files cleaned"
}

# Main function
main() {
    # Parse arguments
    parse_args "$@"

    # Validate environment
    validate_environment

    # Check prerequisites
    check_prerequisites

    # Execute command
    case "$COMMAND" in
        init)
            terraform_init
            ;;
        plan)
            terraform_plan
            ;;
        apply)
            terraform_apply
            ;;
        destroy)
            terraform_destroy
            ;;
        validate)
            terraform_validate
            ;;
        fmt)
            terraform_fmt
            ;;
        refresh)
            terraform_refresh
            ;;
        output)
            terraform_output
            ;;
        state)
            terraform_state
            ;;
        test)
            terraform_test
            ;;
        clean)
            terraform_clean
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"