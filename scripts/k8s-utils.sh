#!/bin/bash
# scripts/k8s-utils.sh
# Shared Kubernetes utilities for Cloud Native Order Processor
# Provides K8s operations for deployment and management

# Source logging utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/logging.sh"

# Kubernetes configuration
K8S_NAMESPACE=${K8S_NAMESPACE:-"default"}
K8S_CONTEXT=${K8S_CONTEXT:-""}
K8S_TIMEOUT=${K8S_TIMEOUT:-300}
K8S_ROLLOUT_TIMEOUT=${K8S_ROLLOUT_TIMEOUT:-600}
K8S_HEALTH_CHECK_INTERVAL=${K8S_HEALTH_CHECK_INTERVAL:-10}

# Check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        return 1
    fi
    log_debug "kubectl is available"
    return 0
}

# Check Kubernetes cluster connectivity
check_k8s_cluster() {
    log_step "Checking Kubernetes cluster connectivity"

    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        return 1
    fi

    local cluster_info=$(kubectl cluster-info | head -n 1)
    log_success "Connected to Kubernetes cluster: $cluster_info"
    return 0
}

# Set Kubernetes context
set_k8s_context() {
    local context="$1"

    if [[ -z "$context" ]]; then
        log_warning "No Kubernetes context specified"
        return 0
    fi

    log_step "Setting Kubernetes context: $context"

    if kubectl config use-context "$context"; then
        log_success "Kubernetes context set to: $context"
        K8S_CONTEXT="$context"
        return 0
    else
        log_error "Failed to set Kubernetes context: $context"
        return 1
    fi
}

# Check if namespace exists
check_namespace() {
    local namespace="${1:-$K8S_NAMESPACE}"

    log_debug "Checking if namespace exists: $namespace"

    if kubectl get namespace "$namespace" &> /dev/null; then
        log_debug "Namespace exists: $namespace"
        return 0
    else
        log_debug "Namespace does not exist: $namespace"
        return 1
    fi
}

# Create namespace if it doesn't exist
create_namespace() {
    local namespace="${1:-$K8S_NAMESPACE}"

    if check_namespace "$namespace"; then
        log_info "Namespace already exists: $namespace"
        return 0
    fi

    log_step "Creating namespace: $namespace"

    if kubectl create namespace "$namespace"; then
        log_success "Namespace created successfully: $namespace"
        return 0
    else
        log_error "Failed to create namespace: $namespace"
        return 1
    fi
}

# Apply Kubernetes manifests
apply_k8s_manifests() {
    local manifest_path="$1"
    local namespace="${2:-$K8S_NAMESPACE}"

    log_step "Applying Kubernetes manifests: $manifest_path"

    if [[ ! -f "$manifest_path" ]] && [[ ! -d "$manifest_path" ]]; then
        log_error "Manifest path does not exist: $manifest_path"
        return 1
    fi

    # Create namespace if it doesn't exist
    create_namespace "$namespace"

    local apply_cmd="kubectl apply"
    if [[ -n "$namespace" ]]; then
        apply_cmd="$apply_cmd -n $namespace"
    fi

    if [[ -d "$manifest_path" ]]; then
        apply_cmd="$apply_cmd -k $manifest_path"
    else
        apply_cmd="$apply_cmd -f $manifest_path"
    fi

    log_command "$apply_cmd"

    if eval "$apply_cmd"; then
        log_success "Kubernetes manifests applied successfully"
        return 0
    else
        log_error "Failed to apply Kubernetes manifests"
        return 1
    fi
}

# Delete Kubernetes resources
delete_k8s_resources() {
    local manifest_path="$1"
    local namespace="${2:-$K8S_NAMESPACE}"

    log_step "Deleting Kubernetes resources: $manifest_path"

    if [[ ! -f "$manifest_path" ]] && [[ ! -d "$manifest_path" ]]; then
        log_error "Manifest path does not exist: $manifest_path"
        return 1
    fi

    local delete_cmd="kubectl delete"
    if [[ -n "$namespace" ]]; then
        delete_cmd="$delete_cmd -n $namespace"
    fi

    if [[ -d "$manifest_path" ]]; then
        delete_cmd="$delete_cmd -k $manifest_path"
    else
        delete_cmd="$delete_cmd -f $manifest_path"
    fi

    log_command "$delete_cmd"

    if eval "$delete_cmd"; then
        log_success "Kubernetes resources deleted successfully"
        return 0
    else
        log_error "Failed to delete Kubernetes resources"
        return 1
    fi
}

# Wait for deployment rollout
wait_for_rollout() {
    local deployment="$1"
    local namespace="${2:-$K8S_NAMESPACE}"
    local timeout="${3:-$K8S_ROLLOUT_TIMEOUT}"

    log_step "Waiting for deployment rollout: $deployment"

    local rollout_cmd="kubectl rollout status"
    if [[ -n "$namespace" ]]; then
        rollout_cmd="$rollout_cmd -n $namespace"
    fi
    rollout_cmd="$rollout_cmd deployment/$deployment --timeout=${timeout}s"

    log_command "$rollout_cmd"

    if eval "$rollout_cmd"; then
        log_success "Deployment rollout completed: $deployment"
        return 0
    else
        log_error "Deployment rollout failed or timed out: $deployment"
        return 1
    fi
}

# Check deployment status
check_deployment_status() {
    local deployment="$1"
    local namespace="${2:-$K8S_NAMESPACE}"

    log_debug "Checking deployment status: $deployment"

    local status_cmd="kubectl get deployment"
    if [[ -n "$namespace" ]]; then
        status_cmd="$status_cmd -n $namespace"
    fi
    status_cmd="$status_cmd $deployment -o jsonpath='{.status.conditions[?(@.type==\"Available\")].status}'"

    local status=$(eval "$status_cmd" 2>/dev/null)

    if [[ "$status" == "True" ]]; then
        log_debug "Deployment is available: $deployment"
        return 0
    else
        log_debug "Deployment is not available: $deployment (status: $status)"
        return 1
    fi
}

# Scale deployment
scale_deployment() {
    local deployment="$1"
    local replicas="$2"
    local namespace="${3:-$K8S_NAMESPACE}"

    log_step "Scaling deployment: $deployment to $replicas replicas"

    local scale_cmd="kubectl scale deployment"
    if [[ -n "$namespace" ]]; then
        scale_cmd="$scale_cmd -n $namespace"
    fi
    scale_cmd="$scale_cmd $deployment --replicas=$replicas"

    log_command "$scale_cmd"

    if eval "$scale_cmd"; then
        log_success "Deployment scaled successfully: $deployment -> $replicas replicas"
        return 0
    else
        log_error "Failed to scale deployment: $deployment"
        return 1
    fi
}

# Get pod logs
get_pod_logs() {
    local pod_name="$1"
    local namespace="${2:-$K8S_NAMESPACE}"
    local lines="${3:-100}"
    local follow="${4:-false}"

    log_step "Getting pod logs: $pod_name (last $lines lines)"

    local log_cmd="kubectl logs"
    if [[ -n "$namespace" ]]; then
        log_cmd="$log_cmd -n $namespace"
    fi
    if [[ "$follow" == "true" ]]; then
        log_cmd="$log_cmd -f"
    fi
    log_cmd="$log_cmd --tail=$lines $pod_name"

    log_command "$log_cmd"
    eval "$log_cmd"
}

# Check pod health
check_pod_health() {
    local pod_name="$1"
    local namespace="${2:-$K8S_NAMESPACE}"
    local timeout="${3:-$K8S_TIMEOUT}"

    log_step "Checking pod health: $pod_name"

    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))

    while [[ $(date +%s) -lt $end_time ]]; do
        local status_cmd="kubectl get pod"
        if [[ -n "$namespace" ]]; then
            status_cmd="$status_cmd -n $namespace"
        fi
        status_cmd="$status_cmd $pod_name -o jsonpath='{.status.phase}'"

        local phase=$(eval "$status_cmd" 2>/dev/null)

        if [[ "$phase" == "Running" ]]; then
            log_success "Pod is running: $pod_name"
            return 0
        elif [[ "$phase" == "Failed" ]] || [[ "$phase" == "Error" ]]; then
            log_error "Pod failed: $pod_name (phase: $phase)"
            return 1
        fi

        log_info "Waiting for pod to be ready... (phase: ${phase:-unknown})"
        sleep $K8S_HEALTH_CHECK_INTERVAL
    done

    log_error "Pod health check timeout after ${timeout}s: $pod_name"
    return 1
}

# Get service endpoints
get_service_endpoints() {
    local service_name="$1"
    local namespace="${2:-$K8S_NAMESPACE}"

    log_step "Getting service endpoints: $service_name"

    local endpoints_cmd="kubectl get endpoints"
    if [[ -n "$namespace" ]]; then
        endpoints_cmd="$endpoints_cmd -n $namespace"
    fi
    endpoints_cmd="$endpoints_cmd $service_name -o wide"

    log_command "$endpoints_cmd"
    eval "$endpoints_cmd"
}

# Port forward service
port_forward_service() {
    local service_name="$1"
    local local_port="$2"
    local service_port="${3:-80}"
    local namespace="${4:-$K8S_NAMESPACE}"

    log_step "Setting up port forward: localhost:$local_port -> $service_name:$service_port"

    local port_forward_cmd="kubectl port-forward"
    if [[ -n "$namespace" ]]; then
        port_forward_cmd="$port_forward_cmd -n $namespace"
    fi
    port_forward_cmd="$port_forward_cmd service/$service_name $local_port:$service_port"

    log_command "$port_forward_cmd"
    log_info "Port forward started. Press Ctrl+C to stop."

    eval "$port_forward_cmd"
}

# Get resource usage
get_resource_usage() {
    local namespace="${1:-$K8S_NAMESPACE}"

    log_step "Getting resource usage for namespace: $namespace"

    echo "=== Pod Resource Usage ==="
    kubectl top pods -n "$namespace" 2>/dev/null || log_warning "Metrics server not available"

    echo -e "\n=== Node Resource Usage ==="
    kubectl top nodes 2>/dev/null || log_warning "Metrics server not available"
}

# Clean up failed pods
cleanup_failed_pods() {
    local namespace="${1:-$K8S_NAMESPACE}"

    log_step "Cleaning up failed pods in namespace: $namespace"

    local failed_pods=$(kubectl get pods -n "$namespace" --field-selector=status.phase=Failed -o jsonpath='{.items[*].metadata.name}')

    if [[ -n "$failed_pods" ]]; then
        log_info "Deleting failed pods: $failed_pods"
        echo "$failed_pods" | xargs -r kubectl delete pod -n "$namespace"
        log_success "Failed pods cleaned up"
    else
        log_info "No failed pods found"
    fi
}

# List all resources in namespace
list_namespace_resources() {
    local namespace="${1:-$K8S_NAMESPACE}"

    log_step "Listing all resources in namespace: $namespace"

    echo "=== Deployments ==="
    kubectl get deployments -n "$namespace"

    echo -e "\n=== Services ==="
    kubectl get services -n "$namespace"

    echo -e "\n=== Pods ==="
    kubectl get pods -n "$namespace"

    echo -e "\n=== ConfigMaps ==="
    kubectl get configmaps -n "$namespace"

    echo -e "\n=== Secrets ==="
    kubectl get secrets -n "$namespace"
}

# Export functions for use in other scripts
export -f check_kubectl check_k8s_cluster set_k8s_context
export -f check_namespace create_namespace apply_k8s_manifests
export -f delete_k8s_resources wait_for_rollout check_deployment_status
export -f scale_deployment get_pod_logs check_pod_health
export -f get_service_endpoints port_forward_service get_resource_usage
export -f cleanup_failed_pods list_namespace_resources
