#!/bin/bash
# deploy.sh
# Root deployment orchestrator script
# Coordinates deployment of all components with proper order and environment support

set -e

# Script configuration
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="${ROOT_DIR}/scripts"

# Component directories - Clear and simple naming
FRONTEND_DIR="${ROOT_DIR}/frontend"
GATEWAY_DIR="${ROOT_DIR}/gateway"
USER_DIR="${ROOT_DIR}/services/user_service"
INVENTORY_DIR="${ROOT_DIR}/services/inventory_service"
ORDER_DIR="${ROOT_DIR}/services/order_service"

# Source shared utilities
source "${SCRIPTS_DIR}/logging.sh"
source "${SCRIPTS_DIR}/prerequisites-checker.sh"
source "${SCRIPTS_DIR}/config-loader.sh"
source "${SCRIPTS_DIR}/docker-utils.sh"
source "${SCRIPTS_DIR}/k8s-utils.sh"

# Usage function
show_usage() {
    cat << EOF
Cloud Native Order Processor - Deployment Orchestrator

Usage: $0 {component} {environment} [options]

Components:
    all                    Deploy all components in proper order
    frontend               Deploy frontend application
    gateway                Deploy API gateway
    services               Deploy all microservices
    user                  Deploy user service only
    inventory             Deploy inventory service only
    order                 Deploy order service only
    auth                  Deploy auth service only
    monitoring             Deploy monitoring stack

Environments:
    dev                    Local development (Docker + Kind)
    prod                   Production (EKS)

Options:
    None - Pure deployment only

Examples:
    $0 all prod                    # Deploy everything to production
    $0 frontend dev                # Deploy frontend to dev environment
    $0 services prod               # Deploy services to prod
    $0 user dev                    # Deploy user service to dev
    $0 monitoring dev              # Deploy monitoring to dev

Deployment Order (for 'all'):
    1. Infrastructure (K8s, networking)
    2. Monitoring (Prometheus, Grafana, Loki)
    3. Services (user, inventory, order)
    4. Gateway (API gateway)
    5. Frontend (React application)

EOF
}

# Show development URLs with new port configuration
show_dev_urls() {
    log_info "Development URLs (new port configuration):"
    log_info "  Frontend: http://localhost:30003"
    log_info "  Gateway:  http://localhost:30002"
    log_info "  Grafana:  http://localhost:30001 (admin/admin123)"
    log_info "  Auth Service: http://localhost:30007"
    log_info "  User Service: http://localhost:30004"
    log_info "  Inventory Service: http://localhost:30005"
    log_info "  Order Service: http://localhost:30006"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking deployment prerequisites..."

    # Use shared prerequisites checker
    if ! check_all_tools; then
        log_error "Prerequisites check failed"
        exit 1
    fi

    # Check Docker specifically
    if ! check_docker; then
        log_error "Docker check failed"
        exit 1
    fi

    # Check Kubernetes
    if ! check_k8s; then
        log_warning "Kubernetes check failed - this may be normal for local dev"
    fi

    log_success "Prerequisites check passed"
}

# Deploy infrastructure
deploy_infrastructure() {
    log_info "Deploying infrastructure for $ENVIRONMENT..."

        if [[ "$ENVIRONMENT" == "dev" ]]; then
        # Dev: Kind cluster setup
        log_info "Setting up Kind cluster..."
        if command -v kind &> /dev/null; then
            # Check if cluster already exists
            if ! kind get clusters | grep -q "order-processor"; then
                log_info "Creating Kind cluster: order-processor"
                kind create cluster --config kubernetes/kind-config.yaml --name order-processor
            else
                log_info "Kind cluster 'order-processor' already exists"
            fi

            # Check if nodes exist and are ready
            log_info "Checking cluster nodes..."
            local node_count=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
            if [[ $node_count -eq 0 ]]; then
                log_warning "No nodes found in existing cluster, recreating..."
                log_info "Deleting existing cluster..."
                kind delete cluster --name order-processor
                log_info "Creating fresh Kind cluster: order-processor"
                kind create cluster --config kubernetes/kind-config.yaml --name order-processor
            else
                log_info "Found $node_count existing nodes"
            fi

            # Wait for cluster to be ready
            log_info "Waiting for cluster to be ready..."
            kubectl wait --for=condition=Ready nodes --all --timeout=300s

            # Verify cluster health
            log_info "Verifying cluster health..."
            local ready_nodes=$(kubectl get nodes --no-headers 2>/dev/null | grep -c "Ready")
            local total_nodes=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
            if [[ $ready_nodes -eq $total_nodes && $total_nodes -gt 0 ]]; then
                log_success "Cluster is healthy: $ready_nodes/$total_nodes nodes ready"
            else
                log_warning "Cluster health check: $ready_nodes/$total_nodes nodes ready"
            fi
        else
            log_error "Kind is not installed. Please install Kind first."
            exit 1
        fi

    # Apply base configurations
    log_info "Applying Kubernetes base configurations..."
    if [[ -d "kubernetes/base" ]]; then
        kubectl apply -k kubernetes/base/
        log_success "Base configurations applied"
    else
        log_warning "kubernetes/base directory not found"
    fi

    elif [[ "$ENVIRONMENT" == "prod" ]]; then
        # Prod: EKS deployment
        log_info "Deploying to EKS..."
        # cd terraform && terraform apply -auto-approve
        log_warning "EKS deployment skipped (commented out for demo)"

        # Apply production configurations
        log_info "Applying production Kubernetes configurations..."
        # kubectl apply -k kubernetes/prod/
        log_warning "Prod K8s configs skipped (commented out for demo)"
    fi

    log_success "Infrastructure deployment completed"
}

# Deploy monitoring stack
deploy_monitoring() {
    log_info "Deploying monitoring stack for $ENVIRONMENT..."

    if [[ "$ENVIRONMENT" == "dev" ]]; then
        # Dev: Kubernetes monitoring
        log_info "Monitoring stack already deployed with infrastructure..."
        log_success "Kubernetes monitoring stack is ready"

    elif [[ "$ENVIRONMENT" == "prod" ]]; then
        # Prod: Kubernetes monitoring
        log_info "Deploying monitoring to Kubernetes..."
        kubectl apply -f kubernetes/base/monitoring.yaml
        log_success "Kubernetes monitoring stack deployed"
    fi

    log_success "Monitoring deployment completed"
}

# Deploy a service
deploy_service() {
    local service="$1"

    log_info "Deploying $service to $ENVIRONMENT..."

    if [[ "$ENVIRONMENT" == "dev" ]]; then
        # Dev: Local Kubernetes deployment (Kind)
        log_info "Deploying $service to local Kubernetes..."
        cd "$ROOT_DIR"

        # Build service Docker image first (like working scripts)
        log_info "Building $service Docker image..."
        docker build --no-cache -t order-processor-${service}_service:latest -f docker/${service}-service/Dockerfile .

        # Deploy to Kubernetes using working pattern
        log_info "Applying Kubernetes manifests for $service..."
        kubectl apply -k kubernetes/base/
        kubectl apply -k kubernetes/dev/

        # Wait for deployment to be ready
        log_info "Waiting for $service deployment to be ready..."
        kubectl rollout status deployment/${service}-service -n order-processor --timeout=300s

        log_success "Service '$service' deployed to Kubernetes"

    elif [[ "$ENVIRONMENT" == "prod" ]]; then
        # Prod: Kubernetes deployment
        log_info "Deploying $service to Kubernetes..."
        kubectl apply -k kubernetes/base/
        kubectl apply -k kubernetes/prod/

        # Wait for rollout
        kubectl rollout status deployment/${service}-service -n order-processor --timeout=300s
    fi

    log_success "$service deployment completed"
}

# Deploy gateway
deploy_gateway() {
    log_info "Deploying gateway to $ENVIRONMENT..."

    if [[ "$ENVIRONMENT" == "dev" ]]; then
        # Dev: Local Kubernetes deployment (Kind)
        log_info "Deploying gateway to local Kubernetes..."
        cd "$ROOT_DIR"

        # Build gateway Docker image first (like working scripts)
        log_info "Building gateway Docker image..."
        docker build --no-cache -t order-processor-gateway:latest -f docker/gateway/Dockerfile .

        # Load image into Kind cluster
        log_info "Loading gateway Docker image into Kind cluster..."
        kind load docker-image order-processor-gateway:latest --name order-processor

        # Deploy to Kubernetes using working pattern
        log_info "Deploying gateway to Kubernetes..."
        kubectl apply -k kubernetes/base/
        kubectl apply -k kubernetes/dev/

        # Wait for deployment to be ready
        log_info "Waiting for gateway deployment to be ready..."
        kubectl rollout status deployment/gateway -n order-processor --timeout=300s

        log_success "Gateway deployed to Kubernetes"

    elif [[ "$ENVIRONMENT" == "prod" ]]; then
        # Prod: Kubernetes deployment
        log_info "Deploying gateway to Kubernetes..."
        kubectl apply -k kubernetes/base/
        kubectl apply -k kubernetes/prod/

        # Wait for rollout
        kubectl rollout status deployment/gateway -n order-processor --timeout=300s
    fi

    log_success "Gateway deployment completed"

    if [[ "$ENVIRONMENT" == "dev" ]]; then
        log_info "Gateway accessible at: http://localhost:30002"
    fi
}

# Deploy frontend
deploy_frontend() {
    log_info "Deploying frontend to $ENVIRONMENT..."

    if [[ "$ENVIRONMENT" == "dev" ]]; then
        # Dev: Local Kubernetes deployment (Kind)
        log_info "Deploying frontend to local Kubernetes..."
        cd "$ROOT_DIR"

        # Build frontend Docker image first (like working scripts)
        log_info "Building frontend Docker image..."
        docker build --no-cache -t order-processor-frontend:latest -f docker/frontend/Dockerfile .

        # Load image into Kind cluster
        log_info "Loading frontend image into Kind cluster..."
        kind load docker-image order-processor-frontend:latest --name order-processor

        # Deploy to Kubernetes using working pattern
        log_info "Deploying frontend to Kubernetes..."
        kubectl apply -k kubernetes/base/
        kubectl apply -k kubernetes/dev/

        # Wait for deployment to be ready
        log_info "Waiting for frontend deployment to be ready..."
        kubectl rollout status deployment/frontend -n order-processor --timeout=300s

        log_success "Frontend deployed to Kubernetes"

    elif [[ "$ENVIRONMENT" == "prod" ]]; then
        # Prod: Kubernetes deployment
        log_info "Deploying frontend to Kubernetes..."
        kubectl apply -k kubernetes/base/
        kubectl apply -k kubernetes/prod/

        # Wait for rollout
        kubectl rollout status deployment/frontend -n order-processor --timeout=300s
    fi

    log_success "Frontend deployment completed"

    if [[ "$ENVIRONMENT" == "dev" ]]; then
        log_info "Frontend accessible at: http://localhost:30003"
    fi
}

# Deploy all services
deploy_services() {
    log_info "Deploying all services to $ENVIRONMENT..."

    if [[ "$ENVIRONMENT" == "dev" ]]; then
        # Dev: Build all Docker images first, then deploy to Kubernetes
        log_info "Building all service Docker images..."
        cd "$ROOT_DIR"

        # Build user service
        log_info "Building user service Docker image..."
        docker build --no-cache -t order-processor-user_service:latest -f docker/user-service/Dockerfile .

        # Build inventory service
        log_info "Building inventory service Docker image..."
        docker build --no-cache -t order-processor-inventory_service:latest -f docker/inventory-service/Dockerfile .

        # Build order service
        log_info "Building order service Docker image..."
        docker build --no-cache -t order-processor-order_service:latest -f docker/order-service/Dockerfile .

        # Build auth service
        log_info "Building auth service Docker image..."
        docker build --no-cache -t order-processor-auth_service:latest -f docker/auth-service/Dockerfile .

        # Load images into Kind cluster (required for local Kind deployment)
        log_info "Loading Docker images into Kind cluster..."
        kind load docker-image order-processor-user_service:latest --name order-processor
        kind load docker-image order-processor-inventory_service:latest --name order-processor
        kind load docker-image order-processor-order_service:latest --name order-processor
        kind load docker-image order-processor-auth_service:latest --name order-processor

        # Deploy to Kubernetes
        log_info "Applying Kubernetes manifests for all services..."
        kubectl apply -k kubernetes/base/
        kubectl apply -k kubernetes/dev/

        # Wait for deployments to be ready
        log_info "Waiting for service deployments to be ready..."
        kubectl rollout status deployment/user-service -n order-processor --timeout=300s
        kubectl rollout status deployment/inventory-service -n order-processor --timeout=300s
        kubectl rollout status deployment/order-service -n order-processor --timeout=300s
        kubectl rollout status deployment/auth-service -n order-processor --timeout=300s

        log_success "All services deployed to Kubernetes"

    elif [[ "$ENVIRONMENT" == "prod" ]]; then
        # Prod: Kubernetes deployment
        log_info "Deploying services to Kubernetes..."
        kubectl apply -k kubernetes/base/
        kubectl apply -k kubernetes/prod/

        # Wait for rollouts
        kubectl rollout status deployment/user-service -n order-processor --timeout=300s
        kubectl rollout status deployment/inventory-service -n order-processor --timeout=300s
        kubectl rollout status deployment/order-service -n order-processor --timeout=300s
        kubectl rollout status deployment/auth-service -n order-processor --timeout=300s
    fi

    log_success "All services deployment completed"
}

# Deploy everything in proper order
deploy_all() {
    log_info "Starting full deployment to $ENVIRONMENT environment..."
    log_info "Deployment order: Infrastructure → Monitoring → Services → Gateway → Frontend"

    # 1. Infrastructure
    deploy_infrastructure

    # 2. Monitoring
    deploy_monitoring

    # 3. Services
    deploy_services

    # 4. Gateway
    deploy_gateway

    # 5. Frontend
    deploy_frontend

    log_success "Full deployment to $ENVIRONMENT completed successfully!"

    if [[ "$ENVIRONMENT" == "dev" ]]; then
        show_dev_urls

        # Show cluster status
        log_info ""
        log_info "Cluster Status:"
        kubectl get nodes --no-headers 2>/dev/null | while read -r node status rest; do
            log_info "  $node: $status"
        done

        # Show service status
        log_info ""
        log_info "Service Status:"
        kubectl get services -n order-processor --no-headers 2>/dev/null | while read -r service type cluster_ip external_ip ports age; do
            log_info "  $service: $type $ports"
        done
    elif [[ "$ENVIRONMENT" == "prod" ]]; then
        log_info "Production deployment completed"
        log_info "Check kubernetes/prod/ingress.yaml for external URLs"
    fi
}

# Parse command line arguments
parse_args() {
    COMPONENT=""
    ENVIRONMENT=""


    while [[ $# -gt 0 ]]; do
        case $1 in
            all|frontend|gateway|services|user|inventory|order|auth|monitoring)
                COMPONENT="$1"
                shift
                ;;
            dev|prod)
                ENVIRONMENT="$1"
                shift
                ;;

            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown argument: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "$COMPONENT" ]]; then
        log_error "Component not specified"
        show_usage
        exit 1
    fi

    if [[ -z "$ENVIRONMENT" ]]; then
        log_error "Environment not specified"
        show_usage
        exit 1
    fi
}

# Main function
main() {
    # Parse arguments
    parse_args "$@"

    log_info "Cloud Native Order Processor - Deployment Starting"
    log_info "Component: $COMPONENT"
    log_info "Environment: $ENVIRONMENT"

    # Check prerequisites
    check_prerequisites

    # Load environment configuration
    load_env "$ENVIRONMENT"

    # Execute deployment based on component
    case $COMPONENT in
        all)
            deploy_all
            ;;
        frontend)
            deploy_frontend
            ;;
        gateway)
            deploy_gateway
            ;;
        services)
            deploy_services
            ;;
        user)
            log_info "Deploying user service to $ENVIRONMENT..."
            if [[ "$ENVIRONMENT" == "dev" ]]; then
                cd "$ROOT_DIR"
                docker build --no-cache -t order-processor-user_service:latest -f docker/user-service/Dockerfile .
                kind load docker-image order-processor-user_service:latest --name order-processor
                kubectl apply -k kubernetes/base/
                kubectl apply -k kubernetes/dev/
                kubectl rollout status deployment/user-service -n order-processor --timeout=300s
                log_info "User service accessible at: http://localhost:30004"
            fi
            ;;
        inventory)
            log_info "Deploying inventory service to $ENVIRONMENT..."
            if [[ "$ENVIRONMENT" == "dev" ]]; then
                cd "$ROOT_DIR"
                docker build --no-cache -t order-processor-inventory_service:latest -f docker/inventory-service/Dockerfile .
                kind load docker-image order-processor-inventory_service:latest --name order-processor
                kubectl apply -k kubernetes/base/
                kubectl apply -k kubernetes/dev/
                kubectl rollout status deployment/inventory-service -n order-processor --timeout=300s
                log_info "Inventory service accessible at: http://localhost:30005"
            fi
            ;;
        order)
            log_info "Deploying order service to $ENVIRONMENT..."
            if [[ "$ENVIRONMENT" == "dev" ]]; then
                cd "$ROOT_DIR"
                docker build --no-cache -t order-processor-order_service:latest -f docker/order-service/Dockerfile .
                kind load docker-image order-processor-order_service:latest --name order-processor
                kubectl apply -k kubernetes/base/
                kubectl apply -k kubernetes/dev/
                kubectl rollout status deployment/order-service -n order-processor --timeout=300s
                log_info "Order service accessible at: http://localhost:30006"
            fi
            ;;
        auth)
            log_info "Deploying auth service to $ENVIRONMENT..."
            if [[ "$ENVIRONMENT" == "dev" ]]; then
                cd "$ROOT_DIR"
                docker build --no-cache -t order-processor-auth_service:latest -f docker/auth-service/Dockerfile .
                kind load docker-image order-processor-auth_service:latest --name order-processor
                kubectl apply -k kubernetes/base/
                kubectl apply -k kubernetes/dev/
                kubectl rollout status deployment/auth-service -n order-processor --timeout=300s
                log_info "Auth service accessible at: http://localhost:30007"
            fi
            ;;
        monitoring)
            deploy_monitoring
            ;;
        *)
            log_error "Unknown component: $COMPONENT"
            show_usage
            exit 1
            ;;
    esac
}

# Script execution
main "$@"
