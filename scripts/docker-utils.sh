#!/bin/bash
# scripts/docker-utils.sh
# Shared Docker utilities for Cloud Native Order Processor
# Provides Docker operations for development and deployment

# Source logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/logging.sh"

# Docker configuration
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"localhost:5000"}
DOCKER_NAMESPACE=${DOCKER_NAMESPACE:-"order-processor"}
DOCKER_BUILD_ARGS=${DOCKER_BUILD_ARGS:-""}
DOCKER_PUSH_RETRIES=${DOCKER_PUSH_RETRIES:-3}

# Docker health check timeout
DOCKER_HEALTH_TIMEOUT=${DOCKER_HEALTH_TIMEOUT:-60}

# Check if Docker is running
check_docker_running() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running or not accessible"
        return 1
    fi
    log_debug "Docker is running"
    return 0
}

# Check Docker daemon status
check_docker_daemon() {
    if ! docker version >/dev/null 2>&1; then
        log_error "Docker daemon is not accessible"
        return 1
    fi
    log_info "Docker daemon is accessible"
    return 0
}

# Build Docker image
build_docker_image() {
    local context="$1"
    local image_name="$2"
    local tag="${3:-latest}"
    local dockerfile="${4:-Dockerfile}"
    local build_args="${5:-$DOCKER_BUILD_ARGS}"

    log_step "Building Docker image: $image_name:$tag"

    if [[ ! -d "$context" ]]; then
        log_error "Build context directory does not exist: $context"
        return 1
    fi

    if [[ ! -f "$context/$dockerfile" ]]; then
        log_error "Dockerfile not found: $context/$dockerfile"
        return 1
    fi

    local full_image_name="$DOCKER_NAMESPACE/$image_name:$tag"

    log_command "cd $context && docker build -t $full_image_name -f $dockerfile $build_args ."

    if cd "$context" && docker build -t "$full_image_name" -f "$dockerfile" $build_args .; then
        log_success "Docker image built successfully: $full_image_name"
        return 0
    else
        log_error "Failed to build Docker image: $full_image_name"
        return 1
    fi
}

# Build Docker image with no cache
build_docker_image_no_cache() {
    local context="$1"
    local image_name="$2"
    local tag="${3:-latest}"
    local dockerfile="${4:-Dockerfile}"

    log_step "Building Docker image (no cache): $image_name:$tag"

    local build_args="$DOCKER_BUILD_ARGS --no-cache"
    build_docker_image "$context" "$image_name" "$tag" "$dockerfile" "$build_args"
}

# Tag Docker image
tag_docker_image() {
    local source_image="$1"
    local target_image="$2"
    local source_tag="${3:-latest}"
    local target_tag="${4:-latest}"

    local source_full="$DOCKER_NAMESPACE/$source_image:$source_tag"
    local target_full="$DOCKER_NAMESPACE/$target_image:$target_tag"

    log_step "Tagging Docker image: $source_full -> $target_full"

    if docker tag "$source_full" "$target_full"; then
        log_success "Docker image tagged successfully"
        return 0
    else
        log_error "Failed to tag Docker image"
        return 1
    fi
}

# Push Docker image to registry
push_docker_image() {
    local image_name="$1"
    local tag="${2:-latest}"
    local registry="${3:-$DOCKER_REGISTRY}"

    local full_image_name="$DOCKER_NAMESPACE/$image_name:$tag"
    local registry_image="$registry/$full_image_name"

    log_step "Pushing Docker image to registry: $registry_image"

    # Tag for registry
    if ! docker tag "$full_image_name" "$registry_image"; then
        log_error "Failed to tag image for registry"
        return 1
    fi

    # Push with retries
    local attempt=1
    while [[ $attempt -le $DOCKER_PUSH_RETRIES ]]; do
        log_info "Push attempt $attempt/$DOCKER_PUSH_RETRIES"

        if docker push "$registry_image"; then
            log_success "Docker image pushed successfully to registry"
            return 0
        else
            log_warning "Push attempt $attempt failed"
            if [[ $attempt -lt $DOCKER_PUSH_RETRIES ]]; then
                log_info "Retrying in 5 seconds..."
                sleep 5
            fi
        fi
        ((attempt++))
    done

    log_error "Failed to push Docker image after $DOCKER_PUSH_RETRIES attempts"
    return 1
}

# Run Docker container
run_docker_container() {
    local image_name="$1"
    local container_name="$2"
    local ports="${3:-}"
    local environment="${4:-}"
    local volumes="${5:-}"
    local network="${6:-}"
    local detach="${7:-true}"

    local full_image_name="$DOCKER_NAMESPACE/$image_name:latest"

    log_step "Running Docker container: $container_name"

    # Build run command
    local run_cmd="docker run"

    if [[ "$detach" == "true" ]]; then
        run_cmd="$run_cmd -d"
    fi

    if [[ -n "$container_name" ]]; then
        run_cmd="$run_cmd --name $container_name"
    fi

    if [[ -n "$ports" ]]; then
        run_cmd="$run_cmd -p $ports"
    fi

    if [[ -n "$environment" ]]; then
        run_cmd="$run_cmd -e $environment"
    fi

    if [[ -n "$volumes" ]]; then
        run_cmd="$run_cmd -v $volumes"
    fi

    if [[ -n "$network" ]]; then
        run_cmd="$run_cmd --network $network"
    fi

    run_cmd="$run_cmd $full_image_name"

    log_command "$run_cmd"

    if eval "$run_cmd"; then
        log_success "Docker container started successfully: $container_name"
        return 0
    else
        log_error "Failed to start Docker container: $container_name"
        return 1
    fi
}

# Stop Docker container
stop_docker_container() {
    local container_name="$1"
    local timeout="${2:-10}"

    log_step "Stopping Docker container: $container_name"

    if docker stop --time="$timeout" "$container_name"; then
        log_success "Docker container stopped successfully: $container_name"
        return 0
    else
        log_error "Failed to stop Docker container: $container_name"
        return 1
    fi
}

# Remove Docker container
remove_docker_container() {
    local container_name="$1"
    local force="${2:-false}"

    log_step "Removing Docker container: $container_name"

    local remove_cmd="docker rm"
    if [[ "$force" == "true" ]]; then
        remove_cmd="$remove_cmd -f"
    fi
    remove_cmd="$remove_cmd $container_name"

    if eval "$remove_cmd"; then
        log_success "Docker container removed successfully: $container_name"
        return 0
    else
        log_error "Failed to remove Docker container: $container_name"
        return 1
    fi
}

# Check container health
check_container_health() {
    local container_name="$1"
    local timeout="${2:-$DOCKER_HEALTH_TIMEOUT}"

    log_step "Checking container health: $container_name"

    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))

    while [[ $(date +%s) -lt $end_time ]]; do
        local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null)

        if [[ "$health_status" == "healthy" ]]; then
            log_success "Container is healthy: $container_name"
            return 0
        elif [[ "$health_status" == "unhealthy" ]]; then
            log_error "Container is unhealthy: $container_name"
            return 1
        fi

        log_info "Waiting for container to be healthy... (${health_status:-unknown})"
        sleep 5
    done

    log_error "Container health check timeout after ${timeout}s: $container_name"
    return 1
}

# Get container logs
get_container_logs() {
    local container_name="$1"
    local lines="${2:-100}"
    local follow="${3:-false}"

    log_step "Getting container logs: $container_name (last $lines lines)"

    local log_cmd="docker logs"
    if [[ "$follow" == "true" ]]; then
        log_cmd="$log_cmd -f"
    fi
    log_cmd="$log_cmd --tail $lines $container_name"

    log_command "$log_cmd"
    eval "$log_cmd"
}

# Clean up Docker resources
cleanup_docker_resources() {
    local pattern="$1"

    log_step "Cleaning up Docker resources matching: $pattern"

    # Stop containers
    local containers=$(docker ps -a --filter "name=$pattern" --format "{{.Names}}")
    if [[ -n "$containers" ]]; then
        log_info "Stopping containers: $containers"
        echo "$containers" | xargs -r docker stop
    fi

    # Remove containers
    if [[ -n "$containers" ]]; then
        log_info "Removing containers: $containers"
        echo "$containers" | xargs -r docker rm -f
    fi

    # Remove images
    local images=$(docker images --filter "reference=$pattern" --format "{{.Repository}}:{{.Tag}}")
    if [[ -n "$images" ]]; then
        log_info "Removing images: $images"
        echo "$images" | xargs -r docker rmi -f
    fi

    log_success "Docker cleanup completed"
}

# List Docker resources
list_docker_resources() {
    local pattern="${1:-$DOCKER_NAMESPACE}"

    log_step "Listing Docker resources for: $pattern"

    echo "=== Containers ==="
    docker ps -a --filter "name=$pattern" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    echo -e "\n=== Images ==="
    docker images --filter "reference=$pattern" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

    echo -e "\n=== Networks ==="
    docker network ls --filter "name=$pattern" --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"
}

# Export functions for use in other scripts
export -f check_docker_running check_docker_daemon
export -f build_docker_image build_docker_image_no_cache tag_docker_image
export -f push_docker_image run_docker_container stop_docker_container
export -f remove_docker_container check_container_health get_container_logs
export -f cleanup_docker_resources list_docker_resources
