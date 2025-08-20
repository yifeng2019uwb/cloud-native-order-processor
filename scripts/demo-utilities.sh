#!/bin/bash
# scripts/demo-utilities.sh
# Demonstration script for Cloud Native Order Processor utilities
# Shows how to use logging, Docker, and Kubernetes utilities together

set -e

# Source all utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/logging.sh"
source "${SCRIPT_DIR}/docker-utils.sh"
source "${SCRIPT_DIR}/k8s-utils.sh"

# Demo configuration
DEMO_NAMESPACE="demo-utilities"
DEMO_COMPONENT="demo-app"

# Main demonstration function
main() {
    log_section "Cloud Native Order Processor - Utilities Demo"

    log_info "This script demonstrates the shared utilities for deployment automation"
    log_info "Components: Logging, Docker, Kubernetes utilities"

    # Test logging utilities
    demo_logging_utilities

    # Test Docker utilities
    demo_docker_utilities

    # Test Kubernetes utilities
    demo_k8s_utilities

    # Test integration
    demo_integration

    log_section "Demo Completed Successfully"
    log_success "All utilities are working correctly!"
}

# Demonstrate logging utilities
demo_logging_utilities() {
    log_section "Logging Utilities Demo"

    log_info "Testing different log levels and functions"
    log_success "Success message example"
    log_warning "Warning message example"
    log_error "Error message example (this is expected)"
    log_debug "Debug message example"
    log_step "Step message example"

    # Test progress indicator
    log_info "Testing progress indicator..."
    for i in {1..5}; do
        log_progress $i 5 "Demo Progress"
        sleep 0.5
    done

    # Test section headers
    log_section "Nested Section Demo"
    log_info "This shows how sections can be nested"
}

# Demonstrate Docker utilities
demo_docker_utilities() {
    log_section "Docker Utilities Demo"

    log_info "Checking Docker environment..."

    if check_docker_running; then
        log_success "Docker is running"

        if check_docker_daemon; then
            log_success "Docker daemon is accessible"

            # Test Docker resource listing
            log_info "Current Docker resources:"
            list_docker_resources "order-processor" || log_warning "No order-processor resources found"

        else
            log_warning "Docker daemon check failed"
        fi
    else
        log_warning "Docker is not running - skipping Docker tests"
    fi
}

# Demonstrate Kubernetes utilities
demo_k8s_utilities() {
    log_section "Kubernetes Utilities Demo"

    log_info "Checking Kubernetes environment..."

    if check_kubectl; then
        log_success "kubectl is available"

        # Try to connect to cluster (this might fail in demo environment)
        if check_k8s_cluster; then
            log_success "Connected to Kubernetes cluster"

            # Test namespace operations
            log_info "Testing namespace operations..."
            if create_namespace "$DEMO_NAMESPACE"; then
                log_success "Demo namespace created/verified"

                # List resources in demo namespace
                log_info "Resources in demo namespace:"
                list_namespace_resources "$DEMO_NAMESPACE"

                # Clean up demo namespace
                log_info "Cleaning up demo namespace..."
                kubectl delete namespace "$DEMO_NAMESPACE" --ignore-not-found=true
                log_success "Demo namespace cleaned up"
            fi

        else
            log_warning "Cannot connect to Kubernetes cluster - skipping K8s tests"
            log_info "This is expected in demo environments without active clusters"
        fi
    else
        log_warning "kubectl not available - skipping Kubernetes tests"
    fi
}

# Demonstrate utility integration
demo_integration() {
    log_section "Utility Integration Demo"

    log_info "Showing how utilities work together..."

    # Example deployment workflow
    log_step "Example: Complete deployment workflow"

    # 1. Check prerequisites
    log_info "1. Checking prerequisites..."
    check_docker_running || log_warning "Docker not available"
    check_kubectl || log_warning "kubectl not available"

    # 2. Build and deploy
    log_info "2. Build and deploy workflow (simulated)..."

    # Simulate building a component
    log_step "Building demo component"
    log_info "This would call: build_docker_image . demo-app latest"

    # Simulate deploying to Kubernetes
    log_step "Deploying to Kubernetes"
    log_info "This would call: apply_k8s_manifests kubernetes/demo/ default"

    # Simulate health checks
    log_step "Health checks"
    log_info "This would call: wait_for_rollout demo-app default"

    log_success "Integration demo completed"
}

# Error handling
trap 'log_error "Demo script failed with exit code $?"' ERR

# Run demo
main "$@"
