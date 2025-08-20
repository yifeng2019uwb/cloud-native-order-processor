#!/bin/bash
# scripts/prerequisites-checker.sh
# Simple tool dependency checker for Cloud Native Order Processor

# Source logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/logging.sh"

# Essential tools for the project
REQUIRED_TOOLS=("docker" "kubectl" "go" "python3" "node" "npm")

# Check if a tool is installed
check_tool() {
    local tool="$1"

    if command -v "$tool" &> /dev/null; then
        log_success "$tool is available"
        return 0
    else
        log_error "$tool is not installed"
        return 1
    fi
}

# Check all required tools
check_all_tools() {
    log_info "Checking required tools..."

    local missing_tools=()

    for tool in "${REQUIRED_TOOLS[@]}"; do
        if ! check_tool "$tool"; then
            missing_tools+=("$tool")
        fi
    done

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing tools: ${missing_tools[*]}"
        log_info "Please install missing tools before proceeding"
        return 1
    fi

    log_success "All required tools are available"
    return 0
}

# Check Docker
check_docker() {
    log_info "Checking Docker..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        return 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker is not running"
        return 1
    fi

    log_success "Docker is running"
    return 0
}

# Check Kubernetes
check_k8s() {
    log_info "Checking Kubernetes..."

    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        return 1
    fi

    if ! kubectl cluster-info &> /dev/null; then
        log_warning "Cannot connect to Kubernetes cluster"
        log_info "This is normal for local development"
        return 0
    fi

    log_success "Connected to Kubernetes cluster"
    return 0
}

# Main function
main() {
    local command="${1:-all}"

    case "$command" in
        "all")
            check_all_tools
            check_docker
            check_k8s
            ;;
        "tools")
            check_all_tools
            ;;
        "docker")
            check_docker
            ;;
        "k8s")
            check_k8s
            ;;
        *)
            log_error "Unknown command: $command"
            log_info "Usage: $0 {all|tools|docker|k8s}"
            exit 1
            ;;
    esac
}

# Export functions for use in other scripts
export -f check_tool check_all_tools check_docker check_k8s

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
