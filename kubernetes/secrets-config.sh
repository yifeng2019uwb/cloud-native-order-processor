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

# Extract specific values using jq
AWS_ACCOUNT_ID=$(echo $TERRAFORM_OUTPUT | jq -r '.aws_account_id.value // "940482447349"')
AWS_REGION=$(echo $TERRAFORM_OUTPUT | jq -r '.aws_region.value // "us-west-2"')

# SNS Topics
SNS_ORDER_EVENTS=$(echo $TERRAFORM_OUTPUT | jq -r '.sns_topics.value.order_events // ""')
SNS_PAYMENT_EVENTS=$(echo $TERRAFORM_OUTPUT | jq -r '.sns_topics.value.payment_events // ""')
SNS_INVENTORY_EVENTS=$(echo $TERRAFORM_OUTPUT | jq -r '.sns_topics.value.inventory_events // ""')
SNS_NOTIFICATION_EVENTS=$(echo $TERRAFORM_OUTPUT | jq -r '.sns_topics.value.notification_events // ""')

# SQS Queues
SQS_ORDER_PROCESSING=$(echo $TERRAFORM_OUTPUT | jq -r '.sqs_queues.value.order_processing // ""')
SQS_PAYMENT_PROCESSING=$(echo $TERRAFORM_OUTPUT | jq -r '.sqs_queues.value.payment_processing // ""')
SQS_INVENTORY_PROCESSING=$(echo $TERRAFORM_OUTPUT | jq -r '.sqs_queues.value.inventory_processing // ""')
SQS_NOTIFICATION_PROCESSING=$(echo $TERRAFORM_OUTPUT | jq -r '.sqs_queues.value.notification_processing // ""')

# S3 Buckets
S3_EVENTS_BUCKET=$(echo $TERRAFORM_OUTPUT | jq -r '.s3_buckets.value.events // ""')
S3_BACKUP_BUCKET=$(echo $TERRAFORM_OUTPUT | jq -r '.s3_buckets.value.backups // ""')

# IAM Role for pods
IAM_POD_ROLE=$(echo $TERRAFORM_OUTPUT | jq -r '.iam_roles.value.pod_role // ""')

# RDS Database info
DB_ENDPOINT=$(echo $TERRAFORM_OUTPUT | jq -r '.rds_instance.value.endpoint // ""')
DB_PORT=$(echo $TERRAFORM_OUTPUT | jq -r '.rds_instance.value.port // "5432"')

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
      - objectName: "order-processor-dev-db-credentials"
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
# ConfigMap for application configuration (Generated from Terraform)
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

  # SNS Topics (from Terraform outputs)
  SNS_TOPIC_ORDER_EVENTS: "${SNS_ORDER_EVENTS}"
  SNS_TOPIC_PAYMENT_EVENTS: "${SNS_PAYMENT_EVENTS}"
  SNS_TOPIC_INVENTORY_EVENTS: "${SNS_INVENTORY_EVENTS}"
  SNS_TOPIC_NOTIFICATION_EVENTS: "${SNS_NOTIFICATION_EVENTS}"

  # SQS Queues (from Terraform outputs)
  SQS_QUEUE_ORDER_PROCESSING: "${SQS_ORDER_PROCESSING}"
  SQS_QUEUE_PAYMENT_PROCESSING: "${SQS_PAYMENT_PROCESSING}"
  SQS_QUEUE_INVENTORY_PROCESSING: "${SQS_INVENTORY_PROCESSING}"
  SQS_QUEUE_NOTIFICATION_PROCESSING: "${SQS_NOTIFICATION_PROCESSING}"

  # S3 Buckets (from Terraform outputs)
  S3_EVENTS_BUCKET: "${S3_EVENTS_BUCKET}"
  S3_BACKUP_BUCKET: "${S3_BACKUP_BUCKET}"

  # Database Configuration (from Terraform outputs)
  DB_ENDPOINT: "${DB_ENDPOINT}"
  DB_PORT: "${DB_PORT}"

  # API Configuration
  API_HOST: "0.0.0.0"
  API_PORT: "8000"

  # Feature Flags
  ENABLE_METRICS: "true"
  ENABLE_AUDIT_LOGGING: "true"
  ENABLE_RATE_LIMITING: "false"
EOF

print_success "✅ Generated kubernetes/secrets-config-generated.yaml"

# Also generate service account with dynamic IAM role
cat > kubernetes/service-account-generated.yaml << EOF
---
# Service Account for order-service with IAM role annotation (Generated from Terraform)
apiVersion: v1
kind: ServiceAccount
metadata:
  name: order-service-sa
  namespace: order-processor
  annotations:
    # IAM role ARN from Terraform outputs
    eks.amazonaws.com/role-arn: ${IAM_POD_ROLE}
    generated-from: terraform-outputs
    generated-at: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

---
# ClusterRole for secrets access
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
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

print_info "📊 Summary of extracted values:"
echo "=================="
echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
echo "SNS Order Events: $SNS_ORDER_EVENTS"
echo "SQS Order Processing: $SQS_ORDER_PROCESSING"
echo "S3 Events Bucket: $S3_EVENTS_BUCKET"
echo "IAM Pod Role: $IAM_POD_ROLE"
echo "Database Endpoint: $DB_ENDPOINT"
echo ""

print_success "🎯 Ready to deploy with dynamic configuration!"
print_info "Use the generated files:"
print_info "  - kubernetes/secrets-config-generated.yaml"
print_info "  - kubernetes/service-account-generated.yaml"