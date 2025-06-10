#!/bin/bash

# Generate Kubernetes ConfigMap from Terraform outputs
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info "🔧 Generating Kubernetes ConfigMap from Terraform outputs..."

# Check if terraform directory exists
if [ ! -d "terraform" ]; then
    print_error "Terraform directory not found. Please run from project root."
    exit 1
fi

cd terraform

# Get Terraform outputs in JSON format
print_info "📋 Reading Terraform outputs..."
TERRAFORM_OUTPUT=$(terraform output -json)

if [ $? -ne 0 ]; then
    print_error "Failed to read Terraform outputs. Make sure Terraform is applied."
    exit 1
fi

# Extract specific values using your actual output names
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="us-west-2"

# Get values from your existing Terraform outputs
EKS_CLUSTER_NAME=$(echo $TERRAFORM_OUTPUT | jq -r '.eks_cluster_name.value // ""')
EKS_CLUSTER_ENDPOINT=$(echo $TERRAFORM_OUTPUT | jq -r '.eks_cluster_endpoint.value // ""')
DATABASE_ENDPOINT=$(echo $TERRAFORM_OUTPUT | jq -r '.database_endpoint.value // ""')
DATABASE_SECRET_ARN=$(echo $TERRAFORM_OUTPUT | jq -r '.database_secret_arn.value // ""')
DATABASE_SECRET_NAME=$(echo $TERRAFORM_OUTPUT | jq -r '.database_secret_name.value // ""')
S3_EVENTS_BUCKET=$(echo $TERRAFORM_OUTPUT | jq -r '.s3_events_bucket_name.value // ""')
SNS_ORDER_EVENTS=$(echo $TERRAFORM_OUTPUT | jq -r '.sns_order_events_topic_arn.value // ""')
SQS_ORDER_PROCESSING=$(echo $TERRAFORM_OUTPUT | jq -r '.sqs_order_processing_queue_url.value // ""')
ECR_REPOSITORY_URL=$(echo $TERRAFORM_OUTPUT | jq -r '.ecr_order_api_repository_url.value // ""')
ORDER_SERVICE_ROLE_ARN=$(echo $TERRAFORM_OUTPUT | jq -r '.order_service_role_arn.value // ""')

# Go back to project root
cd ..

print_info "🏗️ Generating ConfigMap YAML..."

# Generate the ConfigMap with dynamic values
cat > kubernetes/secrets-config-generated.yaml << EOF
---
# AWS Secrets Store CSI Driver SecretProviderClass
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: order-processor-secrets
  namespace: order-processor
spec:
  provider: aws
  parameters:
    objects: |
      - objectName: "${DATABASE_SECRET_NAME}"
        objectType: "secretsmanager"
        jmesPath:
          - path: "username"
            objectAlias: "db-username"
          - path: "password"
            objectAlias: "db-password"
          - path: "host"
            objectAlias: "db-host"
          - path: "port"
            objectAlias: "db-port"
          - path: "dbname"
            objectAlias: "db-name"
  secretObjects:
  - secretName: db-credentials
    type: Opaque
    data:
    - objectName: "db-username"
      key: "username"
    - objectName: "db-password"
      key: "password"
    - objectName: "db-host"
      key: "host"
    - objectName: "db-port"
      key: "port"
    - objectName: "db-name"
      key: "dbname"

---
# ConfigMap for application configuration (Generated from YOUR Terraform outputs)
apiVersion: v1
kind: ConfigMap
metadata:
  name: order-service-config
  namespace: order-processor
  annotations:
    generated-from: terraform-outputs
    generated-at: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
data:
  # Application settings
  APP_NAME: "order-processor-api"
  APP_ENV: "development"
  DEBUG: "true"
  LOG_LEVEL: "INFO"

  # AWS Configuration
  AWS_REGION: "${AWS_REGION}"
  AWS_DEFAULT_REGION: "${AWS_REGION}"
  AWS_ACCOUNT_ID: "${AWS_ACCOUNT_ID}"

  # EKS Cluster info
  EKS_CLUSTER_NAME: "${EKS_CLUSTER_NAME}"
  EKS_CLUSTER_ENDPOINT: "${EKS_CLUSTER_ENDPOINT}"

  # SNS Topics (from your Terraform outputs)
  SNS_TOPIC_ORDER_EVENTS: "${SNS_ORDER_EVENTS}"

  # SQS Queues (from your Terraform outputs)
  SQS_QUEUE_ORDER_PROCESSING: "${SQS_ORDER_PROCESSING}"

  # S3 Buckets (from your Terraform outputs)
  S3_EVENTS_BUCKET: "${S3_EVENTS_BUCKET}"

  # Database Configuration (from your Terraform outputs)
  DATABASE_ENDPOINT: "${DATABASE_ENDPOINT}"

  # ECR Repository
  ECR_REPOSITORY_URL: "${ECR_REPOSITORY_URL}"

  # API Configuration
  API_HOST: "0.0.0.0"
  API_PORT: "8000"

  # Feature Flags
  ENABLE_METRICS: "true"
  ENABLE_AUDIT_LOGGING: "true"
  ENABLE_RATE_LIMITING: "false"
EOF

# Generate Secret for sensitive data
cat >> kubernetes/secrets-config-generated.yaml << EOF

# Secret for sensitive configuration
apiVersion: v1
kind: Secret
metadata:
  name: order-service-secrets
  namespace: order-processor
  annotations:
    generated-from: terraform-outputs
    generated-at: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
type: Opaque
stringData:
  DATABASE_SECRET_ARN: "${DATABASE_SECRET_ARN}"
  DATABASE_SECRET_NAME: "${DATABASE_SECRET_NAME}"
EOF

print_success "✅ Generated kubernetes/secrets-config-generated.yaml"

# Also generate service account with dynamic IAM role
cat > kubernetes/service-account-generated.yaml << EOF
---
# Service Account for order-service with IAM role annotation (Generated from YOUR Terraform)
apiVersion: v1
kind: ServiceAccount
metadata:
  name: order-service-sa
  namespace: order-processor
  annotations:
    # IAM role ARN from your Terraform outputs
    eks.amazonaws.com/role-arn: ${ORDER_SERVICE_ROLE_ARN}
    generated-from: terraform-outputs
    generated-at: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

---
# ClusterRole for secrets access
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secret-reader
rules:
- apiGroups: ["secrets-store.csi.x-k8s.io"]
  resources: ["secretproviderclasses"]
  verbs: ["get", "list"]

---
# ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: order-service-secret-reader
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: secret-reader
subjects:
- kind: ServiceAccount
  name: order-service-sa
  namespace: order-processor
EOF

print_success "✅ Generated kubernetes/service-account-generated.yaml"

print_info "📊 Summary of extracted values from YOUR Terraform:"
echo "=================="
echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
echo "EKS Cluster: $EKS_CLUSTER_NAME"
echo "Database Endpoint: $DATABASE_ENDPOINT"
echo "Database Secret: $DATABASE_SECRET_NAME"
echo "SNS Order Events: $SNS_ORDER_EVENTS"
echo "SQS Order Processing: $SQS_ORDER_PROCESSING"
echo "S3 Events Bucket: $S3_EVENTS_BUCKET"
echo "Order Service Role: $ORDER_SERVICE_ROLE_ARN"
echo "ECR Repository: $ECR_REPOSITORY_URL"
echo ""

print_success "🎯 Ready to deploy with dynamic configuration!"
print_info "Use the generated files:"
print_info "  - kubernetes/secrets-config-generated.yaml"
print_info "  - kubernetes/service-account-generated.yaml"