#!/bin/bash
# scripts/destroy.sh
# Simplified Infrastructure Cleanup Script
# Destroys ALL AWS resources for this project only

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

Destroy ALL AWS resources for this project only.

REQUIRED:
    --environment {dev|prod}           Target environment

OPTIONS:
    -v, --verbose                     Enable verbose output
    --dry-run                         Show what would be destroyed (don't destroy)
    --force                           Skip all confirmations and destroy everything
    -h, --help                        Show this help message

EXAMPLES:
    $0 --environment dev                    # Destroy dev infrastructure
    $0 --environment prod                   # Destroy prod infrastructure
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
    if [[ -z "$ENVIRONMENT" ]]; then
        log_error "--environment is required"
        show_usage
        exit 1
    fi

    if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
        log_error "--environment must be 'dev' or 'prod'"
        show_usage
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking Prerequisites"

    # Check required tools
    local missing_tools=()
    local tools=("terraform" "aws")
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
    if [[ "$FORCE" == "true" || "$DRY_RUN" == "true" ]]; then
        return 0
    fi

    log_step "Destruction Confirmation"

    echo
    printf "${RED}WARNING: This will permanently destroy:${NC}\n"
    printf "${RED}  - Environment: $ENVIRONMENT${NC}\n"
    printf "${RED}  - All AWS resources managed by Terraform${NC}\n"
    printf "${RED}  - All data in databases${NC}\n"
    printf "${RED}  - All data in S3 buckets${NC}\n"
    printf "${RED}  - All EKS clusters and node groups${NC}\n"
    printf "${RED}  - All IAM roles and policies for this project${NC}\n"

    read -p "Are you absolutely sure you want to continue? (type 'yes' to confirm): " confirmation

    if [[ "$confirmation" != "yes" ]]; then
        log_info "Destruction cancelled by user"
        exit 0
    fi

    log_warning "Proceeding with infrastructure destruction..."
}

# Pre-cleanup: Empty S3 buckets
pre_cleanup_s3() {
    log_step "Pre-cleanup: Emptying S3 Buckets"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would empty S3 buckets"
        return 0
    fi

    local resource_prefix="order-processor-$ENVIRONMENT"
    local buckets
    buckets=$(aws s3api list-buckets \
        --query "Buckets[?contains(Name, '${resource_prefix}')].Name" \
        --output text 2>/dev/null || echo "")

    if [[ -n "$buckets" ]]; then
        for bucket in $buckets; do
            log_info "Emptying S3 bucket: $bucket"
            aws s3 rm "s3://$bucket" --recursive 2>/dev/null || true
        done
    fi
}

# Pre-cleanup: Delete KMS aliases and secrets
pre_cleanup_kms_secrets() {
    log_step "Pre-cleanup: KMS and Secrets"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would cleanup KMS and secrets"
        return 0
    fi

    local resource_prefix="order-processor-$ENVIRONMENT"

    # Delete KMS aliases
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

    # Force delete secrets
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

# Pre-cleanup: IAM roles and policies
pre_cleanup_iam() {
    log_step "Pre-cleanup: IAM Resources"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would cleanup IAM resources"
        return 0
    fi

    local resource_prefix="order-processor-$ENVIRONMENT"

    # Get all roles and filter by our prefix
    local all_roles
    all_roles=$(aws iam list-roles --query 'Roles[].RoleName' --output text 2>/dev/null || echo "")

    for role_name in $all_roles; do
        # Skip AWS service-linked roles
        if [[ "$role_name" == *"AWSServiceRole"* ]]; then
            continue
        fi

        # Check if role matches our project
        if [[ "$role_name" == *"$resource_prefix"* ]]; then
            log_info "Cleaning up IAM role: $role_name"

            # Detach managed policies
            local attached_policies
            attached_policies=$(aws iam list-attached-role-policies \
                --role-name "$role_name" \
                --query 'AttachedPolicies[].PolicyArn' \
                --output text 2>/dev/null || echo "")

            for policy_arn in $attached_policies; do
                if [[ -n "$policy_arn" ]]; then
                    aws iam detach-role-policy --role-name "$role_name" --policy-arn "$policy_arn" 2>/dev/null || true
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
                    aws iam delete-role-policy --role-name "$role_name" --policy-name "$policy_name" 2>/dev/null || true
                fi
            done

            # Delete the role
            aws iam delete-role --role-name "$role_name" 2>/dev/null || true
        fi
    done

    # Clean up customer-managed policies
    local policies
    policies=$(aws iam list-policies \
        --scope Local \
        --query 'Policies[].Arn' \
        --output text 2>/dev/null || echo "")

    for policy_arn in $policies; do
        if [[ "$policy_arn" == *"$resource_prefix"* ]]; then
            log_info "Deleting policy: $policy_arn"
            aws iam delete-policy --policy-arn "$policy_arn" 2>/dev/null || true
        fi
    done
}

# Terraform destroy
terraform_destroy() {
    log_step "Destroying Infrastructure with Terraform"

    cd "$PROJECT_ROOT/terraform"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would run terraform destroy"
        terraform plan -destroy -var="environment=$ENVIRONMENT"
        return 0
    fi

    # Initialize if needed
    if [[ ! -d ".terraform" ]]; then
        log_info "Initializing Terraform..."
        terraform init
    fi

    # Destroy with auto-approve
    log_info "Running terraform destroy..."
    if terraform destroy -var="environment=$ENVIRONMENT" -auto-approve; then
        log_success "Terraform destroy completed successfully"
    else
        log_error "Terraform destroy failed"
        return 1
    fi
}

# Verify cleanup
verify_cleanup() {
    log_step "Verifying Complete Cleanup"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would verify cleanup"
        return 0
    fi

    local resource_prefix="order-processor-$ENVIRONMENT"
    local warnings=()

    # Check for remaining S3 buckets
    local remaining_s3
    remaining_s3=$(aws s3api list-buckets \
        --query "Buckets[?contains(Name, '${resource_prefix}')].Name" \
        --output text 2>/dev/null || echo "")
    if [[ -n "$remaining_s3" ]]; then
        warnings+=("S3 buckets still exist: $remaining_s3")
    fi

    # Check for remaining RDS instances
    local remaining_rds
    remaining_rds=$(aws rds describe-db-instances \
        --query "DBInstances[?contains(DBInstanceIdentifier, '${resource_prefix}')].DBInstanceIdentifier" \
        --output text 2>/dev/null || echo "")
    if [[ -n "$remaining_rds" ]]; then
        warnings+=("RDS instances still exist: $remaining_rds")
    fi

    # Check for remaining EKS clusters
    local remaining_eks
    remaining_eks=$(aws eks list-clusters \
        --query "clusters[?contains(@, '${resource_prefix}')]" \
        --output text 2>/dev/null || echo "")
    if [[ -n "$remaining_eks" ]]; then
        warnings+=("EKS clusters still exist: $remaining_eks")
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
    fi
}

# Main execution
main() {
    parse_arguments "$@"
    validate_arguments

    echo
    printf "${RED}🧹 Infrastructure Destroy Script${NC}\n"
    printf "${RED}================================${NC}\n"
    echo
    log_warning "Destroying: $ENVIRONMENT environment"
    echo

    check_prerequisites
    confirm_destruction
    pre_cleanup_s3
    pre_cleanup_kms_secrets
    pre_cleanup_iam
    terraform_destroy
    verify_cleanup

    log_success "✅ Infrastructure destruction completed!"
    log_info "Check AWS Console and billing dashboard to verify"
    log_success "💰 Expected cost reduction: ~$0.50-20/day"

    cd "$PROJECT_ROOT"
}

# Run main function
main "$@"