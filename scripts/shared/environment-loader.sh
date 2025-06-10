#!/bin/bash
# File: scripts/shared/environment-loader.sh
# Load and validate environment configuration
# Auto-detects environment (local, dev, staging, ci)
# Loads configuration hierarchy: defaults → environment-specific → local overrides
# Validates required variables and environment-specific settings
# Handles staging placeholder (not configured yet)

set -euo pipefail

# Global variables (compatible with older Bash)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CONFIG_DIR="${PROJECT_ROOT}/config"
ENV_DIR="${CONFIG_DIR}/environments"

# Environment loading functions
load_environment_config() {
    local environment="${1:-}"
    local config_loaded=false

    # Determine environment if not provided
    if [[ -z "${environment}" ]]; then
        environment=$(detect_environment)
    fi

    log_info "Loading configuration for environment: ${environment}"

    # Load configuration files in order of precedence
    # 1. Load defaults first
    if [[ -f "${ENV_DIR}/.env.defaults" ]]; then
        log_debug "Loading default configuration from .env.defaults"
        # shellcheck source=/dev/null
        source "${ENV_DIR}/.env.defaults"
        config_loaded=true
    else
        log_warn "Default configuration file not found: ${ENV_DIR}/.env.defaults"
    fi

    # 2. Load environment-specific config
    local env_file="${ENV_DIR}/.env.${environment}"
    if [[ -f "${env_file}" ]]; then
        log_debug "Loading environment configuration from .env.${environment}"
        # shellcheck source=/dev/null
        source "${env_file}"
        config_loaded=true
    else
        log_warn "Environment configuration file not found: ${env_file}"
    fi

    # 3. Load local overrides (only for local/dev environments)
    local local_file="${ENV_DIR}/.env.local"
    if [[ -f "${local_file}" && ("${environment}" == "local" || "${environment}" == "dev") ]]; then
        log_debug "Loading local configuration overrides from .env.local"
        # shellcheck source=/dev/null
        source "${local_file}"
    fi

    # Set global environment variable
    export ENVIRONMENT="${environment}"

    # Validate that we loaded some configuration
    if [[ "${config_loaded}" != "true" ]]; then
        log_error "No configuration files could be loaded for environment: ${environment}"
        return 1
    fi

    log_info "Configuration loaded successfully for environment: ${environment}"
    return 0
}

detect_environment() {
    local detected_env="dev"  # Default fallback

    # Check environment variable first
    if [[ -n "${ENVIRONMENT:-}" ]]; then
        detected_env="${ENVIRONMENT}"
    # Check if running in GitHub Actions
    elif [[ -n "${GITHUB_ACTIONS:-}" ]]; then
        detected_env="ci"
    # Check if running locally with AWS profile
    elif [[ -n "${AWS_PROFILE:-}" ]]; then
        detected_env="local"
    # Check git branch for environment hints
    elif command -v git >/dev/null 2>&1; then
        local branch
        branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
        case "${branch}" in
            main|master) detected_env="dev" ;;
            staging*) detected_env="staging" ;;
            dev*|develop*) detected_env="dev" ;;
            *) detected_env="local" ;;
        esac
    fi

    log_debug "Detected environment: ${detected_env}"
    echo "${detected_env}"
}

validate_environment_config() {
    local environment="${ENVIRONMENT:-}"

    if [[ -z "${environment}" ]]; then
        log_error "Environment not set. Call load_environment_config first."
        return 1
    fi

    log_info "Validating configuration for environment: ${environment}"

    # Required variables validation
    local required_vars=(
        "PROJECT_NAME"
        "AWS_DEFAULT_REGION"
        "TERRAFORM_BACKEND_BUCKET_SUFFIX"
        "RESOURCE_PREFIX"
    )

    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("${var}")
        fi
    done

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            log_error "  - ${var}"
        done
        return 1
    fi

    # Environment-specific validations
    case "${environment}" in
        "staging")
            if [[ "${STAGING_CONFIGURED:-false}" == "false" ]]; then
                log_warn "Staging environment is not yet configured"
                log_warn "This is expected - staging will be set up when additional AWS account is available"
                return 2  # Warning but not error
            fi
            ;;
        "ci")
            validate_ci_config
            ;;
        "local"|"dev")
            validate_dev_config
            ;;
    esac

    log_info "Environment configuration validation completed successfully"
    return 0
}

validate_ci_config() {
    # CI-specific validations
    if [[ -z "${GITHUB_ACTIONS:-}" ]]; then
        log_warn "CI environment detected but not running in GitHub Actions"
    fi

    # Check for CI-required variables
    local ci_vars=("CI_MODE" "AUTOMATED_DEPLOYMENT")
    for var in "${ci_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_warn "CI variable not set: ${var}"
        fi
    done
}

validate_dev_config() {
    # Development-specific validations
    if [[ "${AUTO_CLEANUP_ENABLED:-false}" == "true" ]]; then
        log_warn "Auto-cleanup is enabled in development environment"
        log_warn "Resources will be automatically cleaned up"
    fi
}

print_environment_summary() {
    local environment="${ENVIRONMENT:-unknown}"

    log_info "=== Environment Configuration Summary ==="
    log_info "Environment: ${environment}"
    log_info "Project: ${PROJECT_NAME:-unknown}"
    log_info "AWS Region: ${AWS_DEFAULT_REGION:-unknown}"
    log_info "Resource Prefix: ${RESOURCE_PREFIX:-unknown}"
    log_info "Terraform Workspace: ${TERRAFORM_WORKSPACE:-unknown}"

    if [[ "${DEBUG_MODE:-false}" == "true" ]]; then
        log_debug "=== Debug Information ==="
        log_debug "Project Root: ${PROJECT_ROOT}"
        log_debug "Config Directory: ${CONFIG_DIR}"
        log_debug "Test Timeout: ${TEST_TIMEOUT:-unknown}"
        log_debug "Test Verbose: ${TEST_VERBOSE:-unknown}"
        log_debug "Cleanup Enabled: ${INFRA_TEST_CLEANUP:-unknown}"
    fi

    log_info "========================================="
}

# Export functions for use in other scripts
export -f load_environment_config
export -f detect_environment
export -f validate_environment_config
export -f print_environment_summary
