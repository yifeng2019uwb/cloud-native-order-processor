#!/bin/bash
# terraform/scripts/test-infrastructure.sh
# Minimal Infrastructure Test Script
# Essential tests for Terraform-managed AWS resources

set -e

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd "${TERRAFORM_DIR}/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="dev"
TEST_TYPE="all"
VERBOSE=false
DRY_RUN=false

# Usage function
show_usage() {
    cat << EOF
$(printf "${BLUE}🧪 Minimal Infrastructure Test Script${NC}")

Usage: $0 [OPTIONS]

Run essential infrastructure validation tests.

OPTIONS:
    -e, --environment ENV   Target environment (dev|prod, default: dev)
    -t, --test-type TYPE    Test type (terraform|aws|all, default: all)
    -v, --verbose          Enable verbose output
    --dry-run              Show what would be tested without running
    -h, --help             Show this help message

TEST TYPES:
    terraform              Terraform configuration and state tests
    aws                    AWS resource validation tests
    all                    Run all test types (default)

EXAMPLES:
    $0                                    # Run all tests for dev
    $0 --environment prod                 # Run all tests for prod
    $0 --test-type terraform              # Run only Terraform tests
    $0 --dry-run                          # Show what tests would run

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
    printf "\n${BLUE}=== %s ===${NC}\n" "$1"
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -t|--test-type)
                TEST_TYPE="$2"
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
    if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
        log_error "Environment must be 'dev' or 'prod'"
        exit 1
    fi

    if [[ "$TEST_TYPE" != "terraform" && "$TEST_TYPE" != "aws" && "$TEST_TYPE" != "all" ]]; then
        log_error "Test type must be 'terraform', 'aws', or 'all'"
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

# Test Terraform configuration
test_terraform() {
    log_step "Testing Terraform Configuration"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would test Terraform configuration"
        return 0
    fi

    cd "$TERRAFORM_DIR"

    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init

    # Validate configuration
    log_info "Validating Terraform configuration..."
    if terraform validate; then
        log_success "Terraform configuration is valid"
    else
        log_error "Terraform configuration validation failed"
        return 1
    fi

    # Format check
    log_info "Checking Terraform format..."
    if terraform fmt -check -recursive; then
        log_success "Terraform files are properly formatted"
    else
        log_warning "Terraform files need formatting (run: terraform fmt -recursive)"
    fi

    # Plan check
    log_info "Running Terraform plan..."
    if terraform plan -var="environment=$ENVIRONMENT" -detailed-exitcode; then
        log_success "Terraform plan completed successfully"
    else
        local exit_code=$?
        if [[ $exit_code -eq 2 ]]; then
            log_warning "Terraform plan shows changes needed"
        else
            log_error "Terraform plan failed"
            return 1
        fi
    fi
}

# Test AWS resources
test_aws_resources() {
    log_step "Testing AWS Resources"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry-run mode: Would test AWS resources"
        return 0
    fi

    local resource_prefix="order-processor-$ENVIRONMENT"

    # Test S3 buckets
    log_info "Checking S3 buckets..."
    local buckets
    buckets=$(aws s3api list-buckets \
        --query "Buckets[?contains(Name, '${resource_prefix}')].Name" \
        --output text 2>/dev/null || echo "")

    if [[ -n "$buckets" ]]; then
        log_success "Found S3 buckets: $buckets"
        for bucket in $buckets; do
            if aws s3api head-bucket --bucket "$bucket" >/dev/null 2>&1; then
                log_success "S3 bucket $bucket is accessible"
            else
                log_warning "S3 bucket $bucket is not accessible"
            fi
        done
    else
        log_info "No S3 buckets found for this project"
    fi

    # Test DynamoDB tables
    log_info "Checking DynamoDB tables..."
    local tables
    tables=$(aws dynamodb list-tables \
        --query "TableNames[?contains(@, '${resource_prefix}')]" \
        --output text 2>/dev/null || echo "")

    if [[ -n "$tables" ]]; then
        log_success "Found DynamoDB tables: $tables"
        for table in $tables; do
            if aws dynamodb describe-table --table-name "$table" >/dev/null 2>&1; then
                log_success "DynamoDB table $table is accessible"
            else
                log_warning "DynamoDB table $table is not accessible"
            fi
        done
    else
        log_info "No DynamoDB tables found for this project"
    fi

    # Test EKS clusters
    log_info "Checking EKS clusters..."
    local clusters
    clusters=$(aws eks list-clusters \
        --query "clusters[?contains(@, '${resource_prefix}')]" \
        --output text 2>/dev/null || echo "")

    if [[ -n "$clusters" ]]; then
        log_success "Found EKS clusters: $clusters"
        for cluster in $clusters; do
            local status
            status=$(aws eks describe-cluster --name "$cluster" \
                --query 'cluster.status' --output text 2>/dev/null || echo "UNKNOWN")
            log_info "EKS cluster $cluster status: $status"
        done
    else
        log_info "No EKS clusters found for this project"
    fi
}

# Main execution
main() {
    parse_arguments "$@"
    validate_arguments

    echo
    printf "${BLUE}🧪 Minimal Infrastructure Test Script${NC}\n"
    printf "${BLUE}=====================================${NC}\n"
    echo
    log_info "Environment: $ENVIRONMENT"
    log_info "Test type: $TEST_TYPE"
    echo

    check_prerequisites

    case $TEST_TYPE in
        terraform)
            test_terraform
            ;;
        aws)
            test_aws_resources
            ;;
        all)
            test_terraform
            test_aws_resources
            ;;
    esac

    log_success "✅ Infrastructure tests completed!"
    cd "$PROJECT_ROOT"
}

# Run main function
main "$@"