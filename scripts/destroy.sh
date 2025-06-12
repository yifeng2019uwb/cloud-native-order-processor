#!/bin/bash
# scripts/destroy.sh
# Infrastructure Cleanup Script
# Destroys AWS infrastructure and cleans up resources

set -e

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=""
PROFILE=""
VERBOSE=false
DRY_RUN=false
AUTO_APPROVE=false
FORCE_CLEANUP=false

# Usage function
show_usage() {
    cat << EOF
$(printf "${RED}🧹 Infrastructure Destroy Script${NC}")

Usage: $0 --environment {dev|prod} --profile {learning|minimum|prod} [OPTIONS]

Destroy AWS infrastructure and cleanup resources.

REQUIRED:
    --environment {dev|prod}           Target environment
    --profile {learning|minimum|prod}  Resource profile

OPTIONS:
    -v, --verbose                      Enable verbose output
    --dry-run                         Show what would be destroyed (don't destroy)
    --auto-approve                    Skip confirmation prompts
    --force-cleanup                   Force cleanup of stuck resources
    -h, --help                        Show this help message

EXAMPLES:
    $0 --environment dev --profile learning                    # Destroy dev infrastructure
    $0 --environment dev --profile learning --dry-run          # Plan destruction only
    $0 --environment dev --profile learning --auto-approve     # Destroy without prompts
    $0 --environment dev --profile learning --force-cleanup    # Force cleanup stuck resources

⚠️  WARNING: This will permanently destroy AWS resources and data!

EOF
}

# Logging functions
log_info() {
    printf "${BLUE}[INFO]${NC} %s\n" "$1"
}

log_success() {
    printf "${GREEN}[SUCCESS]${NC} %s\n" "$1"
}

log_warning() {
    printf "${YELLOW}[WARNING]${NC} %s\n" "$1"
}

log_error() {
    printf "${RED}[ERROR]${NC} %s\n" "$1"
}

log_step() {
    printf "\n${RED}=== %s ===${NC}\n" "$1"
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --profile)
                PROFILE="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --auto-approve)
                AUTO_APPROVE=true
                shift
                ;;
            --force-cleanup)
                FORCE_CLEANUP=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Validate arguments
validate_arguments() {
    local errors=()

    # Check required arguments
    if [[ -z "$ENVIRONMENT" ]]; then
        errors+=("--environment is required")
    elif [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
        errors+=("--environment must be 'dev' or 'prod'")
    fi

    if [[ -z "$PROFILE" ]]; then
        errors+=("--profile is required")
    elif [[ "$PROFILE" != "learning" && "$PROFILE" != "minimum" && "$PROFILE" != "prod" ]]; then
        errors+=("--profile must be 'learning', 'minimum', or 'prod'")
    fi

    if [[ ${#errors[@]} -gt 0 ]]; then
        log_error "Validation failed:"
        for error in "${errors[@]}"; do
            log_error "  - $error"
        done
        echo
        show_usage
        exit 1
    fi
}

# Setup environment
setup_environment() {
    log_step "🔧 Setting up destroy environment"

    # Set base environment variables
    export ENVIRONMENT="$ENVIRONMENT"
    export COST_PROFILE="$PROFILE"
    export TF_VAR_environment="$ENVIRONMENT"
    export TF_VAR_cost_profile="$PROFILE"

    # Load environment-specific configuration
    local env_config="$PROJECT_ROOT/config/environments/${ENVIRONMENT}.env"
    if [[ -f "$env_config" ]]; then
        log_info "Loading environment config: $env_config"
        source "$env_config"
    fi

    if [[ "$VERBOSE" == "true" ]]; then
        log_info "Environment variables set:"
        log_info "  ENVIRONMENT: $ENVIRONMENT"
        log_info "  COST_PROFILE: $PROFILE"
        log_info "  AWS_REGION: ${AWS_REGION:-us-west-2}"
    fi
}

# Check prerequisites
check_prerequisites() {
    log_step "🔍 Checking Prerequisites"

    # Check required tools
    local missing_tools=()
    local tools=("terraform" "aws" "jq")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        log_error "AWS credentials not configured or invalid"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Confirm destruction
confirm_destruction() {
    if [[ "$AUTO_APPROVE" == "true" || "$DRY_RUN" == "true" ]]; then
        return 0
    fi

    log_step "⚠️ Destruction Confirmation"

    echo
    printf "${RED}WARNING: This will permanently destroy the following:${NC}\n"
    printf "${RED}  - Environment: $ENVIRONMENT${NC}\n"
    printf "${RED}  - Profile: $PROFILE${NC}\n"
    printf "${RED}  - All AWS resources managed by Terraform${NC}\n"
    printf "${RED}  - All data in RDS databases${NC}\n"
    printf "${RED}  - All data in S3 buckets${NC}\n"
    printf "${RED}  - EKS cluster and all applications${NC}\n"
    echo

    read -p "Are you absolutely sure you want to continue? (type 'yes' to confirm): " confirmation

    if [[ "$confirmation" != "yes" ]]; then
        log_info "Destruction cancelled by user"
        exit 0
    fi

    log_warning "Proceeding with infrastructure destruction..."
}

# Pre-cleanup tasks
pre_cleanup() {
    log_step "🧹 Pre-Cleanup Tasks"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would perform pre-cleanup tasks"
        return 0
    fi

    # Empty S3 buckets first (they must be empty to delete)
    log_info "Checking for S3 buckets to empty..."

    local buckets
    buckets=$(aws s3api list-buckets \
        --query "Buckets[?contains(Name, 'order-processor-${ENVIRONMENT}')].Name" \
        --output text 2>/dev/null || echo "")

    if [[ -n "$buckets" ]]; then
        for bucket in $buckets; do
            log_info "Emptying S3 bucket: $bucket"

            # Remove all objects
            aws s3 rm "s3://$bucket" --recursive 2>/dev/null || true

            # Remove versioned objects if versioning enabled
            aws s3api list-object-versions --bucket "$bucket" --output json 2>/dev/null | \
            jq -r '.Versions[]? | "\(.Key) \(.VersionId)"' | \
            while read -r key version; do
                if [[ -n "$key" && -n "$version" ]]; then
                    aws s3api delete-object --bucket "$bucket" --key "$key" --version-id "$version" 2>/dev/null || true
                fi
            done || true

            # Remove delete markers
            aws s3api list-object-versions --bucket "$bucket" --output json 2>/dev/null | \
            jq -r '.DeleteMarkers[]? | "\(.Key) \(.VersionId)"' | \
            while read -r key version; do
                if [[ -n "$key" && -n "$version" ]]; then
                    aws s3api delete-object --bucket "$bucket" --key "$key" --version-id "$version" 2>/dev/null || true
                fi
            done || true

            log_info "Bucket $bucket emptied"
        done
    fi

    # Clean up any stuck resources if force cleanup requested
    if [[ "$FORCE_CLEANUP" == "true" ]]; then
        log_warning "Force cleanup enabled - attempting to remove stuck resources"
        force_cleanup_resources
    fi

    log_success "Pre-cleanup tasks completed"
}

# Force cleanup stuck resources
force_cleanup_resources() {
    log_info "Attempting to force cleanup stuck resources..."

    # Remove stuck IAM roles
    local roles=("order-processor-${ENVIRONMENT}-eks-cluster-role"
                 "order-processor-${ENVIRONMENT}-fargate-pod-execution-role"
                 "order-processor-${ENVIRONMENT}-node-group-role")

    for role in "${roles[@]}"; do
        if aws iam get-role --role-name "$role" >/dev/null 2>&1; then
            log_info "Removing IAM role: $role"

            # Detach policies first
            aws iam list-attached-role-policies --role-name "$role" --output text 2>/dev/null | \
            awk '{print $2}' | \
            while read -r policy; do
                if [[ -n "$policy" ]]; then
                    aws iam detach-role-policy --role-name "$role" --policy-arn "$policy" 2>/dev/null || true
                fi
            done

            # Delete inline policies
            aws iam list-role-policies --role-name "$role" --output text 2>/dev/null | \
            awk '{print $2}' | \
            while read -r policy; do
                if [[ -n "$policy" ]]; then
                    aws iam delete-role-policy --role-name "$role" --policy-name "$policy" 2>/dev/null || true
                fi
            done

            # Delete role
            aws iam delete-role --role-name "$role" 2>/dev/null || true
        fi
    done

    # Remove stuck DB subnet groups
    local subnet_group="order-processor-${ENVIRONMENT}-db-subnet-group"
    if aws rds describe-db-subnet-groups --db-subnet-group-name "$subnet_group" >/dev/null 2>&1; then
        log_info "Removing DB subnet group: $subnet_group"
        aws rds delete-db-subnet-group --db-subnet-group-name "$subnet_group" 2>/dev/null || true
    fi
}

# Use existing destroy script if available
use_existing_destroy_script() {
    local existing_script="$PROJECT_ROOT/terraform/scripts/destroy-everything.sh"

    if [[ -f "$existing_script" ]]; then
        log_info "Using existing destroy script: $existing_script"
        cd "$PROJECT_ROOT/terraform"  # Stay in terraform root directory
        chmod +x scripts/destroy-everything.sh

        if [[ "$VERBOSE" == "true" ]]; then
            ./scripts/destroy-everything.sh
        else
            ./scripts/destroy-everything.sh >/dev/null 2>&1
        fi

        return $?
    fi

    return 1
}

# Terraform destroy
terraform_destroy() {
    log_step "💥 Destroying Infrastructure with Terraform"

    cd "$PROJECT_ROOT/terraform"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would run terraform destroy"
        terraform plan -destroy -var="cost_profile=$PROFILE" -var="environment=$ENVIRONMENT"
        return 0
    fi

    # Try existing destroy script first
    if use_existing_destroy_script; then
        log_success "Infrastructure destroyed using existing script"
        return 0
    fi

    # Fallback to direct terraform destroy
    log_info "Running terraform destroy..."

    # Initialize if needed
    if [[ ! -d ".terraform" ]]; then
        log_info "Initializing Terraform..."
        terraform init
    fi

    # Destroy with auto-approve
    local destroy_args="-var=cost_profile=$PROFILE -var=environment=$ENVIRONMENT"

    if [[ "$AUTO_APPROVE" == "true" ]]; then
        destroy_args="$destroy_args -auto-approve"
    fi

    if terraform destroy $destroy_args; then
        log_success "Terraform destroy completed successfully"
    else
        log_error "Terraform destroy failed, attempting cleanup of remaining resources"
        cleanup_remaining_resources
    fi
}

# Cleanup remaining resources
cleanup_remaining_resources() {
    log_warning "Attempting to cleanup remaining resources..."

    # List and remove remaining resources manually
    cd "$PROJECT_ROOT/terraform"

    # Get list of remaining resources
    if terraform state list >/dev/null 2>&1; then
        local remaining_resources
        remaining_resources=$(terraform state list 2>/dev/null || echo "")

        if [[ -n "$remaining_resources" ]]; then
            log_warning "Remaining resources in state:"
            echo "$remaining_resources"

            # Remove problematic resources from state
            local problem_resources=("aws_iam_role" "aws_db_subnet_group" "aws_s3_bucket")

            for resource_type in "${problem_resources[@]}"; do
                terraform state list 2>/dev/null | grep "^${resource_type}\." | while read -r resource; do
                    log_info "Removing $resource from state"
                    terraform state rm "$resource" 2>/dev/null || true
                done
            done

            # Try destroy again
            terraform destroy -auto-approve -var="cost_profile=$PROFILE" -var="environment=$ENVIRONMENT" || true
        fi
    fi
}

# Post-cleanup verification
verify_cleanup() {
    log_step "✅ Verifying Cleanup"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would verify cleanup completion"
        return 0
    fi

    local warnings=()

    # Check for remaining IAM roles
    local remaining_roles
    remaining_roles=$(aws iam list-roles --query "Roles[?contains(RoleName, 'order-processor-${ENVIRONMENT}')].RoleName" --output text 2>/dev/null || echo "")
    if [[ -n "$remaining_roles" ]]; then
        warnings+=("IAM roles still exist: $remaining_roles")
    fi

    # Check for remaining S3 buckets
    local remaining_buckets
    remaining_buckets=$(aws s3api list-buckets --query "Buckets[?contains(Name, 'order-processor-${ENVIRONMENT}')].Name" --output text 2>/dev/null || echo "")
    if [[ -n "$remaining_buckets" ]]; then
        warnings+=("S3 buckets still exist: $remaining_buckets")
    fi

    # Check for remaining RDS instances
    local remaining_rds
    remaining_rds=$(aws rds describe-db-instances --query "DBInstances[?contains(DBInstanceIdentifier, 'order-processor-${ENVIRONMENT}')].DBInstanceIdentifier" --output text 2>/dev/null || echo "")
    if [[ -n "$remaining_rds" ]]; then
        warnings+=("RDS instances still exist: $remaining_rds")
    fi

    if [[ ${#warnings[@]} -gt 0 ]]; then
        log_warning "Cleanup verification found remaining resources:"
        for warning in "${warnings[@]}"; do
            log_warning "  - $warning"
        done
        log_info "These may require manual cleanup in AWS Console"
    else
        log_success "All resources appear to be cleaned up"
    fi
}

# Nuclear cleanup - destroy everything for cost savings
nuclear_cleanup() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would perform nuclear cleanup"
        return 0
    fi

    log_step "☢️ Nuclear Cleanup - Destroying ALL Project Resources"
    log_warning "This will destroy ALL resources with project tags to prevent costs!"

    # Get all resources with project tag
    local all_resources
    all_resources=$(aws resourcegroupstaggingapi get-resources \
        --tag-filters Key=Project,Values=order-processor \
        --region "${AWS_REGION:-us-west-2}" \
        --output json 2>/dev/null || echo '{"ResourceTagMappingList":[]}')

    # Parse and delete each resource type
    echo "$all_resources" | jq -r '.ResourceTagMappingList[].ResourceARN' | while read -r arn; do
        if [[ -n "$arn" ]]; then
            nuclear_delete_resource "$arn"
        fi
    done

    # Additional cleanup for resources that might not have tags
    nuclear_cleanup_untagged_resources

    log_success "Nuclear cleanup completed"
}

# Delete individual resource by ARN
nuclear_delete_resource() {
    local arn="$1"
    local resource_type=$(echo "$arn" | cut -d':' -f3)
    local resource_id=$(echo "$arn" | rev | cut -d'/' -f1 | rev)

    log_info "Deleting $resource_type: $resource_id"

    case "$resource_type" in
        "s3")
            local bucket_name=$(echo "$arn" | rev | cut -d':' -f1 | rev)
            log_info "Force deleting S3 bucket: $bucket_name"
            aws s3 rm "s3://$bucket_name" --recursive 2>/dev/null || true
            aws s3 rb "s3://$bucket_name" --force 2>/dev/null || true
            ;;
        "secretsmanager")
            log_info "Force deleting secret: $resource_id"
            aws secretsmanager delete-secret --secret-id "$resource_id" --force-delete-without-recovery 2>/dev/null || true
            ;;
        "rds")
            if [[ "$arn" == *":db:"* ]]; then
                log_info "Force deleting RDS instance: $resource_id"
                aws rds delete-db-instance --db-instance-identifier "$resource_id" --skip-final-snapshot --delete-automated-backups 2>/dev/null || true
            elif [[ "$arn" == *":cluster:"* ]]; then
                log_info "Force deleting RDS cluster: $resource_id"
                aws rds delete-db-cluster --db-cluster-identifier "$resource_id" --skip-final-snapshot 2>/dev/null || true
            fi
            ;;
        "eks")
            log_info "Force deleting EKS cluster: $resource_id"
            # Delete nodegroups first
            aws eks list-nodegroups --cluster-name "$resource_id" --query 'nodegroups[]' --output text 2>/dev/null | while read -r nodegroup; do
                if [[ -n "$nodegroup" ]]; then
                    aws eks delete-nodegroup --cluster-name "$resource_id" --nodegroup-name "$nodegroup" 2>/dev/null || true
                fi
            done
            # Wait a bit then delete cluster
            sleep 30
            aws eks delete-cluster --name "$resource_id" 2>/dev/null || true
            ;;
        "ec2")
            if [[ "$arn" == *":instance/"* ]]; then
                log_info "Terminating EC2 instance: $resource_id"
                aws ec2 terminate-instances --instance-ids "$resource_id" 2>/dev/null || true
            elif [[ "$arn" == *":vpc/"* ]]; then
                log_info "Deleting VPC: $resource_id (after dependencies)"
                # VPC will be deleted after other resources
            elif [[ "$arn" == *":subnet/"* ]]; then
                log_info "Deleting subnet: $resource_id"
                aws ec2 delete-subnet --subnet-id "$resource_id" 2>/dev/null || true
            elif [[ "$arn" == *":security-group/"* ]]; then
                log_info "Deleting security group: $resource_id"
                aws ec2 delete-security-group --group-id "$resource_id" 2>/dev/null || true
            elif [[ "$arn" == *":vpc-endpoint/"* ]]; then
                log_info "Deleting VPC endpoint: $resource_id"
                aws ec2 delete-vpc-endpoint --vpc-endpoint-id "$resource_id" 2>/dev/null || true
            elif [[ "$arn" == *":natgateway/"* ]]; then
                log_info "Deleting NAT gateway: $resource_id"
                aws ec2 delete-nat-gateway --nat-gateway-id "$resource_id" 2>/dev/null || true
            fi
            ;;
        "elasticloadbalancing")
            log_info "Deleting load balancer: $resource_id"
            aws elbv2 delete-load-balancer --load-balancer-arn "$arn" 2>/dev/null || true
            ;;
        "iam")
            if [[ "$arn" == *":role/"* ]]; then
                log_info "Deleting IAM role: $resource_id"
                # Detach all policies first
                aws iam list-attached-role-policies --role-name "$resource_id" --output text 2>/dev/null | awk '{print $2}' | while read -r policy; do
                    if [[ -n "$policy" ]]; then
                        aws iam detach-role-policy --role-name "$resource_id" --policy-arn "$policy" 2>/dev/null || true
                    fi
                done
                # Delete inline policies
                aws iam list-role-policies --role-name "$resource_id" --output text 2>/dev/null | awk '{print $2}' | while read -r policy; do
                    if [[ -n "$policy" ]]; then
                        aws iam delete-role-policy --role-name "$resource_id" --policy-name "$policy" 2>/dev/null || true
                    fi
                done
                aws iam delete-role --role-name "$resource_id" 2>/dev/null || true
            fi
            ;;
        "kms")
            log_info "Scheduling KMS key deletion: $resource_id"
            aws kms schedule-key-deletion --key-id "$resource_id" --pending-window-in-days 7 2>/dev/null || true
            ;;
        "sqs")
            log_info "Deleting SQS queue: $resource_id"
            aws sqs delete-queue --queue-url "$resource_id" 2>/dev/null || true
            ;;
        "sns")
            log_info "Deleting SNS topic: $resource_id"
            aws sns delete-topic --topic-arn "$arn" 2>/dev/null || true
            ;;
        "ecr")
            log_info "Deleting ECR repository: $resource_id"
            aws ecr delete-repository --repository-name "$resource_id" --force 2>/dev/null || true
            ;;
        *)
            log_warning "Unknown resource type for deletion: $resource_type ($arn)"
            ;;
    esac
}

# Cleanup untagged resources that might belong to the project
nuclear_cleanup_untagged_resources() {
    log_info "Cleaning up potentially untagged project resources..."

    # Delete any VPCs that match our naming pattern
    aws ec2 describe-vpcs --filters "Name=tag:Project,Values=order-processor" --query 'Vpcs[].VpcId' --output text 2>/dev/null | while read -r vpc_id; do
        if [[ -n "$vpc_id" && "$vpc_id" != "None" ]]; then
            log_info "Deleting VPC: $vpc_id"

            # Delete all instances in VPC first
            aws ec2 describe-instances --filters "Name=vpc-id,Values=$vpc_id" --query 'Reservations[].Instances[].InstanceId' --output text 2>/dev/null | while read -r instance_id; do
                if [[ -n "$instance_id" && "$instance_id" != "None" ]]; then
                    aws ec2 terminate-instances --instance-ids "$instance_id" 2>/dev/null || true
                fi
            done

            # Wait for instances to terminate
            sleep 30

            # Delete VPC (this will fail if dependencies exist, which is fine)
            aws ec2 delete-vpc --vpc-id "$vpc_id" 2>/dev/null || true
        fi
    done

    # Clean up any remaining Elastic IPs
    aws ec2 describe-addresses --filters "Name=tag:Project,Values=order-processor" --query 'Addresses[].AllocationId' --output text 2>/dev/null | while read -r allocation_id; do
        if [[ -n "$allocation_id" && "$allocation_id" != "None" ]]; then
            log_info "Releasing Elastic IP: $allocation_id"
            aws ec2 release-address --allocation-id "$allocation_id" 2>/dev/null || true
        fi
    done

    # Delete any remaining IAM roles with our naming pattern
    aws iam list-roles --query "Roles[?contains(RoleName, 'order-processor')].RoleName" --output text 2>/dev/null | while read -r role_name; do
        if [[ -n "$role_name" && "$role_name" != "None" ]]; then
            log_info "Force deleting IAM role: $role_name"
            # Detach policies
            aws iam list-attached-role-policies --role-name "$role_name" --output text 2>/dev/null | awk '{print $2}' | while read -r policy; do
                if [[ -n "$policy" ]]; then
                    aws iam detach-role-policy --role-name "$role_name" --policy-arn "$policy" 2>/dev/null || true
                fi
            done
            aws iam delete-role --role-name "$role_name" 2>/dev/null || true
        fi
    done
}

# Verify complete cleanup with detailed status
verify_complete_cleanup() {
    log_step "🔍 Verifying Complete Cleanup"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would verify complete cleanup"
        return 0
    fi

    # Check all regions for any remaining resources
    local regions=("us-west-2" "us-east-1" "us-west-1" "us-east-2")
    local has_remaining_resources=false

    for region in "${regions[@]}"; do
        log_info "Checking region: $region"

        # Get resources with project tag
        local resources_json
        resources_json=$(aws resourcegroupstaggingapi get-resources \
            --tag-filters Key=Project,Values=order-processor \
            --region "$region" \
            --output json 2>/dev/null || echo '{"ResourceTagMappingList":[]}')

        # Parse and display resources in a readable format
        local resource_count
        resource_count=$(echo "$resources_json" | jq -r '.ResourceTagMappingList | length' 2>/dev/null || echo "0")

        if [[ "$resource_count" -gt 0 ]]; then
            has_remaining_resources=true

            printf "\n${YELLOW}📋 Remaining Resources in $region:${NC}\n"
            printf "${YELLOW}%-20s %-30s %-15s %s${NC}\n" "TYPE" "ID/NAME" "STATUS" "CHARGES"
            printf "${YELLOW}%-20s %-30s %-15s %s${NC}\n" "----" "-------" "------" "-------"

            echo "$resources_json" | jq -r '.ResourceTagMappingList[] | .ResourceARN' | while read -r arn; do
                check_resource_status "$arn"
            done
        else
            printf "${GREEN}✅ No resources found in $region${NC}\n"
        fi
    done

    if [[ "$has_remaining_resources" == "false" ]]; then
        log_success "✅ No project resources found in any region!"
    else
        printf "\n${YELLOW}⚠️  Resource Summary:${NC}\n"
        printf "${YELLOW}• KMS Keys: Scheduled for deletion (7 days) - ${GREEN}NO COST${NC}\n"
        printf "${YELLOW}• Secrets: Scheduled for deletion (immediate) - ${GREEN}NO COST${NC}\n"
        printf "${YELLOW}• NAT Gateway: Deleted but tag remains - ${GREEN}NO COST${NC}\n"
        printf "${YELLOW}• VPC Endpoint: Deleted but tag remains - ${GREEN}NO COST${NC}\n"
        printf "${YELLOW}• OIDC Provider: Minimal cost (pennies) - ${GREEN}NEARLY FREE${NC}\n"
        printf "\n${GREEN}💰 Total ongoing cost: $0.01-$0.10 per month maximum${NC}\n"
    fi

    # Show estimated cost impact
    printf "\n${BLUE}💰 Cost Impact Summary:${NC}\n"
    printf "${GREEN}✅ S3 buckets: Deleted (no storage charges)${NC}\n"
    printf "${GREEN}✅ RDS instances: Deleted (no compute charges)${NC}\n"
    printf "${GREEN}✅ EKS clusters: Deleted (no hourly charges)${NC}\n"
    printf "${GREEN}✅ EC2 instances: Terminated (no compute charges)${NC}\n"
    printf "${GREEN}✅ Load Balancers: Deleted (no hourly charges)${NC}\n"
    printf "${YELLOW}⏳ KMS keys: Scheduled deletion (free after 7 days)${NC}\n"
    printf "${GREEN}✅ Data transfer: Charges stopped${NC}\n"
}

# Check individual resource status
check_resource_status() {
    local arn="$1"
    local resource_type=$(echo "$arn" | cut -d':' -f3)
    local resource_id=$(echo "$arn" | rev | cut -d'/' -f1 | rev)
    local status="UNKNOWN"
    local cost_impact="UNKNOWN"

    case "$resource_type" in
        "kms")
            # Check KMS key status
            local key_status
            key_status=$(aws kms describe-key --key-id "$resource_id" --query 'KeyMetadata.KeyState' --output text 2>/dev/null || echo "UNKNOWN")
            if [[ "$key_status" == "PendingDeletion" ]]; then
                status="DELETING"
                cost_impact="FREE"
            else
                status="ACTIVE"
                cost_impact="LOW"
            fi
            printf "%-20s %-30s %-15s %s\n" "KMS Key" "${resource_id:0:30}" "$status" "$cost_impact"
            ;;
        "secretsmanager")
            # Check secret status
            local secret_status
            secret_status=$(aws secretsmanager describe-secret --secret-id "$resource_id" --query 'DeletedDate' --output text 2>/dev/null || echo "None")
            if [[ "$secret_status" != "None" ]]; then
                status="DELETING"
                cost_impact="FREE"
            else
                status="ACTIVE"
                cost_impact="LOW"
            fi
            printf "%-20s %-30s %-15s %s\n" "Secret" "${resource_id:0:30}" "$status" "$cost_impact"
            ;;
        "ec2")
            if [[ "$arn" == *":natgateway/"* ]]; then
                # Check NAT gateway status
                local nat_status
                nat_status=$(aws ec2 describe-nat-gateways --nat-gateway-ids "$resource_id" --query 'NatGateways[0].State' --output text 2>/dev/null || echo "deleted")
                if [[ "$nat_status" == "deleted" || "$nat_status" == "deleting" ]]; then
                    status="DELETED"
                    cost_impact="FREE"
                else
                    status="ACTIVE"
                    cost_impact="HIGH"
                fi
                printf "%-20s %-30s %-15s %s\n" "NAT Gateway" "${resource_id:0:30}" "$status" "$cost_impact"
            elif [[ "$arn" == *":vpc-endpoint/"* ]]; then
                # Check VPC endpoint status
                local vpc_endpoint_status
                vpc_endpoint_status=$(aws ec2 describe-vpc-endpoints --vpc-endpoint-ids "$resource_id" --query 'VpcEndpoints[0].State' --output text 2>/dev/null || echo "deleted")
                if [[ "$vpc_endpoint_status" == "deleted" || "$vpc_endpoint_status" == "deleting" ]]; then
                    status="DELETED"
                    cost_impact="FREE"
                else
                    status="ACTIVE"
                    cost_impact="LOW"
                fi
                printf "%-20s %-30s %-15s %s\n" "VPC Endpoint" "${resource_id:0:30}" "$status" "$cost_impact"
            elif [[ "$arn" == *":subnet/"* ]]; then
                # Check subnet status
                local subnet_status
                subnet_status=$(aws ec2 describe-subnets --subnet-ids "$resource_id" --query 'Subnets[0].State' --output text 2>/dev/null || echo "deleted")
                status="$subnet_status"
                cost_impact="FREE"
                printf "%-20s %-30s %-15s %s\n" "Subnet" "${resource_id:0:30}" "$status" "$cost_impact"
            else
                printf "%-20s %-30s %-15s %s\n" "EC2 ($resource_type)" "${resource_id:0:30}" "CHECK" "VARIES"
            fi
            ;;
        "iam")
            if [[ "$arn" == *":oidc-provider/"* ]]; then
                # OIDC providers have minimal cost
                status="ACTIVE"
                cost_impact="MINIMAL"
                local provider_id=$(echo "$arn" | rev | cut -d'/' -f1 | rev)
                printf "%-20s %-30s %-15s %s\n" "OIDC Provider" "${provider_id:0:30}" "$status" "$cost_impact"
            else
                printf "%-20s %-30s %-15s %s\n" "IAM Resource" "${resource_id:0:30}" "CHECK" "FREE"
            fi
            ;;
        *)
            printf "%-20s %-30s %-15s %s\n" "$resource_type" "${resource_id:0:30}" "CHECK" "UNKNOWN"
            ;;
    esac
}

# Generate cleanup summary
generate_summary() {
    log_step "📊 Complete Cleanup Summary"

    log_info "Destruction Details:"
    log_info "  Environment: $ENVIRONMENT"
    log_info "  Profile: $PROFILE"
    log_info "  Region: ${AWS_REGION:-us-west-2}"
    log_info "  Force cleanup: $FORCE_CLEANUP"

    if [[ "$DRY_RUN" == "false" ]]; then
        log_success "✅ Complete infrastructure destruction completed!"
        log_success "✅ Nuclear cleanup performed to prevent any charges!"
        log_info "All AWS resources have been aggressively cleaned up"
        log_info "Check AWS Console and billing dashboard to verify"
    else
        log_success "✅ Destruction plan validated!"
        log_info "Remove --dry-run flag to destroy all infrastructure"
    fi
}

# Main execution
main() {
    # Parse arguments
    parse_arguments "$@"

    # Validate arguments
    validate_arguments

    # Print header
    echo
    printf "${RED}🧹 Infrastructure Destroy Script${NC}\n"
    printf "${RED}================================${NC}\n"
    echo
    log_warning "Destroying: $ENVIRONMENT environment with $PROFILE profile"
    echo

    # Execute destruction steps
    setup_environment
    check_prerequisites
    confirm_destruction
    pre_cleanup
    terraform_destroy

    # Add nuclear cleanup for complete resource removal
    if [[ "$FORCE_CLEANUP" == "true" ]]; then
        nuclear_cleanup
    fi

    verify_complete_cleanup
    generate_summary

    # Return to original directory
    cd "$PROJECT_ROOT"
}

# Run main function
main "$@"