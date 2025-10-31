#!/bin/bash
# deploy.sh - Simple Docker service deployment script for CNOP
# Usage: ./deploy.sh [service_name] [action]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
USE_CACHE=true

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Show usage
show_usage() {
    cat << EOF
Usage: $0 [service_name] [action] [--no-cache]

Services: all, auth, user, inventory, order, gateway, frontend
Actions: deploy, rebuild, restart, stop, start, logs, status, clean

Examples:
    $0 auth deploy              # Deploy with cache
    $0 frontend rebuild         # Rebuild without cache
    $0 all status               # Show status
EOF
}

# Check Docker
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose not found"
        exit 1
    fi
}

# Check if service is healthy (15 lines)
is_service_healthy() {
    local service="$1"
    local container_id=$(docker-compose ps -q "$service" 2>/dev/null)
    [ -z "$container_id" ] && return 1

    local running=$(docker inspect --format='{{.State.Running}}' "$container_id" 2>/dev/null)
    [ "$running" != "true" ] && return 1

    local health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$container_id" 2>/dev/null)
    [ "$health" = "healthy" ] && return 0
    [ "$health" = "none" ] && docker-compose logs "$service" --tail=5 | grep -q "Uvicorn running" && return 0
    return 1
}

# Check if service changed (10 lines)
check_service_changed() {
    local service="$1"
    local image_id=$(docker images -q "docker-${service}" 2>/dev/null)
    [ -z "$image_id" ] && return 0

    local service_dir="$ROOT_DIR/services/${service}"
    [ ! -d "$service_dir" ] && return 0

    local newer=$(find "$service_dir" -type f -name "*.py" -newer "$image_id" 2>/dev/null | wc -l)
    [ "$newer" -gt 0 ] && return 0
    return 1
}

# Wait for service to be healthy - FIXED VERSION
wait_for_healthy() {
    local service="$1"
    local max_attempts=40
    local attempt=1

    log_info "Waiting for $service to be healthy..."

    local container_id=$(docker-compose ps -q "$service" 2>/dev/null)
    if [ -z "$container_id" ]; then
        log_error "$service container not found"
        return 1
    fi

    sleep 2

    while [ $attempt -le $max_attempts ]; do
        # Check if running
        local is_running=$(docker inspect --format='{{.State.Running}}' "$container_id" 2>/dev/null)
        if [ "$is_running" != "true" ]; then
            log_error "$service stopped"
            docker-compose logs "$service" --tail=20
            return 1
        fi

        # Check health
        local health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$container_id" 2>/dev/null)

        case "$health" in
            healthy)
                log_success "$service is healthy!"
                return 0
                ;;
            unhealthy)
                log_error "$service is unhealthy"
                docker-compose logs "$service" --tail=30
                return 1
                ;;
            none)
                # No health check - check logs
                if docker-compose logs "$service" --tail=10 | grep -q "Uvicorn running\|Application startup complete"; then
                    log_success "$service is running!"
                    return 0
                fi
                ;;
        esac

        log_info "Waiting... ($attempt/$max_attempts) [status: $health]"
        sleep 3
        attempt=$((attempt + 1))
    done

    log_error "$service failed to become healthy"
    docker-compose logs "$service" --tail=30
    return 1
}

# Deploy a service
deploy_service() {
    local service="$1"
    log_info "Deploying $service..."

    # Check if need redeploy service:
    if is_service_healthy "$service" && ! check_service_changed "$service"; then
        log_success "$service is already healthy (no changes)"
        return 0
    fi

    # Stop and remove
    docker-compose stop "$service" 2>/dev/null || true
    docker-compose rm -f "$service" 2>/dev/null || true

    # Build
    if [ "$USE_CACHE" = "true" ]; then
        docker-compose build "$service"
    else
        docker-compose build --no-cache "$service"
    fi

    # Start
    docker-compose up -d "$service"
    wait_for_healthy "$service"
}

# Deploy all
deploy_all() {
    log_info "Deploying all services..."
    local services=("auth_service" "user_service" "inventory_service" "order_service" "gateway" "frontend")
    local failed=()

    for service in "${services[@]}"; do
        if ! deploy_service "$service"; then
            failed+=("$service")
        fi
    done

    if [ ${#failed[@]} -eq 0 ]; then
        log_success "All services deployed!"
        show_status
    else
        log_error "Failed: ${failed[*]}"
        exit 1
    fi
}

# Rebuild without cache
rebuild_service() {
    local service="$1"
    log_warning "Rebuilding $service without cache..."
    docker-compose stop "$service" 2>/dev/null || true
    docker-compose rm -f "$service" 2>/dev/null || true
    docker rmi "docker-${service}" 2>/dev/null || true
    docker-compose build --no-cache "$service"
    docker-compose up -d "$service"
    wait_for_healthy "$service"
}

# Restart
restart_service() {
    local service="$1"
    log_info "Restarting $service..."
    docker-compose restart "$service"
    wait_for_healthy "$service"
}

# Stop
stop_service() {
    local service="$1"
    log_info "Stopping $service..."
    docker-compose stop "$service"
    log_success "$service stopped"
}

# Start
start_service() {
    local service="$1"
    log_info "Starting $service..."
    docker-compose up -d "$service"
    wait_for_healthy "$service"
}

# Logs
show_logs() {
    local service="$1"
    log_info "Logs for $service..."
    docker-compose logs -f --tail=100 "$service"
}

# Status
show_status() {
    log_info "Service Status:"
    echo ""
    docker-compose ps
    echo ""

    log_info "Health Status:"
    for service in auth_service user_service inventory_service order_service gateway frontend; do
        local container_id=$(docker-compose ps -q "$service" 2>/dev/null)
        if [ -n "$container_id" ]; then
            local health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$container_id" 2>/dev/null)
            case "$health" in
                healthy) log_success "$service: Healthy" ;;
                unhealthy) log_error "$service: Unhealthy" ;;
                starting) log_warning "$service: Starting" ;;
                none) log_info "$service: Running (no health check)" ;;
            esac
        else
            log_warning "$service: Not running"
        fi
    done
    echo ""
    docker system df
}

# Clean
clean_docker() {
    log_warning "Cleaning Docker..."
    docker container prune -f
    docker image prune -a -f
    docker builder prune -f
    docker volume prune -f
    log_success "Cleanup complete!"
    docker system df
}

# Main
main() {
    check_docker_compose

    if [ $# -lt 2 ]; then
        show_usage
        exit 1
    fi

    local service="$1"
    local action="$2"

    # Check for --no-cache
    if [ "${3:-}" = "--no-cache" ] || [ "$action" = "rebuild" ]; then
        USE_CACHE=false
    fi

    cd "$SCRIPT_DIR"

    case "$service" in
        all)
            case "$action" in
                deploy) deploy_all ;;
                rebuild) USE_CACHE=false; deploy_all ;;
                restart) docker-compose restart ;;
                stop) docker-compose stop ;;
                start) docker-compose up -d ;;
                logs) docker-compose logs -f ;;
                status) show_status ;;
                clean) clean_docker ;;
                *) log_error "Invalid action"; exit 1 ;;
            esac
            ;;
        auth|user|inventory|order|gateway|frontend)
            local svc_name="${service}"
            [ "$service" != "gateway" ] && [ "$service" != "frontend" ] && svc_name="${service}_service"

            case "$action" in
                deploy) deploy_service "$svc_name" ;;
                rebuild) rebuild_service "$svc_name" ;;
                restart) restart_service "$svc_name" ;;
                stop) stop_service "$svc_name" ;;
                start) start_service "$svc_name" ;;
                logs) show_logs "$svc_name" ;;
                status) docker-compose ps "$svc_name" ;;
                *) log_error "Invalid action"; exit 1 ;;
            esac
            ;;
        *)
            log_error "Invalid service"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"