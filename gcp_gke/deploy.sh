#!/bin/bash
# gcp_gke/deploy.sh — Deploy order-processor to GKE
# Usage: ./deploy.sh [all|build|infra|app|status]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
K8S_DIR="$SCRIPT_DIR/kubernetes"
NAMESPACE="order-processor"
JWT_SECRET="test_jwt_gcp_secret_key_for_gke_demo"
PROJECT_ID="ebpfagent"
AR_REGION="us-west1"
AR_REPO="order-processor"
IMAGE_PREFIX="${AR_REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}"
SERVICES="user-service inventory-service order-service auth-service gateway"

# ── logging ──────────────────────────────────────────────────────────────────
info()    { echo "[INFO]  $*"; }
success() { echo "[OK]    $*"; }
warn()    { echo "[WARN]  $*"; }
error()   { echo "[ERROR] $*"; exit 1; }

# ── build + push images ───────────────────────────────────────────────────────
build_images() {
    info "Configuring Docker for Artifact Registry..."
    gcloud auth configure-docker "${AR_REGION}-docker.pkg.dev" --quiet

    for svc in $SERVICES; do
        info "Building and pushing $svc (linux/amd64)..."
        # Use gcp_gke-local override Dockerfile if present (e.g. gateway cross-compilation fix)
        if [ -f "$SCRIPT_DIR/docker/$svc/Dockerfile" ]; then
            DOCKERFILE="$SCRIPT_DIR/docker/$svc/Dockerfile"
        else
            DOCKERFILE="$REPO_ROOT/docker/$svc/Dockerfile"
        fi
        docker buildx build --platform linux/amd64 --no-cache --push \
            -t "${IMAGE_PREFIX}/${svc}:latest" \
            -f "$DOCKERFILE" "$REPO_ROOT"
        success "$svc pushed"
    done
}

# ── prereqs ───────────────────────────────────────────────────────────────────
check_prereqs() {
    info "Checking prerequisites..."
    command -v kubectl >/dev/null 2>&1 || error "kubectl not found"
    kubectl cluster-info >/dev/null 2>&1   || error "No cluster connection — run: gcloud container clusters get-credentials <cluster> --zone <zone>"
    success "Prerequisites OK"
}

# ── namespace + secret ────────────────────────────────────────────────────────
deploy_infra() {
    info "Creating namespace and service account..."
    kubectl apply -f "$K8S_DIR/namespace.yaml"

    info "Creating app-secrets (jwt-secret)..."
    if kubectl get secret app-secrets -n "$NAMESPACE" >/dev/null 2>&1; then
        warn "app-secrets already exists, skipping"
    else
        kubectl create secret generic app-secrets \
            --from-literal=jwt-secret="$JWT_SECRET" \
            -n "$NAMESPACE"
        success "app-secrets created"
    fi

    info "Applying ConfigMap..."
    kubectl apply -f "$K8S_DIR/configmap.yaml"

    success "Infra ready"
}

# ── dependencies: localstack + redis ──────────────────────────────────────────
deploy_deps() {
    info "Deploying LocalStack..."
    kubectl apply -f "$K8S_DIR/localstack.yaml"

    info "Deploying Redis..."
    kubectl apply -f "$K8S_DIR/redis.yaml"

    info "Waiting for LocalStack to be ready..."
    kubectl rollout status deployment/localstack -n "$NAMESPACE" --timeout=120s
    success "LocalStack ready"

    info "Waiting for Redis to be ready..."
    kubectl rollout status deployment/redis -n "$NAMESPACE" --timeout=120s
    success "Redis ready"
}

# ── services + deployments ────────────────────────────────────────────────────
deploy_app() {
    info "Applying Services..."
    kubectl apply -f "$K8S_DIR/service.yaml"

    info "Applying Deployments..."
    kubectl apply -f "$K8S_DIR/deployment.yaml"

    info "Applying HPA..."
    kubectl apply -f "$K8S_DIR/hpa.yaml"

    info "Waiting for deployments to be ready..."
    for svc in auth-service user-service inventory-service order-service gateway; do
        info "  waiting: $svc"
        kubectl rollout status deployment/"$svc" -n "$NAMESPACE" --timeout=300s
        success "  $svc ready"
    done
}

# ── status ────────────────────────────────────────────────────────────────────
show_status() {
    echo ""
    info "=== Pods ==="
    kubectl get pods -n "$NAMESPACE"

    echo ""
    info "=== Services ==="
    kubectl get services -n "$NAMESPACE"

    echo ""
    GATEWAY_IP=$(kubectl get svc gateway -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)
    if [[ -n "$GATEWAY_IP" ]]; then
        success "Gateway: http://$GATEWAY_IP:8080"
    else
        warn "Gateway external IP pending — run: kubectl get svc gateway -n $NAMESPACE"
    fi
}

# ── main ──────────────────────────────────────────────────────────────────────
main() {
    local cmd="${1:-all}"

    check_prereqs

    case "$cmd" in
        all)
            deploy_infra
            deploy_deps
            deploy_app
            show_status
            ;;
        build)
            build_images
            ;;
        infra)
            deploy_infra
            ;;
        app)
            deploy_deps
            deploy_app
            show_status
            ;;
        status)
            show_status
            ;;
        *)
            echo "Usage: $0 [all|build|infra|app|status]"
            echo "  all    — full deploy (default)"
            echo "  build  — build and push Docker images to Artifact Registry"
            echo "  infra  — namespace, secret, configmap only"
            echo "  app    — localstack, redis, services, deployments"
            echo "  status — show pods, services, gateway IP"
            exit 1
            ;;
    esac
}

main "$@"
