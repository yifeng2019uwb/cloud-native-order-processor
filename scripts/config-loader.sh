#!/bin/bash
# scripts/config-loader.sh
# Simple configuration loader for Cloud Native Order Processor

# Source logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/logging.sh"

# Default configuration
DEFAULT_ENVIRONMENT="dev"
DEFAULT_NAMESPACE="default"

# Environment configurations
ENV_CONFIGS=(
    "dev:docker:8080:3000"
    "prod:kubernetes:443:80"
)

# Component configurations
COMPONENT_CONFIGS=(
    "frontend:3000:80"
    "gateway:8080:443"
    "user-service:8001:80"
    "inventory-service:8002:80"
    "order-service:8003:80"
)

# Load environment configuration
load_env() {
    local env="${1:-$DEFAULT_ENVIRONMENT}"

    log_info "Loading environment: $env"

    # Set basic environment variables
    export ENVIRONMENT="$env"
    export NAMESPACE="$DEFAULT_NAMESPACE"

    # Set component ports based on environment
    for comp_config in "${COMPONENT_CONFIGS[@]}"; do
        IFS=':' read -ra parts <<< "$comp_config"
        local component="${parts[0]}"
        local dev_port="${parts[1]}"
        local prod_port="${parts[2]}"

        if [[ "$env" == "dev" ]]; then
            export "$(echo "$component" | tr '[:lower:]' '[:upper:]' | tr '-' '_')_PORT"="$dev_port"
        else
            export "$(echo "$component" | tr '[:lower:]' '[:upper:]' | tr '-' '_')_PORT"="$prod_port"
        fi
    done

    log_success "Environment loaded: $env"
}

# Get component port
get_port() {
    local component="$1"
    local env="${2:-$DEFAULT_ENVIRONMENT}"

    local env_var="$(echo "$component" | tr '[:lower:]' '[:upper:]' | tr '-' '_')_PORT"
    if [[ -n "${!env_var:-}" ]]; then
        echo "${!env_var}"
    else
        log_error "Port not found for component: $component"
        return 1
    fi
}

# List environments
list_envs() {
    log_info "Available environments:"
    for env_config in "${ENV_CONFIGS[@]}"; do
        IFS=':' read -ra parts <<< "$env_config"
        local env="${parts[0]}"
        local platform="${parts[1]}"
        printf "  - %s (%s)\n" "$env" "$platform"
    done
}

# List components
list_components() {
    log_info "Available components:"
    for comp_config in "${COMPONENT_CONFIGS[@]}"; do
        IFS=':' read -ra parts <<< "$comp_config"
        local component="${parts[0]}"
        local dev_port="${parts[1]}"
        local prod_port="${parts[2]}"
        printf "  - %s (dev:%s/prod:%s)\n" "$component" "$dev_port" "$prod_port"
    done
}

# Main function
main() {
    local command="${1:-list}"
    local env="${2:-$DEFAULT_ENVIRONMENT}"

    case "$command" in
        "load")
            load_env "$env"
            ;;
        "list")
            list_envs
            echo
            list_components
            ;;
        "port")
            if [[ -n "$3" ]]; then
                get_port "$3" "$env"
            else
                log_error "Usage: $0 port <component> [environment]"
                exit 1
            fi
            ;;
        *)
            log_error "Unknown command: $command"
            log_info "Usage: $0 {load|list|port} [environment]"
            exit 1
            ;;
    esac
}

# Export functions for use in other scripts
export -f load_env get_port list_envs list_components

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
