#!/bin/bash
# scripts/deploy-monitoring.sh
# Monitoring Deployment Script - Deploy Loki + Grafana monitoring stack
# Integrates with existing infrastructure deployment

set -e

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="dev"
DEPLOY_TYPE="docker"  # docker, k8s, or both
VERBOSE=false
DRY_RUN=false

# Usage function
show_usage() {
    cat << EOF
$(printf "${BLUE}📊 Monitoring Deployment Script${NC}")

Usage: $0 [OPTIONS]

Deploy Loki + Grafana monitoring stack for log aggregation.

OPTIONS:
    --environment {dev|prod}           Target environment (default: dev)
    --type {docker|k8s|both}          Deployment type (default: docker)
    -v, --verbose                      Enable verbose output
    --dry-run                          Show what would happen (k8s only)
    -h, --help                         Show this help message

EXAMPLES:
    # Deploy monitoring with Docker Compose (local development)
    $0 --type docker --environment dev

    # Deploy monitoring to Kubernetes
    $0 --type k8s --environment dev

    # Deploy to both environments
    $0 --type both --environment dev

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

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --type)
                DEPLOY_TYPE="$2"
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

    # Validate environment
    case $ENVIRONMENT in
        dev|prod)
            ;;
        *)
            errors+=("Environment must be 'dev' or 'prod'")
            ;;
    esac

    # Validate deployment type
    case $DEPLOY_TYPE in
        docker|k8s|both)
            ;;
        *)
            errors+=("Deployment type must be 'docker', 'k8s', or 'both'")
            ;;
    esac

    # Show errors if any
    if [[ ${#errors[@]} -gt 0 ]]; then
        for error in "${errors[@]}"; do
            log_error "$error"
        done
        show_usage
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites"

    case $DEPLOY_TYPE in
        docker|both)
            if ! command -v docker &> /dev/null; then
                log_error "Docker is not installed"
                exit 1
            fi
            if ! command -v docker-compose &> /dev/null; then
                log_error "Docker Compose is not installed"
                exit 1
            fi
            log_success "Docker prerequisites met"
            ;;
    esac

    case $DEPLOY_TYPE in
        k8s|both)
            if ! command -v kubectl &> /dev/null; then
                log_error "kubectl is not installed"
                exit 1
            fi
            if ! kubectl cluster-info &> /dev/null; then
                log_error "No Kubernetes cluster is accessible"
                exit 1
            fi
            log_success "Kubernetes prerequisites met"
            ;;
    esac
}

# Deploy monitoring with Docker Compose
deploy_docker_monitoring() {
    log_step "Deploying monitoring with Docker Compose"

    local monitoring_dir="$PROJECT_ROOT/monitoring"
    if [[ ! -d "$monitoring_dir" ]]; then
        log_error "Monitoring directory not found: $monitoring_dir"
        exit 1
    fi

    cd "$monitoring_dir"

    # Check if configuration files exist
    local required_files=(
        "docker-compose.logs.yml"
        "loki/local-config.yaml"
        "promtail/config.yml"
        "grafana/provisioning/datasources/loki.yml"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Required configuration file not found: $file"
            exit 1
        fi
    done

    log_info "Starting monitoring stack..."
    docker-compose -f docker-compose.logs.yml up -d

    log_success "Docker monitoring stack deployed"
    log_info "Access Grafana at: http://localhost:3000 (admin/admin123)"
    log_info "Loki endpoint: http://localhost:3100"
}

# Deploy monitoring to Kubernetes
deploy_k8s_monitoring() {
    log_step "Deploying monitoring to Kubernetes"

    local k8s_dir="$PROJECT_ROOT/kubernetes"
    if [[ ! -d "$k8s_dir" ]]; then
        log_error "Kubernetes directory not found: $k8s_dir"
        exit 1
    fi

    cd "$k8s_dir"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry run - showing what would be deployed..."
        kubectl apply -k base/ --dry-run=client
    else
        log_info "Deploying monitoring infrastructure..."
        kubectl apply -k base/

        log_info "Waiting for monitoring pods to be ready..."
        kubectl wait --for=condition=ready pod -l component=monitoring -n order-processor --timeout=300s

        log_success "Kubernetes monitoring stack deployed"
        log_info "Access Grafana at: http://localhost:30001 (admin/admin123)"
        log_info "Loki endpoint: http://localhost:3100 (port-forward required)"
    fi
}

# Show monitoring status
show_status() {
    log_step "Monitoring Status"

    case $DEPLOY_TYPE in
        docker|both)
            local monitoring_dir="$PROJECT_ROOT/monitoring"
            if [[ -d "$monitoring_dir" ]]; then
                cd "$monitoring_dir"
                log_info "Docker Compose Status:"
                docker-compose -f docker-compose.logs.yml ps
                echo
            fi
            ;;
    esac

    case $DEPLOY_TYPE in
        k8s|both)
            log_info "Kubernetes Status:"
            kubectl get pods -l component=monitoring -n order-processor 2>/dev/null || echo "No monitoring pods found"
            echo
            log_info "Services:"
            kubectl get svc -l component=monitoring -n order-processor 2>/dev/null || echo "No monitoring services found"
            ;;
    esac

    echo
    log_info "Monitoring URLs:"
    echo "  📊 Grafana: http://localhost:3000 (Docker) or http://localhost:30001 (K8s)"
    echo "  📝 Loki: http://localhost:3100"
    echo "  🔍 Promtail: http://localhost:9080"
}

# Setup log directory for services
setup_log_directory() {
    log_step "Setting up log directory for services"

    local log_dir="$PROJECT_ROOT/services/logs"
    mkdir -p "$log_dir"

    # Create service-specific log directories
    local services=("user_service" "inventory_service" "order_service" "gateway")
    for service in "${services[@]}"; do
        mkdir -p "$log_dir/$service"
        log_info "Created log directory: $log_dir/$service"
    done

    log_success "Log directories created"
    log_info "Services will write logs to: $log_dir"
}

# Main deployment function
main() {
    log_info "Starting monitoring deployment..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Deployment type: $DEPLOY_TYPE"

    # Parse and validate arguments first
    parse_arguments "$@"
    validate_arguments

    # Check prerequisites
    check_prerequisites

    # Setup log directory
    setup_log_directory

    # Execute deployments
    case $DEPLOY_TYPE in
        docker)
            deploy_docker_monitoring
            ;;
        k8s)
            deploy_k8s_monitoring
            ;;
        both)
            deploy_docker_monitoring
            deploy_k8s_monitoring
            ;;
    esac

    # Show status
    show_status

    log_success "Monitoring deployment completed successfully!"
}

# Script execution
main "$@"
