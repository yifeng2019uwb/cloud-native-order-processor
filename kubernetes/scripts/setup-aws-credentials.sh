#!/bin/bash

# Setup AWS credentials for Kubernetes deployment
# This script fetches access keys for the IAM user from Terraform outputs and creates/updates Kubernetes secrets directly.
# NOTE: For security, rotate these credentials regularly. No secrets.yaml file is used or required.

set -e

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "🔐 Setting up AWS credentials for Kubernetes (no rotation, just fetch from Terraform)..."

# Get the IAM user name and keys from Terraform output
cd "$PROJECT_ROOT/terraform"
IAM_USER_NAME=$(terraform output -raw application_user_name 2>/dev/null || echo "order-processor-dev-application-user")
ACCESS_KEY_ID=$(terraform output -raw application_user_access_key_id 2>/dev/null || echo "")
SECRET_ACCESS_KEY=$(terraform output -raw application_user_access_key_secret 2>/dev/null || echo "")
cd "$PROJECT_ROOT"

if [ -z "$ACCESS_KEY_ID" ] || [ "$ACCESS_KEY_ID" = "null" ]; then
    echo "❌ Access key not available from Terraform outputs."
    exit 1
fi

if [ -z "$SECRET_ACCESS_KEY" ] || [ "$SECRET_ACCESS_KEY" = "null" ]; then
    echo "❌ Access key secret not available from Terraform outputs."
    exit 1
fi

echo "📋 IAM User: $IAM_USER_NAME"
echo "🔑 Access Key ID: $ACCESS_KEY_ID"
echo "🔐 Secret Access Key: [HIDDEN]"

# Create or update the Kubernetes secret directly
kubectl get namespace order-processor >/dev/null 2>&1 || kubectl create namespace order-processor
kubectl delete secret aws-credentials -n order-processor 2>/dev/null || true
kubectl create secret generic aws-credentials \
  --from-literal=aws-access-key-id="$ACCESS_KEY_ID" \
  --from-literal=aws-secret-access-key="$SECRET_ACCESS_KEY" \
  -n order-processor

echo "✅ Kubernetes secret 'aws-credentials' created/updated successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Deploy to Kubernetes: ./kubernetes/deploy.sh --environment dev"
echo "   2. The services will now use these credentials to assume the IAM role"
echo ""
echo "⚠️  Important: Keep these credentials secure and rotate them regularly!"