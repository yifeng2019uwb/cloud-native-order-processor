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
    command -v jq     >/dev/null 2>&1 || error "jq not found — install with: brew install jq"
    success "Prerequisites OK"
}

# ── per-cluster loop ──────────────────────────────────────────────────────────
# Calls fn "$region" for every cluster in the Pulumi stack output.
for_each_cluster() {
    local fn=$1
    local regions
    regions=$(cd "$SCRIPT_DIR" && pulumi stack output clusterRegions --json 2>/dev/null | jq -r '.[]') \
        || error "Cannot read clusterRegions — run 'pulumi up' first"

    for region in $regions; do
        local cluster zone
        cluster=$(cd "$SCRIPT_DIR" && pulumi stack output "clusterName-${region}" 2>/dev/null)
        zone=$(cd "$SCRIPT_DIR" && pulumi stack output "clusterZone-${region}" 2>/dev/null)
        info "=== Cluster: $cluster ($region) ==="
        gcloud container clusters get-credentials "$cluster" \
            --zone "$zone" --project "$PROJECT_ID" --quiet
        $fn "$region"
    done
}

deploy_full() {
    local region=$1
    deploy_infra
    deploy_deps
    deploy_app
    show_status
    _apply_daemonset "$region"
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

# ── daemonset ────────────────────────────────────────────────────────────────
_apply_daemonset() {
    local region=$1
    local image="us-west1-docker.pkg.dev/ebpfagent/ebpf-edr/ebpf-edr:latest"
    local ds_yaml="$K8S_DIR/ebpf-edr-ds.yaml"

    if [ ! -f "$ds_yaml" ]; then
        warn "ebpf-edr-ds.yaml not found — skipping ($ds_yaml)"
        return 0
    fi

    if ! gcloud artifacts docker images describe "$image" >/dev/null 2>&1; then
        warn "eBPF EDR image not found in Artifact Registry — skipping DaemonSet deploy"
        warn "Build and push from ebpf-edr-demo/: make docker-push"
        return 0
    fi

    REGION=$region envsubst < "$ds_yaml" | kubectl apply -f -
    success "eBPF EDR DaemonSet deployed (region=$region)"
}

# ── main ──────────────────────────────────────────────────────────────────────
main() {
    local cmd="${1:-all}"

    check_prereqs

    case "$cmd" in
        all)
            for_each_cluster deploy_full
            ;;
        build)
            build_images
            ;;
        daemonset)
            for_each_cluster _apply_daemonset
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
            echo "Usage: $0 [all|build|daemonset|infra|app|status]"
            echo "  all       — deploy services to every cluster in Pulumi stack"
            echo "  build     — build and push Docker images to Artifact Registry"
            echo "  daemonset — deploy eBPF EDR DaemonSet to every cluster (skips if image not found)"
            echo "  infra     — namespace, secret, configmap (current kubectl context)"
            echo "  app       — localstack, redis, services, deployments (current context)"
            echo "  status    — show pods, services, gateway IP (current context)"
            exit 1
            ;;
    esac
}

main "$@"
