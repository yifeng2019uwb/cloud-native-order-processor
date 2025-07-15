#!/bin/bash

# Cleanup Order Processor deployments
# Usage: ./cleanup.sh [dev|prod]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV=${1:-"dev"}

# Validate environment
if [[ "$ENV" != "dev" && "$ENV" != "prod" ]]; then
    echo "❌ Usage: $0 [dev|prod]"
    exit 1
fi

echo "🧹 Cleaning up Order Processor ($ENV)..."

# Check if namespace exists
if ! kubectl get namespace order-processor >/dev/null 2>&1; then
    echo "ℹ️  No deployment found"
    exit 0
fi

# Cleanup based on environment
if [[ "$ENV" == "dev" ]]; then
    kubectl delete -k "$K8S_DIR/dev" --ignore-not-found=true

    # Delete Kind cluster if exists
    if kind get clusters 2>/dev/null | grep -q "order-processor"; then
        echo "🗑️  Deleting Kind cluster..."
        kind delete cluster --name order-processor
    fi
else
    # Prod cleanup - remove all overlays
    kubectl delete -k "$K8S_DIR/prod" --ignore-not-found=true
    kubectl delete -k "$K8S_DIR/dev" --ignore-not-found=true
    kubectl delete -k "$K8S_DIR/base" --ignore-not-found=true
fi

echo "✅ Cleanup complete!"