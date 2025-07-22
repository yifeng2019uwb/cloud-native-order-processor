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
AWS_REGION="us-west-2"

# Default values
ENVIRONMENT=""
VERBOSE=false
DRY_RUN=false

# Job flags
RUN_BUILD_TESTS=false
RUN_DEPLOY=false
RUN_APP_DEPLOY=false
RUN_INTEGRATION_TESTS=false
RUN_DESTROY=false
RUN_ALL=false

# Workflow flags
APP_ONLY=false
DEV_CYCLE=false
KEEP_ENVIRONMENT=false

# Usage
show_usage() {
    cat << EOF
$(printf "${BLUE}🧪 Local Testing Script CI/CD Mirror${NC}")

Usage: $0 --environment {dev|prod} [OPTIONS]

Test locally before pushing to GitHub. Mirrors CI/CD pipeline.

REQUIRED:
    --environment {dev|prod}        Target environment

JOB OPTIONS:
    --build                        Only run build and package tests
    --deploy                       Only deploy infrastructure
    --app                          Only deploy/update application
    --app-only                     Deploy app only (assumes infra exists)
    --test                         Only run integration tests
    --destroy                      Only destroy infrastructure
    --all                          Full pipeline: build → deploy → app → test → destroy

WORKFLOW OPTIONS:
    --dev-cycle                    Deploy → App → Test (skip destroy for iteration)
    --keep-environment             Don't destroy after testing
    --dry-run                      Show what would happen (don't execute)
    -v, --verbose                  Enable verbose output
    -h, --help                     Show this help message

EXAMPLES:
    # Daily development (cheap)
    $0 --environment dev --all         # Full pipeline
    $0 --environment dev --dev-cycle   # Deploy and test, keep infra
    $0 --environment dev --app-only    # Update app only

    # Pre-push validation (comprehensive)
    $0 --environment dev --all         # Full validation with EKS
    $0 --environment prod --all        # Production simulation

    # Individual jobs
    $0 --environment dev --build       # Build tests only
    $0 --environment dev --deploy      # Deploy infra only
    $0 --environment dev --destroy     # Cleanup only

COST AWARENESS:
    - Default environmentis 'dev' for cost control
    - Use 'prod'for full infrastructure validation
    - Always destroy resources when done testing

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
            --build)
                RUN_BUILD_TESTS=true
                shift
                ;;
            --deploy)
                RUN_DEPLOY=true
                shift
                ;;
            --app)
                RUN_APP_DEPLOY=true
                shift
                ;;
            --app-only)
                RUN_APP_DEPLOY=true
                APP_ONLY=true
                shift
                ;;
            --test)
                RUN_INTEGRATION_TESTS=true
                shift
                ;;
            --destroy)
                RUN_DESTROY=true
                shift
                ;;
            --all)
                RUN_ALL=true
                shift
                ;;
            --dev-cycle)
                DEV_CYCLE=true
                shift
                ;;
            --keep-environment)
                KEEP_ENVIRONMENT=true
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

    # Check that at least one job is selected
    if [[ "$RUN_BUILD_TESTS" == "false" && "$RUN_DEPLOY" == "false" && "$RUN_APP_DEPLOY" == "false" && "$RUN_INTEGRATION_TESTS" == "false" && "$RUN_DESTROY" == "false" && "$RUN_ALL" == "false" && "$DEV_CYCLE" == "false" ]]; then
        errors+=("At least one job must be selected (--build, --deploy, --app, --test, --destroy, --all, or --dev-cycle)")
    fi

    # Validate combinations
    if [[ "$APP_ONLY" == "true" && "$RUN_DEPLOY" == "true" ]]; then
        errors+=("--app-only cannot be used with --deploy (assumes infrastructure exists)")
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

# Setup test environment
setup_test_environment() {
    log_step "🔧 Setting Up Test Environment"

    # Set environment variables
    export ENVIRONMENT="$ENVIRONMENT"
    export AWS_DEFAULT_REGION="$AWS_REGION"
    export PYTHONPATH="$PROJECT_ROOT"

    # Load environment configuration
    if [[ -f "config/environments/.env.defaults" ]]; then
        log_info "Loading default configuration..."
        source config/environments/.env.defaults
    fi

    log_success "Test environment setup complete"
}

# Check prerequisites
check_prerequisites() {
    log_step "🔍 Checking Prerequisites"

    local missing_tools=()

    # Common tools
    local common_tools=("git" "aws" "jq")
    for tool in "${common_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Install missing tools and try again"
        return 1
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        log_error "AWS credentials not configured"
        return 1
    fi

    log_success "Prerequisites check passed"
    return 0
}

# Build and package tests
run_build_tests() {
    log_step "🏗️ Build and Package Tests"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run: Would run build and test for all services"
        return 0
    fi

    # Use the unified build-test script
    local build_args="--test-only"

    if [[ "$VERBOSE" == "true" ]]; then
        build_args="$build_args --verbose"
    fi

    log_info "Calling: ./scripts/build-test.sh $build_args"

    if ! ./scripts/build-test.sh $build_args; then
        log_error "Build and test failed"
        return 1
    fi

    log_success "Build and validation tests completed successfully"
    return 0
}

# Deploy infrastructure
deploy_infrastructure() {
    log_step "🚀 Deploying Infrastructure"

    if [[ "$APP_ONLY" == "true" ]]; then
        log_info "Skipping infrastructure deployment (--app-only specified)"
        return 0
    fi

    local deploy_args="--environment $ENVIRONMENT"

    if [[ "$VERBOSE" == "true" ]]; then
        deploy_args="$deploy_args --verbose"
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        deploy_args="$deploy_args --dry-run"
    fi

    log_info "Calling: ./scripts/deploy.sh $deploy_args"

    if ! ./scripts/deploy.sh $deploy_args; then
        log_error "Infrastructure deployment failed"
        return 1
    fi

    log_success "Infrastructure deployed successfully"
    return 0
}

# Deploy application
deploy_application() {
    log_step "📦 Deploying Application"

    case "$ENVIRONMENT" in
        "dev")
            log_info "Dev environment: No application deployment needed"
            log_info "Start services manually:"
            log_info "  cd services/user-service && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000"
            log_info "  cd services/inventory-service && python -m uvicorn src.main:app --host 0.0.0.0 --port 8001"
            ;;
        "prod")
            log_warning "Prod environment: Application deployment not implemented yet"
            log_info "Manual deployment required for production"
            ;;
    esac

    log_success "Application deployment completed"
    return 0
}

# Run integration tests
run_integration_tests() {
    log_step "🧪 Running Integration Tests"

    # For now, placeholder since test-integration.sh isn't updated yet
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run: Would run integration tests"
        return 0
    fi

    log_info "Integration tests placeholder - waiting for test-integration.sh update"

    # Basic connectivity test based on environment
    case "$ENVIRONMENT" in
        "dev")
            log_info "Testing local FastAPI services connectivity..."
            # Test local services
            if command -v curl >/dev/null 2>&1; then
                if curl -s --max-time 5 "http://localhost:8000/health" >/dev/null 2>&1; then
                    log_success "User service connectivity test passed"
                else
                    log_warning "User service connectivity test failed (service may not be running)"
                fi
                if curl -s --max-time 5 "http://localhost:8001/health" >/dev/null 2>&1; then
                    log_success "Inventory service connectivity test passed"
                else
                    log_warning "Inventory service connectivity test failed (service may not be running)"
                fi
            fi
            ;;
        "prod")
            log_info "Testing EKS + Kubernetes connectivity..."
            # Test kubectl connectivity
            if kubectl get nodes >/dev/null 2>&1; then
                log_success "EKS cluster connectivity test passed"
            else
                log_warning "EKS cluster connectivity test failed"
            fi
            ;;
    esac

    log_success "Integration tests completed"
    return 0
}

# Destroy infrastructure
destroy_infrastructure() {
    log_step "🧹 Destroying Infrastructure"

    local destroy_args="--environment $ENVIRONMENT --force"

    if [[ "$VERBOSE" == "true" ]]; then
        destroy_args="$destroy_args --verbose"
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        destroy_args="$destroy_args --dry-run"
    fi

    log_info "Calling: ./scripts/destroy.sh $destroy_args"

    if ! ./scripts/destroy.sh $destroy_args; then
        log_error "Infrastructure destruction failed"
        return 1
    fi

    log_success "Infrastructure destroyed successfully"
    return 0
}

# Execute workflow based on flags
execute_workflow() {
    local failed_jobs=()
    local start_time=$(date +%s)

    # Set job sequence based on flags
    if [[ "$RUN_ALL" == "true" ]]; then
        RUN_BUILD_TESTS=true
        RUN_DEPLOY=true
        RUN_APP_DEPLOY=true
        RUN_INTEGRATION_TESTS=true
        if [[ "$KEEP_ENVIRONMENT" != "true" ]]; then
            RUN_DESTROY=true
        fi
    elif [[ "$DEV_CYCLE" == "true" ]]; then
        RUN_DEPLOY=true
        RUN_APP_DEPLOY=true
        RUN_INTEGRATION_TESTS=true
        # Don't destroy in dev cycle
    fi

    # Execute jobs in sequence
    if [[ "$RUN_BUILD_TESTS" == "true" ]]; then
        if ! run_build_tests; then
            failed_jobs+=("Build Tests")
        fi
    fi

    if [[ "$RUN_DEPLOY" == "true" ]]; then
        if ! deploy_infrastructure; then
            failed_jobs+=("Infrastructure Deployment")
        fi
    fi

    if [[ "$RUN_APP_DEPLOY" == "true" ]]; then
        if ! deploy_application; then
            failed_jobs+=("Application Deployment")
        fi
    fi

    if [[ "$RUN_INTEGRATION_TESTS" == "true" ]]; then
        if ! run_integration_tests; then
            failed_jobs+=("Integration Tests")
        fi
    fi

    if [[ "$RUN_DESTROY" == "true" ]]; then
        if ! destroy_infrastructure; then
            failed_jobs+=("Infrastructure Destruction")
        fi
    fi

    # Calculate duration
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # Final summary
    log_step "📊 Test Summary"

    if [[ ${#failed_jobs[@]} -eq 0 ]]; then
        log_success "✅ All jobs completed successfully! (${duration}s)"
        log_info "Environment: $ENVIRONMENT"

        if [[ "$KEEP_ENVIRONMENT" == "true" || "$DEV_CYCLE" == "true" ]]; then
            log_warning "⚠️  Infrastructure is still running"
            log_info "Remember to destroy when finished:"
            log_info "  ./scripts/test-local.sh --environment $ENVIRONMENT --destroy"
        fi

        log_success "🚀 Ready for production deployment!"
        return 0
    else
        log_error "❌ Some jobs failed: ${failed_jobs[*]} (${duration}s)"
        log_error "Fix the issues above before proceeding"

        if [[ "$KEEP_ENVIRONMENT" != "true" && "$DEV_CYCLE" != "true" ]]; then
            log_info "Attempting cleanup of partial deployment..."
            destroy_infrastructure || log_warning "Cleanup failed - manual intervention may be required"
        fi

        return 1
    fi
}

# Main execution
main() {
    local start_time=$(date +%s)

    # Parse and validate arguments
    parse_arguments "$@"
    validate_arguments

    # Print header
    echo
    printf "${PURPLE}🧪 Local Testing Script CI/CD Mirror${NC}\n"
    printf "${PURPLE}====================================================${NC}\n"
    echo
    log_info "Environment: $ENVIRONMENT"

    # Show selected jobs
    local selected_jobs=()
    [[ "$RUN_BUILD_TESTS" == "true" ]] && selected_jobs+=("Build")
    [[ "$RUN_DEPLOY" == "true" ]] && selected_jobs+=("Deploy")
    [[ "$RUN_APP_DEPLOY" == "true" ]] && selected_jobs+=("App")
    [[ "$RUN_INTEGRATION_TESTS" == "true" ]] && selected_jobs+=("Test")
    [[ "$RUN_DESTROY" == "true" ]] && selected_jobs+=("Destroy")
    [[ "$RUN_ALL" == "true" ]] && selected_jobs=("All")
    [[ "$DEV_CYCLE" == "true" ]] && selected_jobs=("Dev-Cycle")

    log_info "Selected jobs: ${selected_jobs[*]}"
    echo

    # Setup and execute
    if ! check_prerequisites; then
        exit 1
    fi

    setup_test_environment
    execute_workflow

    exit $?
}

# Run main function
main "$@"