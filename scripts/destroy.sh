#!/bin/bash
# scripts/destroy.sh
# Infrastructure Cleanup Script with Profile Support
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
FORCE=false

# Usage function
show_usage() {
    cat << EOF
$(printf "${RED}🧹 Infrastructure Destroy Script${NC}")

Usage: $0 --environment {dev|prod} --profile {minimum|regular} [OPTIONS]

Destroy AWS infrastructure and cleanup resources based on profile.

REQUIRED:
    --environment {dev|prod}           Target environment
    --profile {minimum|regular}        Resource profile

PROFILES:
    minimum    - Destroy Lambda + API Gateway infrastructure
    regular    - Destroy EKS + Kubernetes infrastructure

OPTIONS:
    -v, --verbose                     Enable verbose output
    --dry-run                         Show what would be destroyed (don't destroy)
    --force                           Skip all confirmations and destroy everything
    -h, --help                        Show this help message

EXAMPLES:
    $0 --environment dev --profile minimum                    # Destroy Lambda infrastructure
    $0 --environment dev --profile regular                    # Destroy EKS infrastructure
    $0 --environment dev --profile minimum --dry-run          # Plan destruction only
    $0 --environment dev --profile regular --force            # Force destroy without prompts

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

    if [[ -z "$PROFILE" ]]; then
        errors+=("--profile is required")
    elif [[ "$PROFILE" != "minimum" && "$PROFILE" != "regular" ]]; then
        errors+=("--profile must be 'minimum' or 'regular'")
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
    export PROFILE="$PROFILE"
    export TF_VAR_environment="$ENVIRONMENT"
    export TF_VAR_profile="$PROFILE"

    # Profile-specific settings
    case "$PROFILE" in
        "minimum")
            export TF_VAR_compute_type="lambda"
            ;;
        "regular")
            export TF_VAR_compute_type="kubernetes"
            ;;
    esac

    # Load environment-specific configuration
    local env_config="$PROJECT_ROOT/config/environments/.env.defaults"
    if [[ -f "$env_config" ]]; then
        log_info "Loading configuration: $env_config"
        source "$env_config"
    fi

    if [[ "$VERBOSE" == "true" ]]; then
        log_info "Environment variables set:"
        log_info "  ENVIRONMENT: $ENVIRONMENT"
        log_info "  PROFILE: $PROFILE"
        log_info "  COMPUTE_TYPE: ${TF_VAR_compute_type}"
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

    case "$PROFILE" in
        "minimum")
            log_info "Lambda + API Gateway Profile will destroy:"
            log_info "  🗑️ Lambda function and versions"
            log_info "  🗑️ API Gateway REST API"
            log_info "  🗑️ IAM roles and policies"
            log_info "  🗑️ CloudWatch logs"
            log_info "  🗑️ RDS database and snapshots"
            log_info "  🗑️ SNS topics and SQS queues"
            log_info "  🗑️ S3 buckets and contents"
            log_success "✅ Cost after destruction: $0.00/day"
            ;;
        "regular")
            log_warning "EKS + Kubernetes Profile will destroy:"
            log_warning "  🗑️ EKS cluster and node groups"
            log_warning "  🗑️ All Kubernetes workloads"
            log_warning "  🗑️ Load balancers and networking"
            log_warning "  🗑️ ECR repositories and images"
            log_warning "  🗑️ RDS database and snapshots"
            log_warning "  🗑️ SNS topics and SQS queues"
            log_warning "  🗑️ S3 buckets and contents"
            log_warning "  🗑️ All persistent volumes"
            log_success "✅ Cost after destruction: $0.00/day"
            ;;
    esac

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
    printf "${RED}  - Profile: $PROFILE${NC}\n"
    printf "${RED}  - All AWS resources managed by Terraform${NC}\n"
    printf "${RED}  - All data in databases${NC}\n"
    printf "${RED}  - All data in S3 buckets${NC}\n"

    case "$PROFILE" in
        "minimum")
            printf "${RED}  - Lambda function and API Gateway${NC}\n"
            ;;
        "regular")
            printf "${RED}  - EKS cluster and all applications${NC}\n"
            ;;
    esac
    echo

    read -p "Are you absolutely sure you want to continue? (type 'yes' to confirm): " confirmation

    if [[ "$confirmation" != "yes" ]]; then
        log_info "Destruction cancelled by user"
        exit 0
    fi

    log_warning "Proceeding with infrastructure destruction..."
}

# Profile-specific pre-cleanup
profile_specific_cleanup() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would perform profile-specific cleanup"
        return 0
    fi

    log_step "🧹 Profile-Specific Pre-Cleanup"

    case "$PROFILE" in
        "minimum")
            # Lambda-specific cleanup
            log_info "Cleaning up Lambda-specific resources..."

            # Clean up Lambda layers if any
            local function_name="${RESOURCE_PREFIX:-order-processor-$ENVIRONMENT}-order-api"
            if aws lambda get-function --function-name "$function_name" --region "${AWS_REGION:-us-west-2}" >/dev/null 2>&1; then
                log_info "Found Lambda function: $function_name"
                # Terraform will handle deletion
            fi

            # Clean up API Gateway custom domains if any
            local api_name="${RESOURCE_PREFIX:-order-processor-$ENVIRONMENT}-api"
            log_info "Checking for API Gateway: $api_name"
            ;;

        "regular")
            # Kubernetes-specific cleanup
            log_info "Cleaning up Kubernetes-specific resources..."

            # Check if kubectl is available and cluster exists
            if command -v kubectl >/dev/null 2>&1; then
                local cluster_name="${RESOURCE_PREFIX:-order-processor-$ENVIRONMENT}-cluster"

                # Try to connect to cluster
                if aws eks update-kubeconfig --region "${AWS_REGION:-us-west-2}" --name "$cluster_name" >/dev/null 2>&1; then
                    log_info "Connected to EKS cluster: $cluster_name"

                    # Delete all resources in order-processor namespace
                    if kubectl get namespace order-processor >/dev/null 2>&1; then
                        log_info "Deleting Kubernetes namespace: order-processor"
                        kubectl delete namespace order-processor --wait=false || true
                    fi

                    # Delete any LoadBalancer services to free up ELBs
                    log_info "Cleaning up LoadBalancer services..."
                    kubectl get services --all-namespaces -o json | \
                    jq -r '.items[] | select(.spec.type=="LoadBalancer") | "\(.metadata.namespace) \(.metadata.name)"' | \
                    while read -r namespace service; do
                        if [[ -n "$namespace" && -n "$service" ]]; then
                            kubectl delete service "$service" -n "$namespace" --wait=false || true
                        fi
                    done
                else
                    log_info "Could not connect to EKS cluster (may already be deleted)"
                fi
            fi

            # Clean up ECR repositories
            local ecr_repo="${RESOURCE_PREFIX:-order-processor-$ENVIRONMENT}-order-api"
            if aws ecr describe-repositories --repository-names "$ecr_repo" --region "${AWS_REGION:-us-west-2}" >/dev/null 2>&1; then
                log_info "Cleaning up ECR repository: $ecr_repo"
                aws ecr delete-repository --repository-name "$ecr_repo" --region "${AWS_REGION:-us-west-2}" --force || true
            fi
            ;;
    esac

    log_success "Profile-specific cleanup completed"
}

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

# Terraform destroy
terraform_destroy() {
    log_step "💥 Destroying Infrastructure with Terraform"

    cd "$PROJECT_ROOT/terraform"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would run terraform destroy"
        terraform plan -destroy \
            -var="profile=$PROFILE" \
            -var="environment=$ENVIRONMENT" \
            -var="compute_type=${TF_VAR_compute_type}"
        return 0
    fi

    # Initialize if needed
    if [[ ! -d ".terraform" ]]; then
        log_info "Initializing Terraform..."
        terraform init
    fi

    # Destroy with auto-approve
    local destroy_args="-var=profile=$PROFILE -var=environment=$ENVIRONMENT -var=compute_type=${TF_VAR_compute_type} -auto-approve"

    log_info "Running terraform destroy..."
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
                        -var="profile=$PROFILE" \
                        -var="environment=$ENVIRONMENT" \
                        -var="compute_type=${TF_VAR_compute_type}" \
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

    # Profile-specific checks
    case "$PROFILE" in
        "minimum")
            # Check for Lambda functions
            local lambda_functions
            lambda_functions=$(aws lambda list-functions \
                --query "Functions[?contains(FunctionName, '${resource_prefix}')].FunctionName" \
                --output text 2>/dev/null || echo "")
            if [[ -n "$lambda_functions" ]]; then
                warnings+=("Lambda functions still exist: $lambda_functions")
            fi

            # Check for API Gateways
            local api_gateways
            api_gateways=$(aws apigateway get-rest-apis \
                --query "items[?contains(name, '${resource_prefix}')].name" \
                --output text 2>/dev/null || echo "")
            if [[ -n "$api_gateways" ]]; then
                warnings+=("API Gateways still exist: $api_gateways")
            fi
            ;;

        "regular")
            # Check for EKS clusters
            local eks_clusters
            eks_clusters=$(aws eks list-clusters \
                --query "clusters[?contains(@, '${resource_prefix}')]" \
                --output text 2>/dev/null || echo "")
            if [[ -n "$eks_clusters" ]]; then
                warnings+=("EKS clusters still exist: $eks_clusters")
            fi

            # Check for ECR repositories
            local ecr_repos
            ecr_repos=$(aws ecr describe-repositories \
                --query "repositories[?contains(repositoryName, '${resource_prefix}')].repositoryName" \
                --output text 2>/dev/null || echo "")
            if [[ -n "$ecr_repos" ]]; then
                warnings+=("ECR repositories still exist: $ecr_repos")
            fi
            ;;
    esac

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
    log_info "  Profile: $PROFILE"
    log_info "  Compute Type: ${TF_VAR_compute_type}"
    log_info "  Region: ${AWS_REGION:-us-west-2}"

    if [[ "$DRY_RUN" == "false" ]]; then
        log_success "✅ Complete infrastructure destruction completed!"

        case "$PROFILE" in
            "minimum")
                log_success "✅ Lambda + API Gateway infrastructure destroyed!"
                ;;
            "regular")
                log_success "✅ EKS + Kubernetes infrastructure destroyed!"
                ;;
        esac

        log_info "All AWS resources have been cleaned up"
        log_info "Check AWS Console and billing dashboard to verify"
        log_success "💰 Expected cost reduction: ~$0.50-20/day depending on profile"
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
    show_destruction_impact
    confirm_destruction
    profile_specific_cleanup
    standard_pre_cleanup
    terraform_destroy
    verify_cleanup
    generate_summary

    # Return to original directory
    cd "$PROJECT_ROOT"
}

# Run main function
main "$@"