#!/bin/bash

# Script to update AWS credentials in Kubernetes secrets
# Usage: ./update-aws-credentials.sh [ACCESS_KEY] [SECRET_KEY]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "kubernetes/local/secrets.yaml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Function to get AWS credentials
get_aws_credentials() {
    local access_key=""
    local secret_key=""

    # Check if credentials were passed as arguments
    if [ $# -eq 2 ]; then
        access_key="$1"
        secret_key="$2"
        print_info "Using provided AWS credentials"
    else
        # Try to get from AWS CLI
        if command -v aws &> /dev/null; then
            print_info "Attempting to get AWS credentials from AWS CLI..."

            # Check if AWS CLI is configured
            if aws sts get-caller-identity &> /dev/null; then
                print_success "AWS CLI is configured"

                # Get credentials from AWS CLI
                local credentials=$(aws configure get aws_access_key_id 2>/dev/null)
                if [ -n "$credentials" ]; then
                    access_key="$credentials"
                    secret_key=$(aws configure get aws_secret_access_key 2>/dev/null)
                    print_info "Retrieved credentials from AWS CLI"
                fi
            else
                print_warning "AWS CLI is not configured or credentials are invalid"
            fi
        fi

        # If still no credentials, prompt user
        if [ -z "$access_key" ] || [ -z "$secret_key" ]; then
            print_info "Please enter your AWS credentials:"
            read -p "AWS Access Key ID: " access_key
            read -s -p "AWS Secret Access Key: " secret_key
            echo
        fi
    fi

    # Validate credentials
    if [ -z "$access_key" ] || [ -z "$secret_key" ]; then
        print_error "AWS credentials are required"
        exit 1
    fi

    echo "$access_key:$secret_key"
}

# Function to update Kubernetes secrets
update_k8s_secrets() {
    local access_key="$1"
    local secret_key="$2"

    print_info "Updating Kubernetes secrets..."

    # Base64 encode the credentials
    local encoded_access_key=$(echo -n "$access_key" | base64)
    local encoded_secret_key=$(echo -n "$secret_key" | base64)

    # Create a temporary file with updated secrets
    cat > kubernetes/local/secrets-updated.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: aws-credentials
  namespace: order-processor
  labels:
    app: order-processor
    component: secrets
    environment: local
type: Opaque
data:
  access-key-id: $encoded_access_key
  secret-access-key: $encoded_secret_key
---
apiVersion: v1
kind: Secret
metadata:
  name: jwt-secret
  namespace: order-processor
  labels:
    app: order-processor
    component: secrets
    environment: local
type: Opaque
data:
  jwt-secret: bG9jYWwtZGV2LXNlY3JldC1rZXk=
EOF

    # Backup original secrets
    cp kubernetes/local/secrets.yaml kubernetes/local/secrets.yaml.backup

    # Replace with updated secrets
    mv kubernetes/local/secrets-updated.yaml kubernetes/local/secrets.yaml

    print_success "Updated kubernetes/local/secrets.yaml"
    print_info "Original file backed up as kubernetes/local/secrets.yaml.backup"
}

# Function to apply secrets to cluster
apply_secrets() {
    print_info "Applying secrets to Kubernetes cluster..."

    # Check if namespace exists
    if ! kubectl get namespace order-processor &> /dev/null; then
        print_info "Creating order-processor namespace..."
        kubectl apply -f kubernetes/base/namespace.yaml
    fi

    # Apply the secrets
    kubectl apply -f kubernetes/local/secrets.yaml

    print_success "Secrets applied to Kubernetes cluster"
}

# Function to verify secrets
verify_secrets() {
    print_info "Verifying secrets in Kubernetes cluster..."

    # Check if secrets exist
    if kubectl get secret aws-credentials -n order-processor &> /dev/null; then
        print_success "AWS credentials secret exists"

        # Decode and show the access key (first 10 characters)
        local stored_access_key=$(kubectl get secret aws-credentials -n order-processor -o jsonpath='{.data.access-key-id}' | base64 -d)
        local masked_key=$(echo "$stored_access_key" | cut -c1-10)
        print_info "Access Key ID: ${masked_key}..."
    else
        print_error "AWS credentials secret not found"
        return 1
    fi

    if kubectl get secret jwt-secret -n order-processor &> /dev/null; then
        print_success "JWT secret exists"
    else
        print_error "JWT secret not found"
        return 1
    fi
}

# Function to restart pods to pick up new credentials
restart_pods() {
    print_info "Restarting pods to pick up new credentials..."

    # Get current pods
    local pods=$(kubectl get pods -n order-processor -o jsonpath='{.items[*].metadata.name}')

    for pod in $pods; do
        print_info "Restarting pod: $pod"
        kubectl delete pod "$pod" -n order-processor
    done

    print_success "Pods restarted"
    print_info "Waiting for pods to be ready..."

    # Wait for pods to be ready
    kubectl wait --for=condition=ready pod -l app=order-processor -n order-processor --timeout=300s

    print_success "All pods are ready"
}

# Main execution
main() {
    print_info "🔐 AWS Credentials Update Script"
    print_info "=================================="

    # Get credentials
    local credentials=$(get_aws_credentials "$@")
    local access_key=$(echo "$credentials" | cut -d: -f1)
    local secret_key=$(echo "$credentials" | cut -d: -f2)

    # Update secrets file
    update_k8s_secrets "$access_key" "$secret_key"

    # Apply to cluster
    apply_secrets

    # Verify
    if verify_secrets; then
        print_success "✅ AWS credentials updated successfully!"

        # Ask if user wants to restart pods
        read -p "Do you want to restart pods to pick up new credentials? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            restart_pods
        else
            print_info "Pods will pick up new credentials on next restart"
        fi

        print_info "🎉 Setup complete! Your logs will now be sent to S3 and CloudWatch"
    else
        print_error "❌ Failed to verify secrets"
        exit 1
    fi
}

# Run main function
main "$@"