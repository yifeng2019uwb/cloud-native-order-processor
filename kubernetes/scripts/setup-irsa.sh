#!/bin/bash
# kubernetes/scripts/setup-irsa.sh
# Setup IRSA (IAM Roles for Service Accounts) for EKS

set -e

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Usage information
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Setup IRSA (IAM Roles for Service Accounts) for EKS

OPTIONS:
    -e, --environment ENV   Target environment (dev, prod)
    -c, --cluster CLUSTER   EKS cluster name
    -r, --region REGION     AWS region (default: us-east-1)
    -h, --help              Show this help message

EXAMPLES:
    $0 --environment prod --cluster order-processor-prod
    $0 --environment prod --cluster my-cluster --region us-west-2

EOF
}

# Parse command line arguments
ENVIRONMENT="prod"
CLUSTER_NAME=""
AWS_REGION="us-east-1"

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -c|--cluster)
            CLUSTER_NAME="$2"
            shift 2
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
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

# Validate environment
if [[ "$ENVIRONMENT" != "prod" ]]; then
    log_error "IRSA is only needed for production environment"
    exit 1
fi

# Get cluster name from Terraform if not provided
if [[ -z "$CLUSTER_NAME" ]]; then
    log_info "Getting cluster name from Terraform..."
    cd "$PROJECT_ROOT/terraform"

    if ! CLUSTER_NAME=$(terraform output -raw eks_cluster_name 2>/dev/null); then
        log_error "Could not get cluster name from Terraform. Please provide --cluster option."
        exit 1
    fi

    log_info "Using cluster: $CLUSTER_NAME"
fi

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is required but not installed"
        exit 1
    fi

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is required but not installed"
        exit 1
    fi

    # Check eksctl
    if ! command -v eksctl &> /dev/null; then
        log_warning "eksctl is not installed. Some operations may not work."
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials are not configured"
        exit 1
    fi

    log_success "Prerequisites satisfied"
}

# Get OIDC provider ID
get_oidc_provider_id() {
    log_info "Getting OIDC provider ID for cluster..."

    OIDC_PROVIDER_ID=$(aws eks describe-cluster --name "$CLUSTER_NAME" --region "$AWS_REGION" \
        --query "cluster.identity.oidc.issuer" --output text | cut -d'/' -f5)

    if [[ -z "$OIDC_PROVIDER_ID" ]]; then
        log_error "Could not get OIDC provider ID"
        exit 1
    fi

    log_info "OIDC Provider ID: $OIDC_PROVIDER_ID"
    echo "$OIDC_PROVIDER_ID"
}

# Update service account with correct role ARN
update_service_account() {
    log_info "Updating service account with IAM role ARN..."

    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

    # Get role ARN from Terraform
    cd "$PROJECT_ROOT/terraform"
    ROLE_ARN=$(terraform output -raw application_role_arn)

    log_info "AWS Account ID: $AWS_ACCOUNT_ID"
    log_info "Role ARN: $ROLE_ARN"

    # Update the service account file
    SERVICE_ACCOUNT_FILE="$PROJECT_ROOT/kubernetes/prod/service-account.yaml"

    if [[ -f "$SERVICE_ACCOUNT_FILE" ]]; then
        # Replace placeholder with actual values
        sed -i.bak "s/\${AWS_ACCOUNT_ID}/$AWS_ACCOUNT_ID/g" "$SERVICE_ACCOUNT_FILE"
        sed -i.bak "s|order-processor-prod-application-service-role|$(basename "$ROLE_ARN")|g" "$SERVICE_ACCOUNT_FILE"

        log_success "Updated service account configuration"
        log_info "File: $SERVICE_ACCOUNT_FILE"
    else
        log_error "Service account file not found: $SERVICE_ACCOUNT_FILE"
        exit 1
    fi
}

# Verify IRSA setup
verify_irsa_setup() {
    log_info "Verifying IRSA setup..."

    # Check if OIDC provider exists
    OIDC_PROVIDER_ID=$(get_oidc_provider_id)

    if aws iam list-open-id-connect-providers --query "OpenIDConnectProviderList[?contains(Arn, '$OIDC_PROVIDER_ID')]" --output text | grep -q "$OIDC_PROVIDER_ID"; then
        log_success "OIDC provider exists"
    else
        log_warning "OIDC provider not found. This may be normal if using Terraform-managed OIDC provider."
    fi

    # Check if service account exists
    if kubectl get serviceaccount order-processor-sa -n order-processor &> /dev/null; then
        log_success "Service account exists"

        # Check annotations
        ROLE_ARN=$(kubectl get serviceaccount order-processor-sa -n order-processor -o jsonpath='{.metadata.annotations.eks\.amazonaws\.com/role-arn}')
        if [[ -n "$ROLE_ARN" ]]; then
            log_success "Service account has IAM role annotation: $ROLE_ARN"
        else
            log_warning "Service account missing IAM role annotation"
        fi
    else
        log_warning "Service account not found. Deploy the application first."
    fi
}

# Main execution
main() {
    log_info "🚀 Setting up IRSA for EKS cluster: $CLUSTER_NAME"
    log_info "📍 AWS Region: $AWS_REGION"
    log_info "🏗️  Environment: $ENVIRONMENT"

    # Check prerequisites
    check_prerequisites

    # Update service account
    update_service_account

    # Verify setup
    verify_irsa_setup

    log_success "🎉 IRSA setup completed!"
    log_info "📝 Next steps:"
    log_info "   1. Deploy your application: ./kubernetes/deploy.sh --environment prod"
    log_info "   2. Verify pods can assume the role"
    log_info "   3. Test Redis connectivity"
}

# Run main function
main "$@"