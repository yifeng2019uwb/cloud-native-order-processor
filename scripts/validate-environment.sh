#!/bin/bash
# File: scripts/validate-environment.sh
# Overall environment validation
# Comprehensive validation orchestrator
# Project structure checks (directories and files)
# Terraform setup validation (init, validate, workspace)
# AWS setup verification (permissions, state bucket)
# Configuration validation with YAML syntax checking
# Command-line interface with help and options

set -euo pipefail

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SHARED_DIR="${SCRIPT_DIR}/shared"

# Source shared utilities
# shellcheck source=shared/logging-utils.sh
source "${SHARED_DIR}/logging-utils.sh"
# shellcheck source=shared/environment-loader.sh
source "${SHARED_DIR}/environment-loader.sh"
# shellcheck source=shared/aws-utils.sh
source "${SHARED_DIR}/aws-utils.sh"
# shellcheck source=shared/error-handler.sh
source "${SHARED_DIR}/error-handler.sh"
# shellcheck source=shared/prerequisites-checker.sh
source "${SHARED_DIR}/prerequisites-checker.sh"

# Script configuration
SCRIPT_NAME="validate-environment"
VERSION="1.0.0"

# Usage information
show_usage() {
    cat << EOF
Usage: ${0} [OPTIONS]

Overall environment validation for cloud-native order processor

OPTIONS:
    -e, --environment ENV    Target environment (local, dev, staging, ci)
    -s, --skip-optional     Skip optional tool checks
    -v, --verbose           Enable verbose output
    -d, --debug             Enable debug mode
    -h, --help              Show this help message

EXAMPLES:
    ${0}                    # Auto-detect environment and validate
    ${0} --environment dev  # Validate development environment
    ${0} --verbose          # Validate with verbose output
    ${0} --skip-optional    # Skip optional tools check

ENVIRONMENT VARIABLES:
    ENVIRONMENT             Target environment (auto-detected if not set)
    DEBUG_MODE              Enable debug mode (true/false)
    TEST_VERBOSE            Enable verbose testing (true/false)
    SKIP_PREREQUISITES_CHECK Skip prerequisites check (true/false)

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
            -s|--skip-optional)
                SKIP_OPTIONAL="true"
                shift
                ;;
            -v|--verbose)
                TEST_VERBOSE="true"
                LOG_LEVEL="INFO"
                shift
                ;;
            -d|--debug)
                DEBUG_MODE="true"
                LOG_LEVEL="DEBUG"
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

# Validate project structure
validate_project_structure() {
    log_subsection "Project Structure Validation"

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
            log_debug "✓ Directory exists: ${dir}"
        else
            log_warn "✗ Directory missing: ${dir}"
            missing_dirs+=("${dir}")
        fi
    done

    local required_files=(
        "terraform/main.tf"
        "config/shared-config.yaml"
        "config/environments/.env.defaults"
        ".github/workflows/ci-cd.yaml"
        "README.md"
    )

    local missing_files=()

    for file in "${required_files[@]}"; do
        local full_path="${PROJECT_ROOT}/${file}"
        if [[ -f "${full_path}" ]]; then
            log_debug "✓ File exists: ${file}"
        else
            log_warn "✗ File missing: ${file}"
            missing_files+=("${file}")
        fi
    done

    if [[ ${#missing_dirs[@]} -eq 0 && ${#missing_files[@]} -eq 0 ]]; then
        log_success "Project structure validation passed"
        return 0
    else
        log_warning "Project structure validation completed with warnings"
        if [[ ${#missing_dirs[@]} -gt 0 ]]; then
            log_warn "Missing directories: ${missing_dirs[*]}"
        fi
        if [[ ${#missing_files[@]} -gt 0 ]]; then
            log_warn "Missing files: ${missing_files[*]}"
        fi
        return 2  # Warning, not error
    fi
}

# Validate Terraform setup
validate_terraform_setup() {
    log_subsection "Terraform Setup Validation"

    local terraform_dir="${PROJECT_ROOT}/terraform"

    if [[ ! -d "${terraform_dir}" ]]; then
        log_error "Terraform directory not found: ${terraform_dir}"
        return 1
    fi

    pushd "${terraform_dir}" >/dev/null

    # Check if Terraform is initialized
    if [[ ! -d ".terraform" ]]; then
        log_warn "Terraform not initialized"
        log_info "Run 'terraform init' in the terraform directory"
    else
        log_success "Terraform is initialized"
    fi

    # Validate Terraform configuration
    if terraform validate >/dev/null 2>&1; then
        log_success "Terraform configuration is valid"
    else
        log_error "Terraform configuration validation failed"
        log_error "Run 'terraform validate' for details"
        popd >/dev/null
        return 1
    fi

    # Check if workspace exists
    local workspace="${TERRAFORM_WORKSPACE:-${ENVIRONMENT}}"
    if terraform workspace list | grep -q "${workspace}"; then
        log_success "Terraform workspace '${workspace}' exists"
    else
        log_warn "Terraform workspace '${workspace}' does not exist"
        log_info "It will be created during deployment"
    fi

    popd >/dev/null
    return 0
}

# Validate AWS setup
validate_aws_setup() {
    log_subsection "AWS Setup Validation"

    # Check AWS credentials (already done in prerequisites)
    if ! check_aws_credentials; then
        return 1
    fi

    # Check AWS region availability
    local region
    region=$(get_aws_region)

    if ! check_aws_region_availability "${region}"; then
        log_error "AWS region '${region}' is not available"
        return 1
    fi

    # Check Terraform state bucket
    local bucket_name="${RESOURCE_PREFIX}-${TERRAFORM_BACKEND_BUCKET_SUFFIX}"

    if check_s3_bucket_exists "${bucket_name}"; then
        log_success "Terraform state bucket exists: ${bucket_name}"
    else
        log_warn "Terraform state bucket does not exist: ${bucket_name}"
        log_info "It will be created during deployment"
    fi

    # Check permissions by listing some basic AWS resources
    log_debug "Checking AWS permissions..."

    if aws ec2 describe-regions --region "${region}" >/dev/null 2>&1; then
        log_debug "✓ EC2 permissions available"
    else
        log_warn "Limited EC2 permissions detected"
    fi

    if aws iam get-user >/dev/null 2>&1 || aws sts get-caller-identity >/dev/null 2>&1; then
        log_debug "✓ IAM permissions available"
    else
        log_warn "Limited IAM permissions detected"
    fi

    log_success "AWS setup validation completed"
    return 0
}

# Validate configuration
validate_configuration() {
    log_subsection "Configuration Validation"

    # Environment configuration already loaded and validated
    log_success "Environment configuration is valid"

    # Check shared configuration file
    local shared_config="${CONFIG_DIR}/shared-config.yaml"

    if [[ ! -f "${shared_config}" ]]; then
        log_error "Shared configuration file not found: ${shared_config}"
        return 1
    fi

    # Validate YAML syntax
    if command -v python3 >/dev/null 2>&1; then
        if python3 -c "import yaml; yaml.safe_load(open('${shared_config}'))" 2>/dev/null; then
            log_success "Shared configuration YAML is valid"
        else
            log_error "Shared configuration YAML syntax error"
            return 1
        fi
    else
        log_debug "Python not available, skipping YAML syntax validation"
    fi

    # Environment-specific validations
    case "${ENVIRONMENT}" in
        "staging")
            if [[ "${STAGING_CONFIGURED:-false}" == "false" ]]; then
                log_warning "Staging environment is not configured yet"
                log_info "This is expected for single AWS account setup"
                return 2  # Warning, not error
            fi
            ;;
        "ci")
            if [[ -z "${GITHUB_ACTIONS:-}" ]]; then
                log_warn "CI environment specified but not running in GitHub Actions"
            fi
            ;;
    esac

    return 0
}

# Main validation function
main() {
    local skip_optional="${SKIP_OPTIONAL:-false}"
    local exit_code=0

    # Initialize logging
    init_logging

    # Setup error handling
    setup_error_handling

    log_section "Environment Validation - ${SCRIPT_NAME} v${VERSION}"

    # Load and validate environment configuration
    if ! load_environment_config "${ENVIRONMENT:-}"; then
        log_error "Failed to load environment configuration"
        exit 1
    fi

    if ! validate_environment_config; then
        case $? in
            1)
                log_error "Environment configuration validation failed"
                exit 1
                ;;
            2)
                log_warn "Environment configuration validation completed with warnings"
                exit_code=2
                ;;
        esac
    fi

    # Print environment summary
    print_environment_summary

    # Run validation checks
    log_info "Starting comprehensive environment validation..."

    # 1. Prerequisites check
    if [[ "${SKIP_PREREQUISITES_CHECK:-false}" != "true" ]]; then
        if ! check_all_prerequisites "${skip_optional}"; then
            log_error "Prerequisites check failed"
            exit_code=1
        fi
    else
        log_info "Skipping prerequisites check (SKIP_PREREQUISITES_CHECK=true)"
    fi

    # 2. Project structure validation
    if ! validate_project_structure; then
        case $? in
            1)
                log_error "Project structure validation failed"
                exit_code=1
                ;;
            2)
                if [[ ${exit_code} -eq 0 ]]; then
                    exit_code=2
                fi
                ;;
        esac
    fi

    # 3. Terraform setup validation
    if ! validate_terraform_setup; then
        log_error "Terraform setup validation failed"
        exit_code=1
    fi

    # 4. AWS setup validation
    if ! validate_aws_setup; then
        log_error "AWS setup validation failed"
        exit_code=1
    fi

    # 5. Configuration validation
    if ! validate_configuration; then
        case $? in
            1)
                log_error "Configuration validation failed"
                exit_code=1
                ;;
            2)
                if [[ ${exit_code} -eq 0 ]]; then
                    exit_code=2
                fi
                ;;
        esac
    fi

    # Final summary
    log_section "Validation Summary"

    case ${exit_code} in
        0)
            log_success "All validations passed successfully"
            log_info "Environment '${ENVIRONMENT}' is ready for infrastructure testing"
            ;;
        1)
            log_failure "Validation failed"
            log_error "Please fix the issues above before proceeding"
            ;;
        2)
            log_warning "Validation completed with warnings"
            log_info "Environment '${ENVIRONMENT}' should work but may have limitations"
            ;;
    esac

    exit ${exit_code}
}

# Set default values
SKIP_OPTIONAL="${SKIP_OPTIONAL:-false}"
DEBUG_MODE="${DEBUG_MODE:-false}"
TEST_VERBOSE="${TEST_VERBOSE:-false}"

# Parse command line arguments
parse_arguments "$@"

# Export environment variables
export DEBUG_MODE TEST_VERBOSE SKIP_OPTIONAL

# Run main function
main