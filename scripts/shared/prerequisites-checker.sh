#!/bin/bash
# File: scripts/shared/prerequisites-checker.sh
# Check tool dependencies
# Required tool versions: terraform ≥1.5.0, aws ≥2.0.0, kubectl ≥1.28.0, docker ≥24.0.0
# Optional tool checks: python3, pytest, helm
# AWS configuration validation with credential verification
# Version comparison logic for compatibility
# Installation help with links and commands

set -euo pipefail

# Required tools with minimum versions (using regular arrays for Bash 3.x compatibility)
REQUIRED_TOOLS="terraform:1.5.0 aws:2.0.0 kubectl:1.28.0 docker:24.0.0 jq:1.6 git:2.20.0"
OPTIONAL_TOOLS="python3:3.8.0 pytest:7.0.0 helm:3.0.0"

# Check if a tool is installed
check_tool_installed() {
    local tool="${1}"

    if command -v "${tool}" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Get version of a tool
get_tool_version() {
    local tool="${1}"
    local version=""

    case "${tool}" in
        "terraform")
            version=$(terraform --version | head -n1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
            ;;
        "aws")
            version=$(aws --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
            ;;
        "kubectl")
            version=$(kubectl version --client=true -o json 2>/dev/null | jq -r '.clientVersion.gitVersion' | sed 's/^v//')
            ;;
        "docker")
            version=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
            ;;
        "jq")
            version=$(jq --version | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?')
            ;;
        "git")
            version=$(git --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
            ;;
        "python3")
            version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
            ;;
        "pytest")
            if command -v pytest >/dev/null 2>&1; then
                version=$(pytest --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
            elif command -v python3 >/dev/null 2>&1; then
                version=$(python3 -m pytest --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1 || echo "")
            fi
            ;;
        "helm")
            version=$(helm version --short 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
            ;;
        *)
            version="unknown"
            ;;
    esac

    echo "${version}"
}

# Compare version strings (returns 0 if version1 >= version2)
version_compare() {
    local version1="${1}"
    local version2="${2}"

    if [[ "${version1}" == "${version2}" ]]; then
        return 0
    fi

    # Convert versions to arrays
    IFS='.' read -ra ver1 <<< "${version1}"
    IFS='.' read -ra ver2 <<< "${version2}"

    # Pad arrays to same length
    local max_length=${#ver1[@]}
    if [[ ${#ver2[@]} -gt ${max_length} ]]; then
        max_length=${#ver2[@]}
    fi

    # Compare each part
    for (( i=0; i<max_length; i++ )); do
        local part1=${ver1[i]:-0}
        local part2=${ver2[i]:-0}

        if [[ ${part1} -gt ${part2} ]]; then
            return 0
        elif [[ ${part1} -lt ${part2} ]]; then
            return 1
        fi
    done

    return 0
}

# Check individual tool
check_individual_tool() {
    local tool="${1}"
    local required_version="${2}"
    local is_optional="${3:-false}"

    log_debug "Checking ${tool}..."

    if ! check_tool_installed "${tool}"; then
        if [[ "${is_optional}" == "true" ]]; then
            log_warn "Optional tool not found: ${tool}"
            return 2  # Warning for optional tools
        else
            log_error "Required tool not found: ${tool}"
            log_error "Please install ${tool} version ${required_version} or later"
            return 1
        fi
    fi

    local current_version
    current_version=$(get_tool_version "${tool}")

    if [[ -z "${current_version}" || "${current_version}" == "unknown" ]]; then
        log_warn "Could not determine version of ${tool}"
        if [[ "${is_optional}" == "true" ]]; then
            return 2
        else
            return 1
        fi
    fi

    if ! version_compare "${current_version}" "${required_version}"; then
        if [[ "${is_optional}" == "true" ]]; then
            log_warn "Optional tool ${tool} version ${current_version} is older than recommended ${required_version}"
            return 2
        else
            log_error "Tool ${tool} version ${current_version} is older than required ${required_version}"
            return 1
        fi
    fi

    log_debug "✓ ${tool} ${current_version} (>= ${required_version})"
    return 0
}

# Check all required tools
check_required_tools() {
    log_info "Checking required tools..."

    local missing_tools=()
    local outdated_tools=()

    for tool_entry in ${REQUIRED_TOOLS}; do
        local tool="${tool_entry%%:*}"
        local required_version="${tool_entry#*:}"
        local result

        check_individual_tool "${tool}" "${required_version}" "false"
        result=$?

        case ${result} in
            0)
                log_success "${tool} is available and up to date"
                ;;
            1)
                if ! check_tool_installed "${tool}"; then
                    missing_tools+=("${tool} (>= ${required_version})")
                else
                    outdated_tools+=("${tool} (current: $(get_tool_version "${tool}"), required: >= ${required_version})")
                fi
                ;;
        esac
    done

    # Report missing tools
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools:"
        for tool in "${missing_tools[@]}"; do
            log_error "  - ${tool}"
        done
    fi

    # Report outdated tools
    if [[ ${#outdated_tools[@]} -gt 0 ]]; then
        log_error "Outdated required tools:"
        for tool in "${outdated_tools[@]}"; do
            log_error "  - ${tool}"
        done
    fi

    # Return error if any required tools are missing or outdated
    if [[ ${#missing_tools[@]} -gt 0 || ${#outdated_tools[@]} -gt 0 ]]; then
        return 1
    fi

    log_success "All required tools are available and up to date"
    return 0
}

# Check optional tools
check_optional_tools() {
    log_info "Checking optional tools..."

    # Parse the OPTIONAL_TOOLS string
    for tool_entry in ${OPTIONAL_TOOLS}; do
        local tool="${tool_entry%%:*}"
        local required_version="${tool_entry#*:}"

        check_individual_tool "${tool}" "${required_version}" "true"
        case $? in
            0)
                log_success "${tool} is available and up to date"
                ;;
            2)
                # Warning already logged
                ;;
        esac
    done

    log_info "Optional tools check completed"
}

# Check AWS CLI configuration
check_aws_configuration() {
    log_info "Checking AWS CLI configuration..."

    if ! check_tool_installed "aws"; then
        log_error "AWS CLI is required but not installed"
        return 1
    fi

    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        log_error "AWS credentials not configured"
        log_error "Please run 'aws configure' or set up AWS credentials"
        log_error "For CI/CD, ensure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set"
        return 1
    fi

    # Get and display AWS account info
    local caller_identity
    caller_identity=$(aws sts get-caller-identity)
    local account_id
    account_id=$(echo "${caller_identity}" | jq -r '.Account')
    local user_arn
    user_arn=$(echo "${caller_identity}" | jq -r '.Arn')

    log_success "AWS credentials configured"
    log_info "Account ID: ${account_id}"
    log_debug "User/Role ARN: ${user_arn}"

    # Check default region
    local region
    region=$(aws configure get region 2>/dev/null || echo "")

    if [[ -z "${region}" ]]; then
        log_warn "AWS default region not configured"
        log_warn "Using fallback region: ${AWS_DEFAULT_REGION:-us-west-2}"
    else
        log_success "AWS default region: ${region}"
    fi

    return 0
}

# Check Python environment for testing
check_python_environment() {
    log_info "Checking Python environment for testing..."

    if ! check_tool_installed "python3"; then
        log_warn "Python3 not available - some tests may not work"
        return 2
    fi

    local python_version
    python_version=$(get_tool_version "python3")
    log_success "Python ${python_version} is available"

    # Check if pytest is available
    if command -v pytest >/dev/null 2>&1; then
        local pytest_version
        pytest_version=$(get_tool_version "pytest")
        log_success "pytest ${pytest_version} is available"
    elif python3 -m pytest --version >/dev/null 2>&1; then
        local pytest_version
        pytest_version=$(python3 -m pytest --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
        log_success "pytest ${pytest_version} is available via python -m pytest"
    else
        log_warn "pytest not available - infrastructure tests will not work"
        log_warn "Install with: pip install pytest"
        return 2
    fi

    return 0
}

# Check Docker environment
check_docker_environment() {
    log_info "Checking Docker environment..."

    if ! check_tool_installed "docker"; then
        log_warn "Docker not available - container operations will not work"
        return 2
    fi

    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon is not running"
        log_error "Please start Docker daemon"
        return 1
    fi

    local docker_version
    docker_version=$(get_tool_version "docker")
    log_success "Docker ${docker_version} is running"

    return 0
}

# Main prerequisites check function
check_all_prerequisites() {
    local environment="${ENVIRONMENT:-dev}"
    local skip_optional="${1:-false}"

    log_section "Prerequisites Check"

    local overall_status=0

    # Check required tools
    if ! check_required_tools; then
        overall_status=1
    fi

    # Check optional tools unless skipped
    if [[ "${skip_optional}" != "true" ]]; then
        check_optional_tools
    fi

    # Check AWS configuration
    if ! check_aws_configuration; then
        overall_status=1
    fi

    # Check Python environment for testing
    check_python_environment

    # Check Docker environment (not critical for infrastructure tests)
    check_docker_environment

    # Environment-specific checks
    case "${environment}" in
        "ci")
            log_info "Additional CI/CD checks..."
            if [[ -z "${GITHUB_ACTIONS:-}" ]]; then
                log_warn "Not running in GitHub Actions environment"
            fi
            ;;
        "local"|"dev")
            log_info "Additional local development checks..."
            # Check for local development conveniences
            if ! command -v code >/dev/null 2>&1; then
                log_debug "VS Code not available (not required)"
            fi
            ;;
    esac

    # Summary
    if [[ ${overall_status} -eq 0 ]]; then
        log_success "All prerequisites check passed"
        log_info "Environment is ready for infrastructure testing"
    else
        log_failure "Prerequisites check failed"
        log_error "Please install missing tools and try again"

        # Provide installation help
        show_installation_help
    fi

    return ${overall_status}
}

# Show installation help for missing tools
show_installation_help() {
    log_info "=== Installation Help ==="
    log_info "Install missing tools:"
    log_info ""
    log_info "Terraform:"
    log_info "  https://developer.hashicorp.com/terraform/downloads"
    log_info ""
    log_info "AWS CLI:"
    log_info "  https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    log_info ""
    log_info "kubectl:"
    log_info "  https://kubernetes.io/docs/tasks/tools/"
    log_info ""
    log_info "Docker:"
    log_info "  https://docs.docker.com/get-docker/"
    log_info ""
    log_info "jq:"
    log_info "  apt-get install jq  # Ubuntu/Debian"
    log_info "  brew install jq     # macOS"
    log_info ""
    log_info "Python packages:"
    log_info "  pip install pytest boto3 requests"
    log_info "========================="
}

# Export functions for use in other scripts
export -f check_all_prerequisites
export -f check_required_tools
export -f check_aws_configuration
export -f check_python_environment
export -f check_docker_environment
