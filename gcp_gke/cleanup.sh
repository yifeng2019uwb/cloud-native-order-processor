#!/bin/bash
# gcp_gke/cleanup.sh — Remove order-processor from GKE
# Usage: ./cleanup.sh

set -e

NAMESPACE="order-processor"

echo "[INFO]  Deleting namespace $NAMESPACE and all resources inside it..."
kubectl delete namespace "$NAMESPACE" --ignore-not-found=true

echo "[OK]    Cleanup complete"
