#!/bin/bash

# Cleanup Order Processor deployments
# Usage: ./cleanup.sh [dev|prod]

set -e

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

CLEANUP_ENV=${1:-"dev"}

if [[ "$CLEANUP_ENV" != "dev" && "$CLEANUP_ENV" != "prod" ]]; then
    echo "❌ Invalid environment: $CLEANUP_ENV"
    echo "Usage: $0 [dev|prod]"
    exit 1
fi

echo "🧹 Cleaning up Order Processor deployment for environment: $CLEANUP_ENV..."

if [[ "$CLEANUP_ENV" == "dev" ]]; then
    if kubectl get namespace order-processor >/dev/null 2>&1; then
        kubectl delete -k "$K8S_DIR/dev" --ignore-not-found=true
        echo "✅ Dev deployment cleaned up"
    else
        echo "ℹ️  No dev deployment found"
    fi
    # Also delete Kind cluster if it exists
    if kind get clusters | grep -q "order-processor"; then
        echo "🗑️  Deleting Kind cluster 'order-processor'..."
        kind delete cluster --name order-processor
        echo "✅ Kind cluster deleted"
    else
        echo "ℹ️  No Kind cluster found"
    fi
elif [[ "$CLEANUP_ENV" == "prod" ]]; then
    if kubectl get namespace order-processor >/dev/null 2>&1; then
        kubectl delete -k "$K8S_DIR/dev" --ignore-not-found=true
        kubectl delete -k "$K8S_DIR/prod" --ignore-not-found=true
        kubectl delete -k "$K8S_DIR/base" --ignore-not-found=true
        echo "✅ All deployments cleaned up"
    else
        echo "ℹ️  No deployments found"
    fi
fi

echo ""
echo "🧹 Cleanup complete!"