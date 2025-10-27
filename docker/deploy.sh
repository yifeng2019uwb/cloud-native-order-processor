#!/bin/bash
# deploy.sh - Simple Docker service deployment script for CNOP
# Usage: ./deploy.sh [service_name] [action]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Show usage
show_usage() {
    cat << EOF
CNOP Docker Service Deployment Script

Usage: $0 [service_name] [action]

Services:
    all                    All services (auth, user, inventory, order, gateway, frontend)
    auth                   Auth service only
    user                   User service only
    inventory             Inventory service only
    order                 Order service only
    gateway               Gateway service only
    frontend              Frontend service only

Actions:
    deploy                 Deploy/redeploy service(s)
    restart               Restart service(s) without rebuild
    stop                  Stop service(s)
    start                 Start service(s)
    logs                  Show service logs
    status                Show service status

Examples:
    $0 auth deploy        # Deploy auth service
    $0 all restart        # Restart all services
    $0 user logs          # Show user service logs
    $0 all status         # Show all services status

EOF
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is not installed or not in PATH"
        exit 1
    fi
}

# Deploy a service (rebuild and start)
deploy_service() {
    local service="$1"
    log_info "Deploying $service service..."

    # Stop and remove existing container
    log_info "Stopping and removing existing $service container..."
    docker-compose stop "$service" 2>/dev/null || true
    docker-compose rm -f "$service" 2>/dev/null || true

    # Remove existing image
    log_info "Removing existing $service image..."
    docker rmi "docker-$service" 2>/dev/null || true

    # Clean build cache before rebuilding
    log_info "Cleaning Docker build cache..."
    docker builder prune -f

    # Build service
    log_info "Building $service service..."
    docker-compose build --no-cache "$service"

    # Start service
    log_info "Starting $service service..."
    docker-compose up -d "$service"

    # Wait for health check
    log_info "Waiting for $service to be healthy..."
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps "$service" | grep -q "healthy"; then
            log_success "$service service is healthy and running!"
            return 0
        fi

        if docker-compose ps "$service" | grep -q "unhealthy\|restarting"; then
            log_error "$service service is unhealthy or restarting"
            docker-compose logs "$service" --tail=20
            return 1
        fi

        log_info "Waiting for $service to be ready... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    log_error "$service service failed to become healthy after $max_attempts attempts"
    docker-compose logs "$service" --tail=20
    return 1
}

# Deploy all services
deploy_all() {
    log_info "Deploying all services..."

    local services=("auth_service" "user_service" "inventory_service" "order_service" "gateway")
    local failed_services=()

    for service in "${services[@]}"; do
        if ! deploy_service "$service"; then
            failed_services+=("$service")
        fi
    done

    if [ ${#failed_services[@]} -eq 0 ]; then
        log_success "All services deployed successfully!"
        show_status
    else
        log_error "Failed to deploy: ${failed_services[*]}"
        exit 1
    fi
}

# Restart a service
restart_service() {
    local service="$1"
    log_info "Restarting $service service..."
    docker-compose restart "$service"
    log_success "$service service restarted"
}

# Stop a service
stop_service() {
    local service="$1"
    log_info "Stopping $service service..."
    docker-compose stop "$service"
    log_success "$service service stopped"
}

# Start a service
start_service() {
    local service="$1"
    log_info "Starting $service service..."
    docker-compose up -d "$service"
    log_success "$service service started"
}

# Show service logs
show_logs() {
    local service="$1"
    log_info "Showing logs for $service service..."
    docker-compose logs -f "$service"
}

# Show service status
show_status() {
    log_info "Service Status:"
    echo ""
    docker-compose ps
    echo ""

    # Show health status
    log_info "Health Status:"
    for service in auth_service user_service inventory_service order_service gateway frontend; do
        if docker-compose ps "$service" | grep -q "healthy\|Up"; then
            log_success "$service: Healthy"
        elif docker-compose ps "$service" | grep -q "unhealthy\|restarting"; then
            log_error "$service: Unhealthy/Restarting"
        else
            log_warning "$service: Not running"
        fi
    done
}

# Main function
main() {
    # Check prerequisites
    check_docker_compose

    # Parse arguments
    if [ $# -lt 2 ]; then
        show_usage
        exit 1
    fi

    local service="$1"
    local action="$2"

    # Change to docker directory
    cd "$SCRIPT_DIR"

    # Execute action based on service and action
    case "$service" in
        all)
            case "$action" in
                deploy) deploy_all ;;
                restart) docker-compose restart ;;
                stop) docker-compose stop ;;
                start) docker-compose up -d ;;
                logs) docker-compose logs -f ;;
                status) show_status ;;
                *) log_error "Invalid action: $action"; show_usage; exit 1 ;;
            esac
            ;;
        auth|user|inventory|order|gateway|frontend)
            local service_name
            if [ "$service" = "gateway" ]; then
                service_name="gateway"
            elif [ "$service" = "frontend" ]; then
                service_name="frontend"
            else
                service_name="${service}_service"
            fi
            case "$action" in
                deploy) deploy_service "$service_name" ;;
                restart) restart_service "$service_name" ;;
                stop) stop_service "$service_name" ;;
                start) start_service "$service_name" ;;
                logs) show_logs "$service_name" ;;
                status) docker-compose ps "$service_name" ;;
                *) log_error "Invalid action: $action"; show_usage; exit 1 ;;
            esac
            ;;
        *)
            log_error "Invalid service: $service"
            show_usage
            exit 1
            ;;
    esac
}

# Script execution
main "$@"
