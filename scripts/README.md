# Cloud Native Order Processor - Shared Utilities

This directory contains shared utility scripts that provide consistent functionality across all deployment and development scripts.

## 📁 Available Utilities

### 1. `logging.sh` - Logging and Output Utilities
Provides consistent logging functions with color coding, timestamps, and log levels.

**Features:**
- Color-coded log levels (INFO, SUCCESS, WARNING, ERROR, DEBUG, STEP)
- Timestamp formatting
- Configurable log levels via `LOG_LEVEL` environment variable
- Section headers with visual separators
- Progress indicators with progress bars
- Command logging and result tracking

**Usage:**
```bash
source scripts/logging.sh

log_info "Starting deployment..."
log_success "Component deployed successfully"
log_warning "Resource usage is high"
log_error "Deployment failed"
log_debug "Debug information"
log_step "Building component..."
log_section "Deployment Phase 1"
```

**Environment Variables:**
- `LOG_LEVEL`: Set log level (0=INFO, 1=WARN, 2=ERROR, 3=DEBUG)

### 2. `docker-utils.sh` - Docker Operations
Provides Docker-related functions for building, running, and managing containers.

**Features:**
- Docker daemon and runtime checks
- Image building with context and Dockerfile support
- Container lifecycle management (run, stop, remove)
- Health checks and monitoring
- Resource cleanup and listing
- Registry operations (tag, push)

**Usage:**
```bash
source scripts/docker-utils.sh

# Check Docker environment
check_docker_running
check_docker_daemon

# Build and run containers
build_docker_image "./frontend" "frontend" "latest"
run_docker_container "frontend" "frontend-app" "3000:80"
check_container_health "frontend-app"

# Cleanup
cleanup_docker_resources "order-processor"
```

**Environment Variables:**
- `DOCKER_REGISTRY`: Docker registry URL (default: localhost:5000)
- `DOCKER_NAMESPACE`: Image namespace (default: order-processor)
- `DOCKER_BUILD_ARGS`: Additional build arguments
- `DOCKER_PUSH_RETRIES`: Number of push retries (default: 3)
- `DOCKER_HEALTH_TIMEOUT`: Health check timeout in seconds (default: 60)

### 3. `k8s-utils.sh` - Kubernetes Operations
Provides Kubernetes-related functions for deployment and management.

**Features:**
- Cluster connectivity checks
- Namespace management
- Manifest application and deletion
- Deployment rollout monitoring
- Pod health checks and scaling
- Service management and port forwarding
- Resource monitoring and cleanup

**Usage:**
```bash
source scripts/k8s-utils.sh

# Check Kubernetes environment
check_kubectl
check_k8s_cluster

# Deploy and manage resources
create_namespace "my-app"
apply_k8s_manifests "kubernetes/manifests/" "my-app"
wait_for_rollout "my-deployment" "my-app"
check_pod_health "my-pod" "my-app"

# Monitor and scale
scale_deployment "my-deployment" 3 "my-app"
get_resource_usage "my-app"
```

**Environment Variables:**
- `K8S_NAMESPACE`: Default namespace (default: default)
- `K8S_CONTEXT`: Kubernetes context to use
- `K8S_TIMEOUT`: Default timeout in seconds (default: 300)
- `K8S_ROLLOUT_TIMEOUT`: Rollout timeout in seconds (default: 600)
- `K8S_HEALTH_CHECK_INTERVAL`: Health check interval in seconds (default: 10)

## 🚀 Integration with deploy.sh

The `deploy.sh` script can be enhanced to use these utilities:

```bash
# In deploy.sh, add at the top:
source "${SCRIPT_DIR}/scripts/logging.sh"
source "${SCRIPT_DIR}/scripts/docker-utils.sh"
source "${SCRIPT_DIR}/scripts/k8s-utils.sh"

# Then use the utilities:
log_section "Starting Deployment"
check_docker_running
check_k8s_cluster

# Build components
build_docker_image "./frontend" "frontend" "latest"
build_docker_image "./gateway" "gateway" "latest"

# Deploy to Kubernetes
apply_k8s_manifests "kubernetes/prod/frontend/" "default"
wait_for_rollout "frontend" "default"
```

## 🧪 Testing Utilities

Use the demo script to test all utilities:

```bash
./scripts/demo-utilities.sh
```

This script demonstrates:
- All logging functions
- Docker environment checks
- Kubernetes connectivity tests
- Utility integration examples

## 🔧 Customization

### Adding New Log Levels
```bash
# In logging.sh, add new level constants:
LOG_LEVEL_VERBOSE=4

# Add corresponding function:
log_verbose() {
    if [[ $DEFAULT_LOG_LEVEL -le $LOG_LEVEL_VERBOSE ]]; then
        local timestamp=$(date +"$TIMESTAMP_FORMAT")
        printf "${MAGENTA}[VERBOSE]${NC} [%s] %s\n" "$timestamp" "$1"
    fi
}
```

### Adding New Docker Functions
```bash
# In docker-utils.sh, add new function:
build_multi_stage_image() {
    local context="$1"
    local image_name="$2"
    local dockerfile="${3:-Dockerfile.multi}"

    log_step "Building multi-stage Docker image: $image_name"
    # Implementation here
}
```

### Adding New Kubernetes Functions
```bash
# In k8s-utils.sh, add new function:
restart_deployment() {
    local deployment="$1"
    local namespace="${2:-$K8S_NAMESPACE}"

    log_step "Restarting deployment: $deployment"
    kubectl rollout restart deployment/$deployment -n $namespace
}
```

## 📋 Best Practices

1. **Always source utilities at the beginning** of your scripts
2. **Use consistent log levels** across all scripts
3. **Handle errors gracefully** using the utility functions
4. **Set appropriate timeouts** for long-running operations
5. **Clean up resources** after operations complete
6. **Use environment variables** for configuration
7. **Test utilities** before using in production scripts

## 🐛 Troubleshooting

### Common Issues

1. **Path not found errors**: Ensure you're sourcing from the correct directory
2. **Permission denied**: Make sure utility scripts are executable (`chmod +x`)
3. **Function not found**: Check that utilities are properly sourced
4. **Environment variables not set**: Verify environment variable configuration

### Debug Mode

Enable debug logging to see detailed information:

```bash
export LOG_LEVEL=3  # Enable debug mode
./your-script.sh
```

### Testing Individual Utilities

Test specific utilities in isolation:

```bash
# Test logging only
source scripts/logging.sh
log_info "Test message"

# Test Docker utilities only
source scripts/docker-utils.sh
check_docker_running

# Test Kubernetes utilities only
source scripts/k8s-utils.sh
check_kubectl
```

## 📚 Examples

See the `demo-utilities.sh` script for comprehensive examples of how to use all utilities together in a real deployment workflow.