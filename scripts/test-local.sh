#!/bin/bash
# scripts/test-local.sh
# Local Testing Script - Mirror CI/CD Pipeline
# Run this before pushing to GitHub to catch issues early

set -e

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.11"
TERRAFORM_VERSION="1.5.0"
AWS_REGION="us-west-2"
ENVIRONMENT="local"

# Default test options
RUN_BUILD_TESTS=true
RUN_LINT_TESTS=true
RUN_UNIT_TESTS=true
RUN_INFRA_TESTS=true
RUN_DOCKER_TESTS=true
RUN_SECURITY_SCAN=true
RUN_TERRAFORM_VALIDATION=true

# Flags
VERBOSE=false
FAST_MODE=false
SKIP_CLEANUP=false
DOCKER_BUILD=false
CI_SIMULATION=false

# Add environment variable initialization
ENVIRONMENT=${ENVIRONMENT:-learning}
DEPLOY_TEST=false
INTEGRATION_ONLY=false
KEEP_ENVIRONMENT=false
DESTROY_ONLY=false

# Usage
show_usage() {
    cat << EOF
$(printf "${BLUE}🧪 Local Testing Script - Mirror CI/CD Pipeline${NC}")

Usage: $0 [OPTIONS]

Test locally before pushing to GitHub to catch issues early and save CI/CD costs.

OPTIONS:
    -h, --help              Show this help message
    -v, --verbose           Enable verbose output
    -f, --fast              Fast mode (skip slow tests)
    -d, --docker            Include Docker build tests
    -c, --ci-simulation     Full CI simulation mode
    --skip-cleanup          Don't cleanup test artifacts
    --build-only            Only run build tests
    --lint-only             Only run linting
    --infra-only            Only run infrastructure tests
    --security-only         Only run security tests
    --deploy-test           Full deploy → test → destroy cycle
    --integration-only      Only run integration tests (assumes deployed)
    --keep-environment      Deploy and test, but don't destroy
    --destroy-only          Only destroy existing environment
    --deploy-test           Full deploy → test → destroy cycle
    --integration-only      Only run integration tests (assumes deployed)
    --keep-environment      Deploy and test, but don't destroy
    --destroy-only          Only destroy existing environment

TEST CATEGORIES:
    🏗️  Build & Package     - Service building and packaging
    🎨 Linting & Format     - Code quality and formatting
    🧪 Unit Tests          - Service unit tests
    🏗️  Infrastructure     - Terraform validation and tests
    🐳 Docker Build        - Container building and testing
    🔒 Security Scan       - Code and dependency scanning
    🚀 Deploy & Test       - AWS deployment and integration testing
    🧹 Environment Cleanup - Destroy AWS resources

EXAMPLES:
    $0                      # Run all tests (recommended before push)
    $0 --fast              # Quick validation (skip slow tests)
    $0 --docker            # Include Docker build testing
    $0 --ci-simulation     # Full CI/CD simulation
    $0 --build-only        # Only test service builds
    $0 --infra-only        # Only test infrastructure
    $0 --deploy-test          # Full deploy → test → destroy
    $0 --integration-only    # Only integration tests
    $0 --deploy-test --keep-environment  # Deploy and test, keep AWS resources
    $0 --destroy-only        # Only destroy AWS environment

ENVIRONMENT:
    Set these environment variables to customize behavior:
    - AWS_PROFILE          # AWS profile for infrastructure tests
    - DOCKER_REGISTRY      # Docker registry for testing
    - TEST_TIMEOUT         # Test timeout in seconds

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
    printf "\n${PURPLE}=== %s ===${NC}\n" "$1"
}

log_substep() {
    printf "${CYAN}--- %s ---${NC}\n" "$1"
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -f|--fast)
                FAST_MODE=true
                RUN_SECURITY_SCAN=false
                shift
                ;;
            -d|--docker)
                DOCKER_BUILD=true
                shift
                ;;
            -c|--ci-simulation)
                CI_SIMULATION=true
                DOCKER_BUILD=true
                RUN_SECURITY_SCAN=true
                shift
                ;;
            --skip-cleanup)
                SKIP_CLEANUP=true
                shift
                ;;
            --build-only)
                RUN_BUILD_TESTS=true
                RUN_LINT_TESTS=true
                RUN_UNIT_TESTS=true
                RUN_INFRA_TESTS=false
                RUN_DOCKER_TESTS=false
                RUN_SECURITY_SCAN=false
                RUN_TERRAFORM_VALIDATION=false
                shift
                ;;
            --infra-only)
                RUN_BUILD_TESTS=false
                RUN_LINT_TESTS=false
                RUN_UNIT_TESTS=false
                RUN_INFRA_TESTS=true
                RUN_DOCKER_TESTS=false
                RUN_SECURITY_SCAN=false
                RUN_TERRAFORM_VALIDATION=true
                shift
                ;;
            --security-only)
                RUN_BUILD_TESTS=false
                RUN_LINT_TESTS=false
                RUN_UNIT_TESTS=false
                RUN_INFRA_TESTS=false
                RUN_DOCKER_TESTS=false
                RUN_SECURITY_SCAN=true
                RUN_TERRAFORM_VALIDATION=false
                shift
                ;;
            --deploy-test)
                DEPLOY_TEST=true
                shift
                ;;
            --integration-only)
                INTEGRATION_ONLY=true
                shift
                ;;
            --keep-environment)
                KEEP_ENVIRONMENT=true
                shift
                ;;
            --destroy-only)
                DESTROY_ONLY=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Check prerequisites
check_prerequisites() {
    log_step "🔍 Checking Prerequisites"

    local missing_tools=()

    # Check Python
    if ! command -v python3 >/dev/null 2>&1; then
        missing_tools+=("python3")
    else
        local python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
        if [[ "$python_version" != "3.11" ]]; then
            log_warning "Python version is $python_version, expected 3.11"
        fi
    fi

    # Check required tools
    local tools=("git" "terraform" "docker" "jq")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Install missing tools:"
        log_info "  - Python 3.11: https://www.python.org/downloads/"
        log_info "  - Terraform: https://developer.hashicorp.com/terraform/downloads"
        log_info "  - Docker: https://docs.docker.com/get-docker/"
        log_info "  - jq: apt install jq / brew install jq"
        return 1
    fi

    # Check Python packages
    local python_packages=("pip" "venv")
    for package in "${python_packages[@]}"; do
        if ! python3 -m "$package" --help >/dev/null 2>&1; then
            log_warning "Python module '$package' not available"
        fi
    done

    log_success "Prerequisites check passed"
    return 0
}

# Setup test environment
setup_test_environment() {
    log_step "🔧 Setting Up Test Environment"

    # Create test workspace
    export TEST_WORKSPACE="${PROJECT_ROOT}/.test-workspace"
    mkdir -p "$TEST_WORKSPACE"

    # Load environment configuration
    if [[ -f "config/environments/.env.defaults" ]]; then
        log_info "Loading default configuration..."
        source config/environments/.env.defaults
    fi

    if [[ -f "config/environments/.env.local" ]]; then
        log_info "Loading local configuration..."
        source config/environments/.env.local
    fi

    # Set environment variables
    export ENVIRONMENT="local"
    export AWS_DEFAULT_REGION="$AWS_REGION"
    export PYTHONPATH="$PROJECT_ROOT"

    # Setup Python virtual environment for testing
    if [[ ! -d "$TEST_WORKSPACE/venv" ]]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv "$TEST_WORKSPACE/venv"
    fi

    source "$TEST_WORKSPACE/venv/bin/activate"
    pip install --quiet --upgrade pip setuptools wheel

    log_success "Test environment setup complete"
}

# Mirror CI/CD: Build and Test Services
test_build_services() {
    if [[ "$RUN_BUILD_TESTS" != "true" ]]; then
        return 0
    fi

    log_step "🏗️ Building Services (Mirror CI/CD Build Stage)"

    cd "$PROJECT_ROOT/services"

    # Make build script executable
    chmod +x build.sh

    # Test common package first
    log_substep "Building common package"
    if ! ./build.sh --build-only --verbose common; then
        log_error "Common package build failed"
        return 1
    fi

    # Build each service
    for service_dir in */; do
        service_name=$(basename "$service_dir")

        # Skip common package (already built)
        if [[ "$service_name" == "common" ]]; then
            continue
        fi

        # Skip if no build script or requirements
        if [[ ! -f "$service_dir/requirements.txt" ]]; then
            log_warning "Skipping $service_name (no requirements.txt)"
            continue
        fi

        log_substep "Building $service_name"
        if ! ./build.sh --build-only --verbose "$service_name"; then
            log_error "$service_name build failed"
            return 1
        fi
    done

    log_success "Service builds completed successfully"
    cd "$PROJECT_ROOT"
}

# Mirror CI/CD: Linting and Code Quality
test_linting() {
    if [[ "$RUN_LINT_TESTS" != "true" ]]; then
        return 0
    fi

    log_step "🎨 Code Quality & Linting (Mirror CI/CD Lint Stage)"

    cd "$PROJECT_ROOT/services"

    # Install linting tools
    pip install --quiet flake8 black isort mypy bandit

    # Run linting through build script
    log_substep "Running linting via build script"
    if ! ./build.sh --test-only common; then
        log_error "Linting failed"
        return 1
    fi

    # Additional security linting
    log_substep "Running security linting (bandit)"
    if command -v bandit >/dev/null 2>&1; then
        for service_dir in */; do
            if [[ -d "$service_dir/src" ]]; then
                bandit -r "$service_dir/src" -f json -o "$TEST_WORKSPACE/bandit-${service_dir%/}.json" 2>/dev/null || true
            fi
        done
    fi

    log_success "Code quality checks passed"
    cd "$PROJECT_ROOT"
}

# Mirror CI/CD: Unit Tests
test_unit_tests() {
    if [[ "$RUN_UNIT_TESTS" != "true" ]]; then
        return 0
    fi

    log_step "🧪 Unit Tests (Mirror CI/CD Test Stage)"

    cd "$PROJECT_ROOT/services"

    # Install test dependencies
  pip install --quiet pytest pytest-cov pytest-mock httpx


    # Run unit tests for each service
    for service_dir in */; do
        service_name=$(basename "$service_dir")

        if [[ "$service_name" == "common" ]]; then
            continue
        fi

        if [[ ! -d "$service_dir/tests" ]]; then
            log_warning "No tests found for $service_name"
            continue
        fi

        log_substep "Running unit tests for $service_name"
        cd "$service_dir"

        # Install service requirements first
        pip install --quiet -r requirements.txt

        # Set PYTHONPATH to include the service src directory and project root
        export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/services/$service_name/src:$PYTHONPATH"

        # Run tests with coverage
        if ! python -m pytest tests/ -v --tb=short --cov=src --cov-report=term-missing; then
            log_error "Unit tests failed for $service_name"
            cd "$PROJECT_ROOT/services"
            return 1
        fi
        if ! python -m pytest tests/ -v --tb=short; then
            log_error "Unit tests failed for $service_name"
            cd "$PROJECT_ROOT/services"
            return 1
        fi

        cd "$PROJECT_ROOT/services"
    done

    log_success "Unit tests completed successfully"
    cd "$PROJECT_ROOT"
}

# Mirror CI/CD: Infrastructure Tests
test_infrastructure() {
    if [[ "$RUN_INFRA_TESTS" != "true" ]]; then
        return 0
    fi

    log_step "🏗️ Infrastructure Tests (Mirror CI/CD Infrastructure Stage)"

    cd "$PROJECT_ROOT/terraform"

    # Install test dependencies
    pip install --quiet boto3 requests pytest pytest-html pytest-timeout

    # Terraform validation
    if [[ "$RUN_TERRAFORM_VALIDATION" == "true" ]]; then
        log_substep "Terraform validation"
        terraform init -backend=false
        terraform validate
        terraform fmt -check -recursive
    fi

    # Run infrastructure tests
    log_substep "Running infrastructure tests"
    if [[ -f "scripts/test-infrastructure.sh" ]]; then
        chmod +x scripts/test-infrastructure.sh
        export TEST_TIMEOUT=300
        export TEST_VERBOSE=$VERBOSE
        export DRY_RUN=true

        if ! ./scripts/test-infrastructure.sh --test-type terraform --dry-run; then
            log_error "Infrastructure tests failed"
            return 1
        fi
    else
        log_warning "Infrastructure test script not found"
        # Fallback to basic pytest
        if [[ -d "infrastructure-tests" ]]; then
            cd infrastructure-tests
            python -m pytest -v -m "terraform" --tb=short || true
            cd ..
        fi
    fi

    log_success "Infrastructure tests completed"
    cd "$PROJECT_ROOT"
}

# Mirror CI/CD: Docker Build Tests
test_docker_build() {
    if [[ "$RUN_DOCKER_TESTS" != "true" || "$DOCKER_BUILD" != "true" ]]; then
        return 0
    fi

    log_step "🐳 Docker Build Tests (Mirror CI/CD Docker Stage)"

    # Test Docker builds for each service
    for docker_dir in docker/*/; do
        if [[ ! -d "$docker_dir" ]]; then
            continue
        fi

        service_name=$(basename "$docker_dir")

        # Skip non-service directories
        if [[ "$service_name" == "frontend" ]]; then
            continue
        fi

        log_substep "Building Docker image for $service_name"
        cd "$docker_dir"

        # Choose Dockerfile
        DOCKERFILE="Dockerfile.simple"
        if [[ ! -f "$DOCKERFILE" ]]; then
            DOCKERFILE="Dockerfile"
        fi

        if [[ ! -f "$DOCKERFILE" ]]; then
            log_warning "No Dockerfile found for $service_name"
            cd "$PROJECT_ROOT"
            continue
        fi

        # Build image
        local image_tag="local-test-${service_name}:latest"
        if ! docker build -t "$image_tag" -f "$DOCKERFILE" ../..; then
            log_error "Docker build failed for $service_name"
            cd "$PROJECT_ROOT"
            return 1
        fi

        # Test image
        log_substep "Testing Docker image for $service_name"
        if ! docker run --rm "$image_tag" python --version; then
            log_error "Docker image test failed for $service_name"
            cd "$PROJECT_ROOT"
            return 1
        fi

        # Cleanup test image
        docker rmi "$image_tag" >/dev/null 2>&1 || true

        cd "$PROJECT_ROOT"
    done

    log_success "Docker build tests completed"
}

# Mirror CI/CD: Security Scanning
test_security_scan() {
    if [[ "$RUN_SECURITY_SCAN" != "true" ]]; then
        return 0
    fi

    log_step "🔒 Security Scanning (Mirror CI/CD Security Stage)"

    # Check if Trivy is installed
    if ! command -v trivy >/dev/null 2>&1; then
        log_warning "Trivy not installed, skipping container security scan"
        log_info "Install Trivy: https://aquasecurity.github.io/trivy/latest/getting-started/installation/"
    else
        log_substep "Running Trivy security scan"

        # Scan filesystem for vulnerabilities
        trivy fs --security-checks vuln,secret,config . \
            --format table \
            --severity HIGH,CRITICAL \
            --exit-code 0 || true
    fi

    # Python dependency security check
    if command -v safety >/dev/null 2>&1; then
        log_substep "Running Python dependency security check"
        safety check || log_warning "Safety check found issues"
    else
        log_info "Install 'safety' for Python dependency security scanning: pip install safety"
    fi

    # Git secrets check
    if command -v git-secrets >/dev/null 2>&1; then
        log_substep "Running git secrets scan"
        git secrets --scan || log_warning "Git secrets scan found issues"
    fi

    log_success "Security scanning completed"
}

# Function: Deploy Infrastructure
deploy_infrastructure() {
    echo "=== 🚀 Deploying Infrastructure to AWS ==="
    echo "--- Deploying to environment: ${ENVIRONMENT:-learning} ---"

    if ! ./scripts/deploy.sh --environment "${ENVIRONMENT:-learning}"; then
        echo "[ERROR] Infrastructure deployment failed"
        return 1
    fi

    echo "[SUCCESS] Infrastructure deployed successfully"
}

# Function: Deploy Application
deploy_application() {
    echo "=== 📦 Deploying Application to AWS ==="
    echo "--- Deploying order-service to environment: ${ENVIRONMENT:-learning} ---"

    if ! ./scripts/deploy-app.sh --environment "${ENVIRONMENT:-learning}"; then
        echo "[ERROR] Application deployment failed"
        return 1
    fi

    echo "[SUCCESS] Application deployed successfully"
}

# Function: Run Integration Tests
run_integration_tests() {
    echo "=== 🧪 Running Integration Tests ==="
    echo "--- Testing against AWS environment: ${ENVIRONMENT:-learning} ---"

    # Wait for services to be ready
    echo "Waiting for services to initialize..."
    sleep 30

    if ! ./scripts/test-integration.sh --environment "${ENVIRONMENT:-learning}"; then
        echo "[ERROR] Integration tests failed"
        return 1
    fi

    echo "[SUCCESS] Integration tests passed"
}

# Function: Destroy Environment
destroy_environment() {
    echo "=== 🧹 Destroying AWS Environment ==="
    echo "--- Destroying environment: ${ENVIRONMENT:-learning} ---"

    if ! ./scripts/destroy.sh --environment "${ENVIRONMENT:-learning}" --auto-approve; then
        echo "[ERROR] Environment destruction failed"
        return 1
    fi

    echo "[SUCCESS] Environment destroyed successfully"
}

# Function: Full Deploy-Test-Destroy Cycle
run_deploy_test_cycle() {
    echo "=== 🚀 Full Deploy → Test → Destroy Cycle ==="

    # Deploy infrastructure
    if ! deploy_infrastructure; then
        echo "[ERROR] Deploy-test cycle failed at infrastructure deployment"
        return 1
    fi

    # Deploy application
    if ! deploy_application; then
        echo "[ERROR] Deploy-test cycle failed at application deployment"
        destroy_environment  # Cleanup on failure
        return 1
    fi

    # Run integration tests
    if ! run_integration_tests; then
        echo "[ERROR] Deploy-test cycle failed at integration testing"
        if [[ "$KEEP_ENVIRONMENT" != "true" ]]; then
            destroy_environment  # Cleanup on failure
        fi
        return 1
    fi

    # Destroy environment (unless keeping it)
    if [[ "$KEEP_ENVIRONMENT" != "true" ]]; then
        if ! destroy_environment; then
            echo "[WARNING] Deploy-test cycle completed but cleanup failed"
            echo "[WARNING] Manual cleanup may be required"
            return 1
        fi
    else
        echo "[INFO] Environment kept as requested (--keep-environment)"
        echo "[INFO] Remember to run --destroy-only when finished"
    fi

    echo "[SUCCESS] Deploy-test cycle completed successfully"
}


# Generate test report
generate_test_report() {
    log_step "📊 Generating Test Report"

    local report_file="$TEST_WORKSPACE/local-test-report.md"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    cat > "$report_file" << EOF
# Local Test Report

**Generated:** $timestamp
**Environment:** $ENVIRONMENT
**Mode:** $([ "$FAST_MODE" = "true" ] && echo "Fast" || echo "Full")
**CI Simulation:** $([ "$CI_SIMULATION" = "true" ] && echo "Yes" || echo "No")

## Test Results

$([ "$RUN_BUILD_TESTS" = "true" ] && echo "- ✅ Build Tests: Passed" || echo "- ⏭️ Build Tests: Skipped")
$([ "$RUN_LINT_TESTS" = "true" ] && echo "- ✅ Linting: Passed" || echo "- ⏭️ Linting: Skipped")
$([ "$RUN_UNIT_TESTS" = "true" ] && echo "- ✅ Unit Tests: Passed" || echo "- ⏭️ Unit Tests: Skipped")
$([ "$RUN_INFRA_TESTS" = "true" ] && echo "- ✅ Infrastructure Tests: Passed" || echo "- ⏭️ Infrastructure Tests: Skipped")
$([ "$RUN_DOCKER_TESTS" = "true" ] && echo "- ✅ Docker Tests: Passed" || echo "- ⏭️ Docker Tests: Skipped")
$([ "$RUN_SECURITY_SCAN" = "true" ] && echo "- ✅ Security Scan: Passed" || echo "- ⏭️ Security Scan: Skipped")

## Recommendations

- All tests passed! ✅ Ready to push to GitHub
- Your code should pass CI/CD pipeline
- Infrastructure validation completed
$([ "$DOCKER_BUILD" = "true" ] && echo "- Docker builds validated")

## Files Generated

- Test workspace: \`$TEST_WORKSPACE\`
- Report location: \`$report_file\`
$([ -f "$TEST_WORKSPACE/bandit-order-service.json" ] && echo "- Security scan: \`$TEST_WORKSPACE/bandit-order-service.json\`")

## Next Steps

1. Review any warnings above
2. Commit your changes: \`git add . && git commit -m "feat: your changes"\`
3. Push to GitHub: \`git push origin develop\`
4. Monitor CI/CD pipeline results

---
Generated by local-test script
EOF

    log_success "Test report generated: $report_file"

    if [[ "$VERBOSE" == "true" ]]; then
        echo
        cat "$report_file"
    fi
}

# Cleanup function
cleanup_test_environment() {
    if [[ "$SKIP_CLEANUP" == "true" ]]; then
        log_info "Skipping cleanup (--skip-cleanup specified)"
        return 0
    fi

    log_step "🧹 Cleaning Up"

    # Cleanup Docker images
    docker image prune -f >/dev/null 2>&1 || true

    # Remove old test workspaces
    find "$PROJECT_ROOT" -name ".test-workspace" -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true

    log_success "Cleanup completed"
}

# Main execution
main() {
    local start_time=$(date +%s)

    # Parse arguments
    parse_arguments "$@"

    # Print header
    echo
    printf "${PURPLE}🧪 Local Testing Script - Mirror CI/CD Pipeline${NC}\n"
    printf "${PURPLE}================================================${NC}\n"
    echo

    if [[ "$CI_SIMULATION" == "true" ]]; then
        log_info "🎭 Running in CI Simulation Mode"
    elif [[ "$FAST_MODE" == "true" ]]; then
        log_info "⚡ Running in Fast Mode"
    else
        log_info "🔄 Running Full Test Suite"
    fi

    # Run test stages
    if ! check_prerequisites; then
        exit 1
    fi

    setup_test_environment

    # Execute test stages (mirror CI/CD pipeline)
    local failed_stages=()

    if ! test_build_services; then
        failed_stages+=("Build")
    fi

    if ! test_linting; then
        failed_stages+=("Linting")
    fi

    if ! test_unit_tests; then
        failed_stages+=("Unit Tests")
    fi

    if ! test_infrastructure; then
        failed_stages+=("Infrastructure")
    fi

    if ! test_docker_build; then
        failed_stages+=("Docker")
    fi

    if ! test_security_scan; then
        failed_stages+=("Security")
    fi

    # Handle deploy-test cycle
    if [[ "$DEPLOY_TEST" == "true" ]]; then
        run_deploy_test_cycle
        exit $?
    fi

    # Handle integration-only
    if [[ "$INTEGRATION_ONLY" == "true" ]]; then
        run_integration_tests
        exit $?
    fi

    # Handle destroy-only
    if [[ "$DESTROY_ONLY" == "true" ]]; then
        destroy_environment
        exit $?
    fi

    # Generate report
    generate_test_report

    # Cleanup
    cleanup_test_environment

    # Calculate duration
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # Final summary
    echo
    printf "${PURPLE}=== Final Summary ===${NC}\n"

    if [[ ${#failed_stages[@]} -eq 0 ]]; then
        printf "${GREEN}✅ All tests passed! (${duration}s)${NC}\n"
        printf "${GREEN}🚀 Ready to push to GitHub${NC}\n"
        echo
        log_info "Your code should pass the CI/CD pipeline"
        log_info "Next steps:"
        log_info "  1. git add ."
        log_info "  2. git commit -m 'your message'"
        log_info "  3. git push origin develop"
        exit 0
    else
        printf "${RED}❌ Some tests failed: ${failed_stages[*]} (${duration}s)${NC}\n"
        printf "${RED}🛑 Fix issues before pushing to GitHub${NC}\n"
        echo
        log_error "Review the output above and fix issues"
        log_info "Test report: $TEST_WORKSPACE/local-test-report.md"
        exit 1
    fi
}

# Trap for cleanup on exit
trap cleanup_test_environment EXIT

# Run main function
main "$@"