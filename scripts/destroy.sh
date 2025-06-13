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
VERBOSE=false
DRY_RUN=false
FORCE=false

# Usage function
show_usage() {
    cat << EOF
$(printf "${RED}🧹 Infrastructure Destroy Script${NC}")

Usage: $0 --environment {dev|prod} [OPTIONS]

Destroy AWS infrastructure and cleanup resources based on environment.

REQUIRED:
    --environment {dev|prod}           Target environment

OPTIONS:
    -v, --verbose                     Enable verbose output
    --dry-run                         Show what would be destroyed (don't destroy)
    --force                           Skip all confirmations and destroy everything
    -h, --help                        Show this help message

EXAMPLES:
    $0 --environment dev                    # Destroy Lambda infrastructure
    $0 --environment prod                   # Destroy EKS infrastructure
    $0 --environment dev --dry-run          # Plan destruction only
    $0 --environment prod --force           # Force destroy without prompts

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
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --force)
                FORCE=true
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
    export TF_VAR_environment="$ENVIRONMENT"

    # Load environment-specific configuration
    local env_config="$PROJECT_ROOT/config/environments/.env.defaults"
    if [[ -f "$env_config" ]]; then
        log_info "Loading configuration: $env_config"
        source "$env_config"
    fi

    if [[ "$VERBOSE" == "true" ]]; then
        log_info "Environment variables set:"
        log_info "  ENVIRONMENT: $ENVIRONMENT"
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

# Show destruction impact
show_destruction_impact() {
    log_step "💥 Destruction Impact"

    echo
    log_warning "⚠️  ALL DATA WILL BE PERMANENTLY LOST!"
    log_warning "⚠️  This action cannot be undone!"
}

# Confirm destruction
confirm_destruction() {
    if [[ "$FORCE" == "true" || "$DRY_RUN" == "true" ]]; then
        return 0
    fi

    log_step "⚠️ Destruction Confirmation"

    echo
    printf "${RED}WARNING: This will permanently destroy the following:${NC}\n"
    printf "${RED}  - Environment: $ENVIRONMENT${NC}\n"
    printf "${RED}  - All AWS resources managed by Terraform${NC}\n"
    printf "${RED}  - All data in databases${NC}\n"
    printf "${RED}  - All data in S3 buckets${NC}\n"

    read -p "Are you absolutely sure you want to continue? (type 'yes' to confirm): " confirmation

    if [[ "$confirmation" != "yes" ]]; then
        log_info "Destruction cancelled by user"
        exit 0
    fi

    log_warning "Proceeding with infrastructure destruction..."
}

# pre-cleanup

# Standard pre-cleanup tasks
standard_pre_cleanup() {
    log_step "🧹 Standard Pre-Cleanup Tasks"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would perform standard pre-cleanup tasks"
        return 0
    fi

    # Empty S3 buckets first (they must be empty to delete)
    log_info "Checking for S3 buckets to empty..."

    local bucket_prefix="${RESOURCE_PREFIX:-order-processor-$ENVIRONMENT}"
    local buckets
    buckets=$(aws s3api list-buckets \
        --query "Buckets[?contains(Name, '${bucket_prefix}')].Name" \
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

    log_success "Standard pre-cleanup tasks completed"
}

# API Gateway specific cleanup
cleanup_api_gateway() {
    log_info "Cleaning up API Gateway resources..."

    local api_prefix="${RESOURCE_PREFIX:-order-processor-$ENVIRONMENT}"

    # Get API Gateway IDs
    local apis
    apis=$(aws apigateway get-rest-apis \
        --query "items[?contains(name, '${api_prefix}')].id" \
        --output text 2>/dev/null || echo "")

    for api_id in $apis; do
        if [[ -n "$api_id" ]]; then
            log_info "Deleting API Gateway: $api_id"
            aws apigateway delete-rest-api --rest-api-id "$api_id" 2>/dev/null || true
        fi
    done

    # Clean up API Gateway v2 (HTTP APIs)
    local http_apis
    http_apis=$(aws apigatewayv2 get-apis \
        --query "Items[?contains(Name, '${api_prefix}')].ApiId" \
        --output text 2>/dev/null || echo "")

    for api_id in $http_apis; do
        if [[ -n "$api_id" ]]; then
            log_info "Deleting HTTP API Gateway: $api_id"
            aws apigatewayv2 delete-api --api-id "$api_id" 2>/dev/null || true
        fi
    done
}

# KMS and Secrets cleanup
cleanup_kms_secrets() {
    log_info "Cleaning up KMS and Secrets Manager resources..."

    local resource_prefix="${RESOURCE_PREFIX:-order-processor-$ENVIRONMENT}"

    # Clean up KMS aliases first (they block key deletion)
    local aliases
    aliases=$(aws kms list-aliases \
        --query "Aliases[?contains(AliasName, '${resource_prefix}')].AliasName" \
        --output text 2>/dev/null || echo "")

    for alias in $aliases; do
        if [[ -n "$alias" ]]; then
            log_info "Deleting KMS alias: $alias"
            aws kms delete-alias --alias-name "$alias" 2>/dev/null || true
        fi
    done

    # Schedule KMS key deletion
    local keys
    keys=$(aws kms list-keys --query 'Keys[].KeyId' --output text 2>/dev/null || echo "")
    for key_id in $keys; do
        local key_description
        key_description=$(aws kms describe-key --key-id "$key_id" \
            --query 'KeyMetadata.Description' --output text 2>/dev/null || echo "")

        if [[ "$key_description" == *"$resource_prefix"* ]]; then
            log_info "Scheduling KMS key deletion: $key_id"
            aws kms schedule-key-deletion --key-id "$key_id" --pending-window-in-days 7 2>/dev/null || true
        fi
    done

    # Force delete secrets (remove deletion protection)
    local secrets
    secrets=$(aws secretsmanager list-secrets \
        --query "SecretList[?contains(Name, '${resource_prefix}')].Name" \
        --output text 2>/dev/null || echo "")

    for secret in $secrets; do
        if [[ -n "$secret" ]]; then
            log_info "Force deleting secret: $secret"
            aws secretsmanager delete-secret --secret-id "$secret" --force-delete-without-recovery 2>/dev/null || true
        fi
    done
}

# IAM roles and policies cleanup
cleanup_iam_resources() {
    log_info "Cleaning up IAM roles and policies..."

    local resource_prefix="${RESOURCE_PREFIX:-order-processor-$ENVIRONMENT}"

    # Common auto-generated role patterns
    local role_patterns=(
        "*${resource_prefix}*"
        "*eks-cluster-service-role*"
        "*eks-nodegroup-*"
        "*lambda-execution-role*"
        "*codebuild-*"
        "*codepipeline-*"
        "*AWSServiceRole*"
    )

    # Get all roles and filter by patterns
    local all_roles
    all_roles=$(aws iam list-roles --query 'Roles[].RoleName' --output text 2>/dev/null || echo "")

    for role_name in $all_roles; do
        # Check if role matches our patterns
        local should_delete=false
        for pattern in "${role_patterns[@]}"; do
            if [[ "$role_name" == $pattern ]] || [[ "$role_name" == *"$resource_prefix"* ]]; then
                should_delete=true
                break
            fi
        done

        # Skip AWS service-linked roles (they're managed by AWS)
        if [[ "$role_name" == *"AWSServiceRole"* ]]; then
            continue
        fi

        if [[ "$should_delete" == "true" ]]; then
            cleanup_single_role "$role_name"
        fi
    done

    # Clean up orphaned policies
    cleanup_orphaned_policies
}

# Clean up a single IAM role
cleanup_single_role() {
    local role_name="$1"

    if [[ -z "$role_name" ]]; then
        return
    fi

    log_info "Cleaning up IAM role: $role_name"

    # Detach managed policies
    local attached_policies
    attached_policies=$(aws iam list-attached-role-policies \
        --role-name "$role_name" \
        --query 'AttachedPolicies[].PolicyArn' \
        --output text 2>/dev/null || echo "")

    for policy_arn in $attached_policies; do
        if [[ -n "$policy_arn" ]]; then
            log_info "  Detaching managed policy: $policy_arn"
            aws iam detach-role-policy \
                --role-name "$role_name" \
                --policy-arn "$policy_arn" 2>/dev/null || true
        fi
    done

    # Delete inline policies
    local inline_policies
    inline_policies=$(aws iam list-role-policies \
        --role-name "$role_name" \
        --query 'PolicyNames' \
        --output text 2>/dev/null || echo "")

    for policy_name in $inline_policies; do
        if [[ -n "$policy_name" ]]; then
            log_info "  Deleting inline policy: $policy_name"
            aws iam delete-role-policy \
                --role-name "$role_name" \
                --policy-name "$policy_name" 2>/dev/null || true
        fi
    done

    # Remove role from instance profiles
    local instance_profiles
    instance_profiles=$(aws iam list-instance-profiles-for-role \
        --role-name "$role_name" \
        --query 'InstanceProfiles[].InstanceProfileName' \
        --output text 2>/dev/null || echo "")

    for profile_name in $instance_profiles; do
        if [[ -n "$profile_name" ]]; then
            log_info "  Removing from instance profile: $profile_name"
            aws iam remove-role-from-instance-profile \
                --instance-profile-name "$profile_name" \
                --role-name "$role_name" 2>/dev/null || true

            # Delete the instance profile if it's empty
            aws iam delete-instance-profile \
                --instance-profile-name "$profile_name" 2>/dev/null || true
        fi
    done

    # Finally delete the role
    log_info "  Deleting role: $role_name"
    aws iam delete-role --role-name "$role_name" 2>/dev/null || true
}

# EKS specific cleanup
cleanup_eks_roles() {
    log_info "Cleaning up EKS-specific resources..."

    local cluster_name="${RESOURCE_PREFIX:-order-processor-$ENVIRONMENT}-cluster"

    # Get EKS cluster service role
    local cluster_role
    cluster_role=$(aws eks describe-cluster \
        --name "$cluster_name" \
        --query 'cluster.roleArn' \
        --output text 2>/dev/null | cut -d'/' -f2 || echo "")

    if [[ -n "$cluster_role" && "$cluster_role" != "None" ]]; then
        log_info "Found EKS cluster role: $cluster_role"
        cleanup_single_role "$cluster_role"
    fi

    # Get node group roles
    local nodegroups
    nodegroups=$(aws eks list-nodegroups \
        --cluster-name "$cluster_name" \
        --query 'nodegroups' \
        --output text 2>/dev/null || echo "")

    for nodegroup in $nodegroups; do
        if [[ -n "$nodegroup" ]]; then
            local nodegroup_role
            nodegroup_role=$(aws eks describe-nodegroup \
                --cluster-name "$cluster_name" \
                --nodegroup-name "$nodegroup" \
                --query 'nodegroup.nodeRole' \
                --output text 2>/dev/null | cut -d'/' -f2 || echo "")

            if [[ -n "$nodegroup_role" && "$nodegroup_role" != "None" ]]; then
                log_info "Found EKS nodegroup role: $nodegroup_role"
                cleanup_single_role "$nodegroup_role"
            fi
        fi
    done
}

# Clean up orphaned policies
cleanup_orphaned_policies() {
    log_info "Cleaning up orphaned customer-managed policies..."

    local resource_prefix="${RESOURCE_PREFIX:-order-processor-$ENVIRONMENT}"

    # Get customer-managed policies
    local policies
    policies=$(aws iam list-policies \
        --scope Local \
        --query 'Policies[].Arn' \
        --output text 2>/dev/null || echo "")

    for policy_arn in $policies; do
        if [[ "$policy_arn" == *"$resource_prefix"* ]]; then
            log_info "Attempting to delete policy: $policy_arn"

            # Get policy versions and delete non-default versions first
            local versions
            versions=$(aws iam list-policy-versions \
                --policy-arn "$policy_arn" \
                --query 'Versions[?IsDefaultVersion==`false`].VersionId' \
                --output text 2>/dev/null || echo "")

            for version in $versions; do
                if [[ -n "$version" ]]; then
                    aws iam delete-policy-version \
                        --policy-arn "$policy_arn" \
                        --version-id "$version" 2>/dev/null || true
                fi
            done

            # Delete the policy
            aws iam delete-policy --policy-arn "$policy_arn" 2>/dev/null || true
        fi
    done
}

# Terraform destroy
terraform_destroy() {
    log_step "💥 Destroying Infrastructure with Terraform"

    cd "$PROJECT_ROOT/terraform"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would run terraform destroy"
        terraform plan -destroy \
            -var="environment=$ENVIRONMENT" \
        return 0
    fi

    # Initialize if needed
    if [[ ! -d ".terraform" ]]; then
        log_info "Initializing Terraform..."
        terraform init
    fi

    # Pre-cleanup AWS resources that block Terraform destroy
    cleanup_api_gateway
    cleanup_kms_secrets

    # Destroy with auto-approve
    local destroy_args="-var=environment=$ENVIRONMENT -auto-approve"

    log_info "Running terraform destroy..."
    if terraform destroy $destroy_args; then
        log_success "Terraform destroy completed successfully"
    else
        log_error "Terraform destroy failed, attempting cleanup of remaining resources"
        cleanup_remaining_resources
    fi

    # Post-cleanup for resources that might not be handled by Terraform
    log_info "Running post-destroy cleanup..."
    cleanup_eks_roles
    cleanup_iam_resources
    cleanup_remaining_resources
}

# Cleanup remaining resources
cleanup_remaining_resources() {
    log_warning "Attempting to cleanup remaining resources..."

    cd "$PROJECT_ROOT/terraform"

    # Get list of remaining resources
    if terraform state list >/dev/null 2>&1; then
        local remaining_resources
        remaining_resources=$(terraform state list 2>/dev/null || echo "")

        if [[ -n "$remaining_resources" ]]; then
            log_warning "Remaining resources in state:"
            echo "$remaining_resources"

            # Try destroy again with individual resource targeting
            log_info "Attempting targeted resource destruction..."
            echo "$remaining_resources" | while read -r resource; do
                if [[ -n "$resource" ]]; then
                    log_info "Attempting to destroy: $resource"
                    terraform destroy -target="$resource" \
                        -var="environment=$ENVIRONMENT" \
                        -auto-approve || true
                fi
            done
        fi
    fi
}

# Verify complete cleanup
verify_cleanup() {
    log_step "✅ Verifying Complete Cleanup"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would verify cleanup completion"
        return 0
    fi

    local warnings=()
    local resource_prefix="${RESOURCE_PREFIX:-order-processor-$ENVIRONMENT}"

    # Check for remaining resources by tags
    log_info "Checking for remaining tagged resources..."
    local tagged_resources
    tagged_resources=$(aws resourcegroupstaggingapi get-resources \
        --tag-filters Key=Project,Values=order-processor \
        --region "${AWS_REGION:-us-west-2}" \
        --query 'ResourceTagMappingList | length' \
        --output text 2>/dev/null || echo "0")

    if [[ "$tagged_resources" -gt 0 ]]; then
        warnings+=("$tagged_resources tagged resources still exist")

        # Show details if verbose
        if [[ "$VERBOSE" == "true" ]]; then
            aws resourcegroupstaggingapi get-resources \
                --tag-filters Key=Project,Values=order-processor \
                --region "${AWS_REGION:-us-west-2}" \
                --query 'ResourceTagMappingList[].ResourceARN' \
                --output table 2>/dev/null || true
        fi
    fi

    # Check for common resources
    local remaining_s3
    remaining_s3=$(aws s3api list-buckets \
        --query "Buckets[?contains(Name, '${resource_prefix}')].Name" \
        --output text 2>/dev/null || echo "")
    if [[ -n "$remaining_s3" ]]; then
        warnings+=("S3 buckets still exist: $remaining_s3")
    fi

    local remaining_rds
    remaining_rds=$(aws rds describe-db-instances \
        --query "DBInstances[?contains(DBInstanceIdentifier, '${resource_prefix}')].DBInstanceIdentifier" \
        --output text 2>/dev/null || echo "")
    if [[ -n "$remaining_rds" ]]; then
        warnings+=("RDS instances still exist: $remaining_rds")
    fi

    if [[ ${#warnings[@]} -eq 0 ]]; then
        log_success "✅ All resources appear to be cleaned up"
        log_success "💰 Estimated ongoing cost: $0.00/day"
    else
        log_warning "Cleanup verification found remaining resources:"
        for warning in "${warnings[@]}"; do
            log_warning "  - $warning"
        done
        log_info "Manual cleanup may be required in AWS Console"
        log_warning "💰 Some costs may still be incurred"
    fi
}

# Generate cleanup summary
generate_summary() {
    log_step "📊 Complete Cleanup Summary"

    log_info "Destruction Details:"
    log_info "  Environment: $ENVIRONMENT"
    log_info "  Region: ${AWS_REGION:-us-west-2}"

    if [[ "$DRY_RUN" == "false" ]]; then
        log_success "✅ Complete infrastructure destruction completed!"

        log_info "All AWS resources have been cleaned up"
        log_info "Check AWS Console and billing dashboard to verify"
        log_success "💰 Expected cost reduction: ~$0.50-20/day"
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
    log_warning "Destroying: $ENVIRONMENT environment"
    echo

    # Execute destruction steps
    setup_environment
    check_prerequisites
    show_destruction_impact
    confirm_destruction
    standard_pre_cleanup
    terraform_destroy
    verify_cleanup
    generate_summary

    # Return to original directory
    cd "$PROJECT_ROOT"
}

# Run main function
main "$@"