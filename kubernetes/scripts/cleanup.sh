#!/bin/bash

# scripts/cleanup.sh - Clean up deployment

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KUBERNETES_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
NAMESPACE=${NAMESPACE:-order-processor}
CHART_NAME=${CHART_NAME:-order-processor}
FORCE=${FORCE:-false}

echo "🧹 Cleaning up Order Processing System..."
echo "📁 Working directory: $KUBERNETES_DIR"
echo "📦 Namespace: $NAMESPACE"

# Confirmation prompt unless forced
if [ "$FORCE" != "true" ]; then
    echo "⚠️  This will delete all resources in namespace '$NAMESPACE'"
    echo "   Are you sure you want to continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "❌ Cleanup cancelled"
        exit 0
    fi
fi

# Remove Helm release
echo "🎯 Removing Helm release '$CHART_NAME'..."
if helm list -n "$NAMESPACE" | grep -q "$CHART_NAME"; then
    helm uninstall "$CHART_NAME" -n "$NAMESPACE"
    echo "✅ Helm release removed"
else
    echo "ℹ️  No Helm release found"
fi

# Wait for pods to terminate
echo "⏳ Waiting for pods to terminate..."
kubectl wait --for=delete pods --all -n "$NAMESPACE" --timeout=60s || true

# Remove namespace
echo "📦 Removing namespace '$NAMESPACE'..."
if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
    kubectl delete namespace "$NAMESPACE"
    echo "✅ Namespace removed"
else
    echo "ℹ️  Namespace does not exist"
fi

# Clean up any stuck resources
echo "🔍 Checking for stuck resources..."
kubectl get all --all-namespaces | grep order-processor || echo "✅ No stuck resources found"

echo "🎉 Cleanup completed successfully!"
echo ""
echo "🛠️  To redeploy, run:"
echo "   make deploy"
echo "   # or"
echo "   ./scripts/deploy.sh"