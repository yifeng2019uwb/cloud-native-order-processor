#!/bin/bash
# destroy-everything.sh - Complete cleanup script

set -e

echo "🧹 Starting complete AWS infrastructure cleanup..."

cd terraform

# Step 1: Empty S3 buckets first (if they have content)
echo "📦 Emptying S3 buckets..."

# Get bucket names from terraform output (if available)
EVENT_BUCKET=$(terraform output -raw s3_events_bucket_name 2>/dev/null || echo "")
if [ ! -z "$EVENT_BUCKET" ]; then
    echo "Emptying events bucket: $EVENT_BUCKET"
    aws s3 rm s3://$EVENT_BUCKET --recursive || echo "Bucket already empty or doesn't exist"
fi

# Check for backup bucket (might not be in outputs)
BACKUP_BUCKET=$(aws s3 ls | grep "order-processor.*backups" | awk '{print $3}' || echo "")
if [ ! -z "$BACKUP_BUCKET" ]; then
    echo "Emptying backup bucket: $BACKUP_BUCKET"
    aws s3 rm s3://$BACKUP_BUCKET --recursive || echo "Bucket already empty or doesn't exist"
fi

# Step 2: Delete ECR images
echo "🐳 Cleaning up ECR repository..."
ECR_REPO=$(terraform output -raw ecr_order_api_repository_url 2>/dev/null | cut -d'/' -f2 || echo "")
if [ ! -z "$ECR_REPO" ]; then
    echo "Deleting images from ECR repository: $ECR_REPO"
    # List and delete all images
    aws ecr list-images --repository-name $ECR_REPO --query 'imageIds[*]' --output json | \
    jq '.[] | select(.imageTag != null) | {imageTag: .imageTag}' | \
    jq -s '.' | \
    aws ecr batch-delete-image --repository-name $ECR_REPO --image-ids file:///dev/stdin || echo "No images to delete"
fi

# Step 3: Terraform destroy with auto-approve
echo "🔥 Running terraform destroy..."
terraform destroy -auto-approve

echo "✅ Complete cleanup finished!"
echo ""
echo "🔍 Verification commands:"
echo "  - Check S3: aws s3 ls | grep order-processor"
echo "  - Check RDS: aws rds describe-db-instances --query 'DBInstances[?contains(DBInstanceIdentifier, \`order-processor\`)].DBInstanceIdentifier'"
echo "  - Check EKS: aws eks list-clusters --query 'clusters[?contains(@, \`order-processor\`)]'"
echo "  - Check ECR: aws ecr describe-repositories --query 'repositories[?contains(repositoryName, \`order-processor\`)].repositoryName'"
echo "  - Check Secrets: aws secretsmanager list-secrets --query 'SecretList[?contains(Name, \`order-processor\`)].Name'"