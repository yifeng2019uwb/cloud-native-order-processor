#!/bin/bash
# File: scripts/validate-environment.sh
# Simplified environment validation
# Basic validation for dev/prod environments with minimum/regular profiles

set -euo pipefail

# Get script directory and project root
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

log_section() {
    printf "\n${BLUE}=== %s ===${NC}\n" "$1"
}

# Usage information
show_usage() {
    cat << EOF
Usage: ${0} [OPTIONS]

Simplified environment validation for cloud-native order processor

OPTIONS:
    -e, --environment ENV    Target environment (dev|prod)
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

EXAMPLES:
    ${0} --environment dev     # Validate development environment
    ${0} --environment prod    # Validate production environment
    ${0} --verbose             # Auto-detect environment with verbose output

EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
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

# Auto-detect environment if not provided
detect_environment() {
    if [[ -n "${ENVIRONMENT}" ]]; then
        return 0
    fi

    # Simple detection logic
    if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
        ENVIRONMENT="prod"
    else
        ENVIRONMENT="dev"
    fi

    log_info "Auto-detected environment: ${ENVIRONMENT}"
}

# Validate environment
validate_environment() {
    if [[ "${ENVIRONMENT}" != "dev" && "${ENVIRONMENT}" != "prod" ]]; then
        log_error "Environment must be 'dev' or 'prod', got: ${ENVIRONMENT}"
        return 1
    fi

    log_success "Environment '${ENVIRONMENT}' is valid"
    return 0
}

# Check required tools
check_tools() {
    log_section "Checking Required Tools"

    local missing_tools=()
    local tools=("terraform" "aws" "docker" "jq" "git")

    for tool in "${tools[@]}"; do
        if command -v "${tool}" >/dev/null 2>&1; then
            if [[ "${VERBOSE}" == "true" ]]; then
                log_success "${tool} is available"
            fi
        else
            missing_tools+=("${tool}")
        fi
    done

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Install missing tools and try again"
        return 1
    fi

    log_success "All required tools are available"
    return 0
}

# Validate project structure
validate_project_structure() {
    log_section "Validating Project Structure"

    local required_dirs=(
        "terraform"
        "services"
        "config"
        "scripts"
        ".github/workflows"
    )

    local missing_dirs=()

    for dir in "${required_dirs[@]}"; do
        local full_path="${PROJECT_ROOT}/${dir}"
        if [[ -d "${full_path}" ]]; then
            if [[ "${VERBOSE}" == "true" ]]; then
                log_success "Directory exists: ${dir}"
            fi
        else
            missing_dirs+=("${dir}")
        fi
    done

    local required_files=(
        "terraform/main.tf"
        "config/shared-config.yaml"
        ".github/workflows/ci-cd.yaml"
        "README.md"
    )

    local missing_files=()

    for file in "${required_files[@]}"; do
        local full_path="${PROJECT_ROOT}/${file}"
        if [[ -f "${full_path}" ]]; then
            if [[ "${VERBOSE}" == "true" ]]; then
                log_success "File exists: ${file}"
            fi
        else
            missing_files+=("${file}")
        fi
    done

    if [[ ${#missing_dirs[@]} -gt 0 ]]; then
        log_error "Missing directories: ${missing_dirs[*]}"
        return 1
    fi

    if [[ ${#missing_files[@]} -gt 0 ]]; then
        log_error "Missing files: ${missing_files[*]}"
        return 1
    fi

    log_success "Project structure is valid"
    return 0
}

# Check AWS credentials
check_aws_credentials() {
    log_section "Checking AWS Credentials"

    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        log_error "AWS credentials not configured or invalid"
        log_info "Please run 'aws configure' or set AWS environment variables"
        return 1
    fi

    if [[ "${VERBOSE}" == "true" ]]; then
        local account_id
        account_id=$(aws sts get-caller-identity --query Account --output text)
        log_info "AWS Account ID: ${account_id}"
    fi

    log_success "AWS credentials are valid"
    return 0
}

# Check AWS region
check_aws_region() {
    local region="${AWS_REGION:-us-west-2}"

    if ! aws ec2 describe-regions --region-names "${region}" >/dev/null 2>&1; then
        log_error "AWS region '${region}' is not available"
        return 1
    fi

    if [[ "${VERBOSE}" == "true" ]]; then
        log_info "AWS Region: ${region}"
    fi

    log_success "AWS region is valid"
    return 0
}

# Validate Terraform
validate_terraform() {
    log_section "Validating Terraform"

    local terraform_dir="${PROJECT_ROOT}/terraform"

    if [[ ! -d "${terraform_dir}" ]]; then
        log_error "Terraform directory not found: ${terraform_dir}"
        return 1
    fi

    pushd "${terraform_dir}" >/dev/null

    # Check if Terraform configuration is valid
    if ! terraform validate >/dev/null 2>&1; then
        log_error "Terraform configuration validation failed"
        log_info "Run 'terraform validate' in terraform directory for details"
        popd >/dev/null
        return 1
    fi

    # Check if initialized (optional)
    if [[ -d ".terraform" ]]; then
        if [[ "${VERBOSE}" == "true" ]]; then
            log_success "Terraform is initialized"
        fi
    else
        log_warning "Terraform not initialized (will be done during deployment)"
    fi

    popd >/dev/null
    log_success "Terraform configuration is valid"
    return 0
}

# Check configuration files
check_configuration() {
    log_section "Checking Configuration Files"

    local config_files=()

    # Check for environment-specific config
    case "${ENVIRONMENT}" in
        "dev")
            config_files+=("config/environments/.env.defaults")
            if [[ -f "config/environments/.env.dev" ]]; then
                config_files+=("config/environments/.env.dev")
            fi
            ;;
        "prod")
            config_files+=("config/environments/.env.defaults")
            # Prod uses CI environment in GitHub Actions
            ;;
    esac

    for config_file in "${config_files[@]}"; do
        if [[ -f "${PROJECT_ROOT}/${config_file}" ]]; then
            if [[ "${VERBOSE}" == "true" ]]; then
                log_success "Config file exists: ${config_file}"
            fi
        else
            log_error "Missing config file: ${config_file}"
            return 1
        fi
    done

    log_success "Configuration files are valid"
    return 0
}

# Main validation function
main() {
    local exit_code=0

    log_section "Environment Validation"

    # Parse arguments
    parse_arguments "$@"

    # Detect environment if not provided
    detect_environment

    # Validate environment
    if ! validate_environment; then
        exit_code=1
    fi

    log_info "Validating environment: ${ENVIRONMENT}"

    # Run validation checks
    if ! check_tools; then
        exit_code=1
    fi

    if ! validate_project_structure; then
        exit_code=1
    fi

    if ! check_aws_credentials; then
        exit_code=1
    fi

    if ! check_aws_region; then
        exit_code=1
    fi

    if ! validate_terraform; then
        exit_code=1
    fi

    if ! check_configuration; then
        exit_code=1
    fi

    # Final summary
    log_section "Validation Summary"

    if [[ ${exit_code} -eq 0 ]]; then
        log_success "All validations passed successfully"
        log_info "Environment '${ENVIRONMENT}' is ready for deployment"
    else
        log_error "Validation failed"
        log_info "Please fix the issues above before proceeding"
    fi

    exit ${exit_code}
}

# Run main function
main "$@"