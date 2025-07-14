#!/bin/bash

# Cleanup Order Processor deployments
# Usage: ./cleanup.sh [local|prod|all]

set -e

CLEANUP_TARGET=${1:-"all"}

echo "🧹 Cleaning up Order Processor deployments..."

case $CLEANUP_TARGET in
    "local")
        echo "🗑️  Cleaning up local deployment..."
        if kubectl get namespace order-processor >/dev/null 2>&1; then
            kubectl delete -k local --ignore-not-found=true
            echo "✅ Local deployment cleaned up"
        else
            echo "ℹ️  No local deployment found"
        fi
        ;;
    "prod")
        echo "🗑️  Cleaning up production deployment..."
        if kubectl get namespace order-processor >/dev/null 2>&1; then
            kubectl delete -k prod --ignore-not-found=true
            echo "✅ Production deployment cleaned up"
        else
            echo "ℹ️  No production deployment found"
        fi
        ;;
    "all")
        echo "🗑️  Cleaning up all deployments..."
        if kubectl get namespace order-processor >/dev/null 2>&1; then
            kubectl delete -k local --ignore-not-found=true
            kubectl delete -k prod --ignore-not-found=true
            kubectl delete -k base --ignore-not-found=true
            echo "✅ All deployments cleaned up"
        else
            echo "ℹ️  No deployments found"
        fi

        # Also delete Kind cluster if it exists
        if kind get clusters | grep -q "order-processor"; then
            echo "🗑️  Deleting Kind cluster 'order-processor'..."
            kind delete cluster --name order-processor
            echo "✅ Kind cluster deleted"
        else
            echo "ℹ️  No Kind cluster found"
        fi
        ;;
    *)
        echo "❌ Invalid target: $CLEANUP_TARGET"
        echo "Usage: $0 [local|prod|all]"
        exit 1
        ;;
esac

echo ""
echo "🧹 Cleanup complete!"