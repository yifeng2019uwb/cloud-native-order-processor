#!/bin/bash
# scripts/deploy-docker.sh
# Docker Deployment Script - Simple wrapper around docker-compose
# Usage: ./scripts/deploy-docker.sh [-b|-d|-bd] [SERVICE_NAME|all]

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
BUILD_ONLY=false
DEPLOY_ONLY=false
BUILD_DEPLOY=false
SERVICE_NAME=""
COMPOSE_FILE="docker/docker-compose.dev.yml"

# Available services (development environment)
AVAILABLE_SERVICES=("frontend-dev" "user_service" "inventory_service" "order_service" "gateway" "all")

# Usage function
show_usage() {
    cat << EOF
$(printf "${BLUE}🐳 Docker Deployment Script${NC}")

Usage: $0 [-b|-d|-bd] [SERVICE_NAME|all]

REQUIRED PARAMETERS:
    -b, --build-only        Build only (no deploy)
    -d, --deploy-only       Deploy only (no build)
    -bd, --build-deploy     Build + Deploy

    SERVICE_NAME            Service to operate on
        frontend-dev        Frontend service
        user_service        User service
        inventory_service   Inventory service
        order_service       Order service
        gateway             Gateway service
        all                 All services

EXAMPLES:
    $0 -bd frontend-dev     # Build + Deploy frontend
    $0 -bd all              # Build + Deploy all services
    $0 -b frontend-dev      # Build only frontend
    $0 -d user_service      # Deploy only user service

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
    action_count=0

    while [[ $# -gt 0 ]]; do
        case $1 in
            -b|--build-only)
                BUILD_ONLY=true
                action_count=$((action_count + 1))
                shift
                ;;
            -d|--deploy-only)
                DEPLOY_ONLY=true
                action_count=$((action_count + 1))
                shift
                ;;
            -bd|--build-deploy)
                BUILD_DEPLOY=true
                action_count=$((action_count + 1))
                shift
                ;;

            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                # First non-flag argument is service name
                if [[ -z "$SERVICE_NAME" ]]; then
                    SERVICE_NAME="$1"
                else
                    log_error "Unknown option: $1"
                    show_usage
                    exit 1
                fi
                shift
                ;;
        esac
    done

        # Export variables for validation
    export BUILD_ONLY
    export BUILD_DEPLOY
    export DEPLOY_ONLY
    export SERVICE_NAME
    export action_count
}

# Validate arguments
validate_arguments() {
    local errors=()

    # Check if exactly one action is specified
    if [[ $action_count -ne 1 ]]; then
        errors+=("Exactly one action must be specified: -b, -d, or -bd")
    fi

    # Check if service name is provided
    if [[ -z "$SERVICE_NAME" ]]; then
        errors+=("Service name is required")
    fi

        # Validate service name
    local valid_service=false
    for service in "${AVAILABLE_SERVICES[@]}"; do
        if [[ "$service" == "$SERVICE_NAME" ]]; then
            valid_service=true
            break
        fi
    done
    if [[ "$valid_service" == "false" ]]; then
        errors+=("Invalid service name: $SERVICE_NAME")
        errors+=("Available services: ${AVAILABLE_SERVICES[*]}")
    fi



    # Check if compose file exists
    if [[ ! -f "$PROJECT_ROOT/$COMPOSE_FILE" ]]; then
        errors+=("Docker Compose file not found: $COMPOSE_FILE")
    fi

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
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker is not running or not accessible"
        exit 1
    fi

    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
}

# Build services
build_services() {
    log_step "Building Docker images"

    local compose_file="$PROJECT_ROOT/$COMPOSE_FILE"
    cd "$(dirname "$compose_file")"

    if [[ "$SERVICE_NAME" == "all" ]]; then
        log_info "Building all services..."
        docker-compose -f "$(basename "$compose_file")" build
    else
        log_info "Building service: $SERVICE_NAME"
        docker-compose -f "$(basename "$compose_file")" build "$SERVICE_NAME"
    fi

    log_success "Build completed"
}

# Deploy services
deploy_services() {
    log_step "Deploying services"

    local compose_file="$PROJECT_ROOT/$COMPOSE_FILE"
    cd "$(dirname "$compose_file")"

    if [[ "$SERVICE_NAME" == "all" ]]; then
        log_info "Deploying all services..."
        docker-compose -f "$(basename "$compose_file")" up -d
    else
        log_info "Deploying service: $SERVICE_NAME"
        docker-compose -f "$(basename "$compose_file")" up -d "$SERVICE_NAME"
    fi

    log_success "Deployment completed"
}

# Show deployment status
show_status() {
    log_step "Deployment Status"

    local compose_file="$PROJECT_ROOT/$COMPOSE_FILE"
    cd "$(dirname "$compose_file")"

    log_info "Container Status:"
    docker-compose -f "$(basename "$compose_file")" ps

    log_info "Service URLs:"
    echo "  🌐 Frontend: http://localhost:3000"
    echo "  🔐 User Service: http://localhost:8000"
    echo "  📦 Inventory Service: http://localhost:8001"
    echo "  📋 Order Service: http://localhost:8002"
    echo "  🚪 API Gateway: http://localhost:8080"
    echo "  🗄️  Redis: localhost:6379"
}

# Main function
main() {
    # Parse and validate arguments first
    parse_arguments "$@"
    validate_arguments

    log_info "Starting Docker deployment (development)"
    log_info "Compose file: $COMPOSE_FILE"
    log_info "Service: $SERVICE_NAME"

    # Check prerequisites
    check_prerequisites

    # Execute actions
    if [[ "$BUILD_ONLY" == "true" ]]; then
        log_info "Action: Build only"
        build_services
    elif [[ "$DEPLOY_ONLY" == "true" ]]; then
        log_info "Action: Deploy only"
        deploy_services
    elif [[ "$BUILD_DEPLOY" == "true" ]]; then
        log_info "Action: Build + Deploy"
        build_services
        deploy_services
    fi

    # Show status
    show_status

    log_success "Docker deployment completed successfully!"
}

# Script execution
main "$@"
