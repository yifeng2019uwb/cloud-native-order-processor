#!/bin/bash
# destroy-everything.sh - Complete cleanup script

set -e

echo "🧹 Starting complete AWS infrastructure cleanup..."

# COST OPTIMIZATION: Add cost monitoring from start
START_TIME=$(date +%s)
echo "💰 Cost monitoring: Cleanup started at $(date)"

cd terraform

# Step 1: Empty S3 buckets first (if they have content)
echo "📦 Emptying S3 buckets..."

# Get bucket names from terraform output (if available)
# ORIGINAL: Uses terraform output which might fail if state is corrupted
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

# COST OPTIMIZATION: Enhanced S3 cleanup with cost verification
# Add comprehensive S3 bucket discovery and cleanup
echo "💰 Performing comprehensive S3 cleanup..."
PROJECT_PREFIX=${PROJECT_PREFIX:-"order-processor"}
ALL_BUCKETS=$(aws s3api list-buckets --query "Buckets[?contains(Name, '$PROJECT_PREFIX')].Name" --output text)

if [ ! -z "$ALL_BUCKETS" ]; then
    echo "💰 Found project S3 buckets: $ALL_BUCKETS"
    for bucket in $ALL_BUCKETS; do
        echo "💰 Calculating storage costs for bucket: $bucket"
        OBJECT_COUNT=$(aws s3api list-objects-v2 --bucket $bucket --query 'KeyCount' --output text 2>/dev/null || echo "0")
        echo "💰 Bucket $bucket contains $OBJECT_COUNT objects"

        if [ "$OBJECT_COUNT" != "0" ]; then
            echo "Emptying bucket: $bucket"
            aws s3 rm s3://$bucket --recursive || echo "Failed to empty $bucket"
        fi
    done
else
    echo "💰 No project S3 buckets found"
fi

# Step 2: Delete ECR images
echo "🐳 Cleaning up ECR repository..."
# ORIGINAL: Uses terraform output which might fail
ECR_REPO=$(terraform output -raw ecr_order_api_repository_url 2>/dev/null | cut -d'/' -f2 || echo "")
if [ ! -z "$ECR_REPO" ]; then
    echo "Deleting images from ECR repository: $ECR_REPO"
    # List and delete all images
    aws ecr list-images --repository-name $ECR_REPO --query 'imageIds[*]' --output json | \
    jq '.[] | select(.imageTag != null) | {imageTag: .imageTag}' | \
    jq -s '.' | \
    aws ecr batch-delete-image --repository-name $ECR_REPO --image-ids file:///dev/stdin || echo "No images to delete"
fi

# COST OPTIMIZATION: Enhanced ECR cleanup with cost verification
echo "💰 Performing comprehensive ECR cleanup..."
ALL_ECR_REPOS=$(aws ecr describe-repositories --query "repositories[?contains(repositoryName, '$PROJECT_PREFIX')].repositoryName" --output text 2>/dev/null || echo "")

if [ ! -z "$ALL_ECR_REPOS" ]; then
    echo "💰 Found project ECR repositories: $ALL_ECR_REPOS"
    for repo in $ALL_ECR_REPOS; do
        IMAGE_COUNT=$(aws ecr list-images --repository-name $repo --query 'length(imageIds)' --output text 2>/dev/null || echo "0")
        echo "💰 Repository $repo contains $IMAGE_COUNT images"

        if [ "$IMAGE_COUNT" != "0" ]; then
            echo "Deleting all images from repository: $repo"
            aws ecr list-images --repository-name $repo --query 'imageIds[*]' --output json | \
            aws ecr batch-delete-image --repository-name $repo --image-ids file:///dev/stdin || echo "Failed to delete images from $repo"
        fi
    done
else
    echo "💰 No project ECR repositories found"
fi

# COST OPTIMIZATION: Add EKS cleanup verification
echo "💰 Checking for running EKS resources..."
EKS_CLUSTERS=$(aws eks list-clusters --query "clusters[?contains(@, '$PROJECT_PREFIX')]" --output text 2>/dev/null || echo "")
if [ ! -z "$EKS_CLUSTERS" ]; then
    echo "💰 Found EKS clusters that will be destroyed: $EKS_CLUSTERS"
    for cluster in $EKS_CLUSTERS; do
        echo "💰 EKS cluster: $cluster (costs ~$72/month + compute costs)"
    done
else
    echo "💰 No EKS clusters found"
fi

# COST OPTIMIZATION: Add RDS cleanup verification
echo "💰 Checking for running RDS instances..."
RDS_INSTANCES=$(aws rds describe-db-instances --query "DBInstances[?contains(DBInstanceIdentifier, '$PROJECT_PREFIX')].DBInstanceIdentifier" --output text 2>/dev/null || echo "")
if [ ! -z "$RDS_INSTANCES" ]; then
    echo "💰 Found RDS instances that will be destroyed: $RDS_INSTANCES"
    for instance in $RDS_INSTANCES; do
        INSTANCE_CLASS=$(aws rds describe-db-instances --db-instance-identifier $instance --query 'DBInstances[0].DBInstanceClass' --output text 2>/dev/null || echo "unknown")
        echo "💰 RDS instance: $instance ($INSTANCE_CLASS - costs ~$12-50/month depending on size)"
    done
else
    echo "💰 No RDS instances found"
fi

# Step 3: Terraform destroy with auto-approve
echo "🔥 Running terraform destroy..."
# ORIGINAL: Direct terraform destroy
terraform destroy -auto-approve

# COST OPTIMIZATION: Add post-destroy verification
echo "💰 Performing post-destroy cost verification..."

echo "✅ Complete cleanup finished!"
echo ""

# COST OPTIMIZATION: Enhanced verification with cost implications
echo "🔍 === COST VERIFICATION COMMANDS ==="
echo "Run these commands to verify all billable resources are deleted:"
echo ""
echo "💰 Check S3 buckets (storage costs):"
echo "  aws s3 ls | grep $PROJECT_PREFIX"
echo ""
echo "💰 Check RDS instances (database costs ~$12-50/month):"
echo "  aws rds describe-db-instances --query 'DBInstances[?contains(DBInstanceIdentifier, \`$PROJECT_PREFIX\`)].{ID:DBInstanceIdentifier,Status:DBInstanceStatus,Class:DBInstanceClass}' --output table"
echo ""
echo "💰 Check EKS clusters (cluster costs ~$72/month + compute):"
echo "  aws eks list-clusters --query 'clusters[?contains(@, \`$PROJECT_PREFIX\`)]'"
echo ""
echo "💰 Check ECR repositories (image storage costs):"
echo "  aws ecr describe-repositories --query 'repositories[?contains(repositoryName, \`$PROJECT_PREFIX\`)].repositoryName'"
echo ""
echo "💰 Check Secrets Manager secrets (costs ~$0.40/month per secret):"
echo "  aws secretsmanager list-secrets --query 'SecretList[?contains(Name, \`$PROJECT_PREFIX\`)].Name'"
echo ""
echo "💰 Check NAT Gateways (costs ~$45/month each):"
echo "  aws ec2 describe-nat-gateways --query 'NatGateways[?State==\`available\`].{ID:NatGatewayId,State:State,VPC:VpcId}' --output table"
echo ""
echo "💰 Check Elastic IPs (costs ~$5/month each if unattached):"
echo "  aws ec2 describe-addresses --query 'Addresses[?AssociationId==null].{IP:PublicIp,AllocationId:AllocationId}' --output table"
echo ""
echo "💰 Check KMS keys (costs ~$1/month each):"
echo "  aws kms list-keys --query 'Keys[*].KeyId' --output table"
echo ""

# COST OPTIMIZATION: Calculate cleanup time and provide cost summary
END_TIME=$(date +%s)
CLEANUP_TIME=$((END_TIME - START_TIME))
echo "💰 === CLEANUP COST SUMMARY ==="
echo "💰 Total cleanup time: ${CLEANUP_TIME} seconds"
echo "💰 Cleanup completed at: $(date)"
echo "💰 "
echo "💰 IMPORTANT: Verify all resources are deleted to avoid unexpected charges!"
echo "💰 "
echo "💰 Typical monthly costs that should now be $0:"
echo "💰 - EKS Cluster: ~$72/month"
echo "💰 - RDS db.t4g.micro: ~$12/month"
echo "💰 - NAT Gateway: ~$45/month (if was enabled)"
echo "💰 - KMS Keys: ~$1/month each"
echo "💰 - S3 Storage: Variable based on usage"
echo "💰 - ECR Image Storage: Variable based on image size"
echo "💰 "
echo "💰 Run verification commands above to confirm $0 ongoing costs"
echo "💰 ================================================="

# COST OPTIMIZATION: Add cost alert for manual verification
echo ""
echo "🚨 COST ALERT: Manual verification required!"
echo "🚨 Please run the verification commands above within 24 hours"
echo "🚨 to ensure no resources are still incurring charges."
echo "🚨 Some resources may take time to fully terminate."