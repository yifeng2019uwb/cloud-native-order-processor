#!/bin/bash

# Setup AWS credentials for Kubernetes deployment
# This script fetches access keys for the IAM user from Terraform outputs and updates Kubernetes secrets
# NOTE: For security, rotate these credentials regularly. To rotate, use AWS Console or a rotation script.

set -e

echo "🔐 Setting up AWS credentials for Kubernetes (no rotation, just fetch from Terraform)..."

# Get the IAM user name and keys from Terraform output
cd ../../terraform
IAM_USER_NAME=$(terraform output -raw application_user_name 2>/dev/null || echo "order-processor-dev-application-user")
ACCESS_KEY_ID=$(terraform output -raw application_user_access_key_id 2>/dev/null || echo "")
SECRET_ACCESS_KEY=$(terraform output -raw application_user_access_key_secret 2>/dev/null || echo "")
cd ../kubernetes

# Check if we're in EKS mode (enable_kubernetes=true)
if [ -z "$ACCESS_KEY_ID" ] || [ "$ACCESS_KEY_ID" = "null" ]; then
    echo "❌ Access key not available from Terraform outputs."
    echo "   This might be because:"
    echo "   1. Terraform is configured for EKS (enable_kubernetes=true)"
    echo "   2. Terraform outputs are not available"
    echo "   3. Terraform needs to be applied"
    echo ""
    echo "💡 For EKS: Use IRSA (IAM Roles for Service Accounts) instead of access keys"
    echo "💡 For local K8s: Set enable_kubernetes=false in Terraform and re-apply"
    exit 1
fi

if [ -z "$SECRET_ACCESS_KEY" ] || [ "$SECRET_ACCESS_KEY" = "null" ]; then
    echo "❌ Access key secret not available from Terraform outputs."
    echo "   This might be because:"
    echo "   1. Terraform is configured for EKS (enable_kubernetes=true)"
    echo "   2. Terraform outputs are not available"
    echo "   3. Terraform needs to be applied"
    echo ""
    echo "💡 For EKS: Use IRSA (IAM Roles for Service Accounts) instead of access keys"
    echo "💡 For local K8s: Set enable_kubernetes=false in Terraform and re-apply"
    exit 1
fi

echo "📋 IAM User: $IAM_USER_NAME"
echo "🔑 Access Key ID: $ACCESS_KEY_ID"
echo "🔐 Secret Access Key: [HIDDEN]"

# Base64 encode the credentials
ACCESS_KEY_B64=$(echo -n "$ACCESS_KEY_ID" | base64)
SECRET_KEY_B64=$(echo -n "$SECRET_ACCESS_KEY" | base64)

# Update the secrets file
# Add a comment about rotation
sed -i.bak "/aws-access-key-id:/i \\n  # NOTE: For security, rotate these credentials regularly. To rotate, use AWS Console or a rotation script." local/secrets.yaml
sed -i.bak "s/aws-access-key-id: .*/aws-access-key-id: $ACCESS_KEY_B64/" local/secrets.yaml
sed -i.bak "s/aws-secret-access-key: .*/aws-secret-access-key: $SECRET_KEY_B64/" local/secrets.yaml

# Clean up backup file
rm -f local/secrets.yaml.bak

echo "✅ Kubernetes secrets updated successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Deploy to Kubernetes: ./kubernetes/scripts/deploy-local.sh"
echo "   2. The services will now use these credentials to assume the IAM role"
echo ""
echo "⚠️  Important: Keep these credentials secure and rotate them regularly!"