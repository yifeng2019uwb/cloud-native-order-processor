#!/bin/bash
# check-prerequisites.sh

echo "🔍 Checking prerequisites for AWS Secrets Manager setup..."

# Check AWS CLI
if command -v aws &> /dev/null; then
    echo "✅ AWS CLI is installed"
    aws --version
else
    echo "❌ AWS CLI is not installed"
    echo "Install it: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check jq
if command -v jq &> /dev/null; then
    echo "✅ jq is installed"
    jq --version
else
    echo "❌ jq is not installed"
    echo "Install it:"
    echo "  Ubuntu/Debian: sudo apt-get install jq"
    echo "  macOS: brew install jq"
    echo "  Amazon Linux: sudo yum install jq"
    exit 1
fi

# Check PostgreSQL client
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL client is installed"
    psql --version
else
    echo "❌ PostgreSQL client (psql) is not installed"
    echo "Install it:"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql-client"
    echo "  macOS: brew install postgresql"
    echo "  Amazon Linux: sudo yum install postgresql"
    exit 1
fi

# Check AWS credentials
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ AWS credentials are configured"
    aws sts get-caller-identity
else
    echo "❌ AWS credentials are not configured"
    echo "Configure them: aws configure"
    exit 1
fi

# Check Terraform
if command -v terraform &> /dev/null; then
    echo "✅ Terraform is installed"
    terraform version
else
    echo "❌ Terraform is not installed"
    exit 1
fi

# COST OPTIMIZATION: Add cost estimation tools check
echo ""
echo "💰 Checking cost estimation and monitoring tools..."

# Check if AWS CLI supports cost explorer (optional but helpful)
if aws ce get-cost-and-usage help &> /dev/null; then
    echo "✅ AWS Cost Explorer CLI support available"
else
    echo "⚠️ AWS Cost Explorer CLI not available (optional for cost monitoring)"
fi

# COST OPTIMIZATION: Get current AWS region and account info for cost estimation
echo ""
echo "💰 === Cost Estimation Setup ==="

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "unknown")
AWS_REGION=$(aws configure get region 2>/dev/null || echo "us-west-2")

echo "💰 AWS Account ID: $AWS_ACCOUNT_ID"
echo "💰 AWS Region: $AWS_REGION"

# COST OPTIMIZATION: Regional cost warnings
case $AWS_REGION in
    "us-east-1")
        echo "💰 ✅ Cost-optimal region: us-east-1 typically has lowest prices"
        ;;
    "us-west-2"|"us-east-2"|"eu-west-1")
        echo "💰 ✅ Good cost region: $AWS_REGION has competitive pricing"
        ;;
    *)
        echo "💰 ⚠️ Cost warning: $AWS_REGION may have higher prices than us-east-1"
        echo "💰 Consider using us-east-1 for practice/learning to minimize costs"
        ;;
esac

# COST OPTIMIZATION: Check for existing resources that might incur costs
echo ""
echo "💰 Checking for existing billable resources in your account..."

# Check for running EC2 instances
RUNNING_INSTANCES=$(aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query 'Reservations[*].Instances[*].InstanceId' --output text 2>/dev/null | wc -w)
if [ "$RUNNING_INSTANCES" -gt 0 ]; then
    echo "💰 ⚠️ Found $RUNNING_INSTANCES running EC2 instances (incurring charges)"
    echo "💰 List them: aws ec2 describe-instances --filters 'Name=instance-state-name,Values=running' --query 'Reservations[*].Instances[*].{ID:InstanceId,Type:InstanceType,State:State.Name}' --output table"
else
    echo "💰 ✅ No running EC2 instances found"
fi

# Check for existing EKS clusters
EKS_CLUSTERS=$(aws eks list-clusters --query 'clusters' --output text 2>/dev/null | wc -w)
if [ "$EKS_CLUSTERS" -gt 0 ]; then
    echo "💰 ⚠️ Found $EKS_CLUSTERS existing EKS clusters (~$72/month each)"
    echo "💰 List them: aws eks list-clusters"
else
    echo "💰 ✅ No existing EKS clusters found"
fi

# Check for RDS instances
RDS_INSTANCES=$(aws rds describe-db-instances --query 'DBInstances[?DBInstanceStatus==`available`].DBInstanceIdentifier' --output text 2>/dev/null | wc -w)
if [ "$RDS_INSTANCES" -gt 0 ]; then
    echo "💰 ⚠️ Found $RDS_INSTANCES running RDS instances (incurring charges)"
    echo "💰 List them: aws rds describe-db-instances --query 'DBInstances[?DBInstanceStatus==\`available\`].{ID:DBInstanceIdentifier,Class:DBInstanceClass,Engine:Engine}' --output table"
else
    echo "💰 ✅ No running RDS instances found"
fi

# Check for NAT Gateways
NAT_GATEWAYS=$(aws ec2 describe-nat-gateways --filter "Name=state,Values=available" --query 'NatGateways[*].NatGatewayId' --output text 2>/dev/null | wc -w)
if [ "$NAT_GATEWAYS" -gt 0 ]; then
    echo "💰 ⚠️ Found $NAT_GATEWAYS NAT Gateways (~$45/month each)"
    echo "💰 List them: aws ec2 describe-nat-gateways --filter 'Name=state,Values=available' --query 'NatGateways[*].{ID:NatGatewayId,VPC:VpcId,State:State}' --output table"
else
    echo "💰 ✅ No NAT Gateways found"
fi

# COST OPTIMIZATION: Provide cost estimation for the infrastructure we're about to deploy
echo ""
echo "💰 === ESTIMATED MONTHLY COSTS FOR THIS PROJECT ==="
echo "💰 "
echo "💰 Cost Profile Options:"
echo "💰 "
echo "💰 MINIMAL Profile (~$85-110/month):"
echo "💰   - EKS Cluster: ~$72/month (unavoidable cluster cost)"
echo "💰   - EKS Spot Instances: ~$3-8/month (t3.micro spot)"
echo "💰   - RDS db.t4g.micro: ~$12/month"
echo "💰   - No NAT Gateway: $0 (uses VPC endpoints)"
echo "💰   - No KMS encryption: $0"
echo "💰   - Minimal S3 storage: ~$1-3/month"
echo "💰 "
echo "💰 LEARNING Profile (~$130-155/month):"
echo "💰   - EKS Cluster: ~$72/month"
echo "💰   - EKS Fargate: ~$50-70/month (more expensive than spot)"
echo "💰   - RDS db.t4g.micro: ~$12/month"
echo "💰   - No NAT Gateway: $0 (cost optimized)"
echo "💰   - KMS encryption: ~$3/month"
echo "💰   - Standard S3 storage: ~$3-5/month"
echo "💰 "
echo "💰 PRODUCTION Profile (~$220-280/month):"
echo "💰   - EKS Cluster: ~$72/month"
echo "💰   - EKS Fargate: ~$80-120/month (more resources)"
echo "💰   - RDS db.t4g.small+: ~$25-50/month"
echo "💰   - NAT Gateway: ~$45/month"
echo "💰   - KMS encryption: ~$3/month"
echo "💰   - Enhanced monitoring: ~$10-20/month"
echo "💰 "
echo "💰 COST REDUCTION TIPS:"
echo "💰   1. Use 'minimal' profile for function testing"
echo "💰   2. Use 'learning' profile for architecture learning"
echo "💰   3. Deploy → Test → Destroy within 24 hours for practice"
echo "💰   4. Always run 'terraform destroy' when done"
echo "💰   5. Monitor AWS billing dashboard daily during learning"
echo "💰 "

# COST OPTIMIZATION: Add cost monitoring setup instructions
# echo "💰 === COST MONITORING SETUP ==="
# echo "💰 "
# echo "💰 1. Set up billing alerts (one-time setup):"
# echo "💰    aws cloudwatch put-metric-alarm --alarm-name 'BillingAlert' --alarm-description 'Alert when monthly bill exceeds \$100' --metric-name EstimatedCharges --namespace AWS/Billing --statistic Maximum --period 86400 --threshold 100 --comparison-operator GreaterThanThreshold"
# echo "💰 "
# echo "💰 2. Check current month costs:"
# echo "💰    aws ce get-cost-and-usage --time-period Start=\$(date -d 'first day of this month' +%Y-%m-%d),End=\$(date +%Y-%m-%d) --granularity MONTHLY --metrics BlendedCost"
# echo "💰 "
# echo "💰 3. Monitor daily costs during learning:"
# echo "💰    aws ce get-cost-and-usage --time-period Start=\$(date -d '7 days ago' +%Y-%m-%d),End=\$(date +%Y-%m-%d) --granularity DAILY --metrics BlendedCost"
# echo "💰 "

echo ""
echo "🎉 All prerequisites are met! You can proceed with the Secrets Manager setup."

# COST OPTIMIZATION: Final cost reminder
echo ""
echo "💰 === FINAL COST REMINDERS ==="
echo "💰 - Choose your cost profile wisely: minimal → learning → production"
echo "💰 - EKS cluster ($72/month) starts charging immediately upon creation"
echo "💰 - RDS instance ($12+/month) charges even when not actively used"
echo "💰 - Practice deploy → test → destroy cycles to minimize costs"
echo "💰 - Set up billing alerts before starting your first deployment"
echo "💰 - Check AWS billing dashboard daily during learning phase"
echo "💰 ==============================================="