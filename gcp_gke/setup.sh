#!/bin/bash
# gcp_gke/setup.sh — One-time setup before running pulumi up or deploy.sh
# Run this once per machine / new GCP project

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ID="ebpfagent"
SERVICE_ACCOUNT_ID="order-processor-sa"
PULUMI_STACK="gke-dev"

info()    { echo "[INFO]  $*"; }
success() { echo "[OK]    $*"; }
warn()    { echo "[WARN]  $*"; }
error()   { echo "[ERROR] $*"; exit 1; }

# ── prereqs ───────────────────────────────────────────────────────────────────
check_tools() {
    info "Checking required tools..."
    command -v gcloud  >/dev/null 2>&1 || error "gcloud not found — install Google Cloud SDK"
    command -v pulumi  >/dev/null 2>&1 || error "pulumi not found — install from https://www.pulumi.com/docs/install/"
    command -v kubectl >/dev/null 2>&1 || error "kubectl not found — install from https://kubernetes.io/docs/tasks/tools/"
    command -v docker  >/dev/null 2>&1 || error "docker not found"
    command -v go      >/dev/null 2>&1 || error "go not found"
    success "All tools found"
}

# ── gcp auth ──────────────────────────────────────────────────────────────────
setup_gcp() {
    info "Setting GCP project to $PROJECT_ID..."
    gcloud config set project "$PROJECT_ID"

    info "Fixing Application Default Credentials quota project..."
    gcloud auth application-default set-quota-project "$PROJECT_ID"

    info "Enabling required GCP APIs (may take a minute)..."
    gcloud services enable container.googleapis.com
    gcloud services enable iam.googleapis.com
    gcloud services enable artifactregistry.googleapis.com

    info "Configuring Docker for Artifact Registry..."
    gcloud auth configure-docker us-west1-docker.pkg.dev --quiet

    success "GCP setup complete"
}

# ── pulumi ────────────────────────────────────────────────────────────────────
setup_pulumi() {
    info "Resolving Go dependencies..."
    go mod tidy

    info "Checking Pulumi login..."
    if ! pulumi whoami >/dev/null 2>&1; then
        warn "Not logged in to Pulumi — logging in locally (no account needed)"
        pulumi login --local
    else
        success "Already logged in: $(pulumi whoami)"
    fi

    info "Initialising Pulumi stack '$PULUMI_STACK'..."
    if pulumi stack ls 2>/dev/null | grep -q "$PULUMI_STACK"; then
        warn "Stack '$PULUMI_STACK' already exists, selecting it"
        pulumi stack select "$PULUMI_STACK"
    else
        pulumi stack init "$PULUMI_STACK"
    fi

    info "Setting Pulumi GCP project config..."
    pulumi config set gcp:project "$PROJECT_ID"

    success "Pulumi setup complete"
}

# ── kubectl ───────────────────────────────────────────────────────────────────
connect_kubectl() {
    info "Reading cluster list from Pulumi stack outputs..."
    local regions
    regions=$(cd "$SCRIPT_DIR" && pulumi stack output clusterRegions --json 2>/dev/null | jq -r '.[]') \
        || error "Cannot read clusterRegions — run 'pulumi up' first"

    for region in $regions; do
        local cluster zone
        cluster=$(cd "$SCRIPT_DIR" && pulumi stack output "clusterName-${region}" 2>/dev/null)
        zone=$(cd "$SCRIPT_DIR" && pulumi stack output "clusterZone-${region}" 2>/dev/null)
        info "Connecting kubectl to $cluster ($zone)..."
        gcloud container clusters get-credentials "$cluster" \
            --zone "$zone" --project "$PROJECT_ID"
        success "Connected: $cluster"
    done
}

# ── main ──────────────────────────────────────────────────────────────────────
main() {
    local cmd="${1:-all}"

    case "$cmd" in
        all)
            check_tools
            setup_gcp
            setup_pulumi
            connect_kubectl
            echo ""
            success "Setup complete. Next steps:"
            echo "  1. pulumi up          — create GKE cluster"
            echo "  2. ./setup.sh kubectl — connect kubectl (if not done above)"
            echo "  3. ./deploy.sh all    — deploy services to cluster"
            ;;
        gcp)
            setup_gcp
            ;;
        pulumi)
            setup_pulumi
            ;;
        kubectl)
            connect_kubectl
            ;;
        tools)
            check_tools
            ;;
        *)
            echo "Usage: $0 [all|gcp|pulumi|kubectl|tools]"
            echo "  all     — full one-time setup (default)"
            echo "  gcp     — gcloud auth + enable APIs"
            echo "  pulumi  — go mod tidy + login + stack init + config"
            echo "  kubectl — connect kubectl to existing cluster"
            echo "  tools   — check required tools only"
            exit 1
            ;;
    esac
}

main "$@"
