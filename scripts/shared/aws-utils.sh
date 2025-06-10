#!/bin/bash
# File: scripts/shared/aws-utils.sh
# Common AWS utility functions
# AWS credential validation with account ID detection
# Region management and availability checks
# S3 bucket operations (check, create with security)
# Terraform output retrieval for infrastructure tests
# CloudFormation stack monitoring utilities

set -euo pipefail

# AWS utility functions
check_aws_credentials() {
    log_info "Checking AWS credentials..."

    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        log_error "AWS credentials not configured or invalid"
        log_error "Please configure AWS credentials using one of:"
        log_error "  - aws configure"
        log_error "  - AWS_PROFILE environment variable"
        log_error "  - IAM role (for CI/CD)"
        return 1
    fi

    local caller_identity
    caller_identity=$(aws sts get-caller-identity)
    local account_id
    account_id=$(echo "${caller_identity}" | jq -r '.Account')
    local user_arn
    user_arn=$(echo "${caller_identity}" | jq -r '.Arn')

    log_info "AWS credentials verified successfully"
    log_debug "Account ID: ${account_id}"
    log_debug "User/Role ARN: ${user_arn}"

    # Export for use by other scripts
    export AWS_ACCOUNT_ID="${account_id}"

    return 0
}

get_aws_region() {
    local region="${AWS_REGION:-}"

    if [[ -z "${region}" ]]; then
        region=$(aws configure get region 2>/dev/null || echo "${AWS_DEFAULT_REGION:-us-west-2}")
    fi

    log_debug "Using AWS region: ${region}"
    export AWS_REGION="${region}"
    echo "${region}"
}

check_aws_region_availability() {
    local region="${1:-$(get_aws_region)}"

    log_debug "Checking availability of AWS region: ${region}"

    if ! aws ec2 describe-regions --region-names "${region}" >/dev/null 2>&1; then
        log_error "AWS region '${region}' is not available or accessible"
        return 1
    fi

    log_debug "AWS region '${region}' is available"
    return 0
}

check_s3_bucket_exists() {
    local bucket_name="${1}"

    if [[ -z "${bucket_name}" ]]; then
        log_error "Bucket name not provided to check_s3_bucket_exists"
        return 1
    fi

    log_debug "Checking if S3 bucket exists: ${bucket_name}"

    if aws s3api head-bucket --bucket "${bucket_name}" >/dev/null 2>&1; then
        log_debug "S3 bucket exists: ${bucket_name}"
        return 0
    else
        log_debug "S3 bucket does not exist: ${bucket_name}"
        return 1
    fi
}

create_s3_bucket_if_not_exists() {
    local bucket_name="${1}"
    local region="${2:-$(get_aws_region)}"

    if [[ -z "${bucket_name}" ]]; then
        log_error "Bucket name not provided to create_s3_bucket_if_not_exists"
        return 1
    fi

    if check_s3_bucket_exists "${bucket_name}"; then
        log_info "S3 bucket already exists: ${bucket_name}"
        return 0
    fi

    log_info "Creating S3 bucket: ${bucket_name}"

    if [[ "${region}" == "us-east-1" ]]; then
        # us-east-1 doesn't need LocationConstraint
        aws s3api create-bucket --bucket "${bucket_name}"
    else
        aws s3api create-bucket \
            --bucket "${bucket_name}" \
            --region "${region}" \
            --create-bucket-configuration LocationConstraint="${region}"
    fi

    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket "${bucket_name}" \
        --versioning-configuration Status=Enabled

    # Add bucket policy for secure access
    local bucket_policy='{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:*",
                "Resource": [
                    "arn:aws:s3:::'"${bucket_name}"'/*",
                    "arn:aws:s3:::'"${bucket_name}"'"
                ],
                "Condition": {
                    "Bool": {
                        "aws:SecureTransport": "false"
                    }
                }
            }
        ]
    }'

    echo "${bucket_policy}" | aws s3api put-bucket-policy \
        --bucket "${bucket_name}" \
        --policy file:///dev/stdin

    log_info "S3 bucket created successfully: ${bucket_name}"
    return 0
}

wait_for_stack_status() {
    local stack_name="${1}"
    local expected_status="${2}"
    local timeout="${3:-600}"
    local check_interval="${4:-30}"

    log_info "Waiting for CloudFormation stack '${stack_name}' to reach status '${expected_status}'"

    local elapsed=0
    while [[ ${elapsed} -lt ${timeout} ]]; do
        local current_status
        current_status=$(aws cloudformation describe-stacks \
            --stack-name "${stack_name}" \
            --query 'Stacks[0].StackStatus' \
            --output text 2>/dev/null || echo "NOT_FOUND")

        log_debug "Stack ${stack_name} current status: ${current_status}"

        if [[ "${current_status}" == "${expected_status}" ]]; then
            log_info "Stack '${stack_name}' reached expected status: ${expected_status}"
            return 0
        elif [[ "${current_status}" =~ FAILED|ROLLBACK ]]; then
            log_error "Stack '${stack_name}' failed with status: ${current_status}"
            return 1
        fi

        log_debug "Waiting ${check_interval}s for stack status change..."
        sleep "${check_interval}"
        elapsed=$((elapsed + check_interval))
    done

    log_error "Timeout waiting for stack '${stack_name}' to reach status '${expected_status}'"
    return 1
}

get_terraform_outputs() {
    local terraform_dir="${1:-}"

    if [[ -z "${terraform_dir}" ]]; then
        terraform_dir="${PROJECT_ROOT}/terraform"
    fi

    if [[ ! -d "${terraform_dir}" ]]; then
        log_error "Terraform directory not found: ${terraform_dir}"
        return 1
    fi

    log_debug "Getting Terraform outputs from: ${terraform_dir}"

    pushd "${terraform_dir}" >/dev/null

    if ! terraform output -json > /tmp/terraform_outputs.json 2>/dev/null; then
        log_error "Failed to get Terraform outputs. Make sure infrastructure is deployed."
        popd >/dev/null
        return 1
    fi

    popd >/dev/null

    log_debug "Terraform outputs retrieved successfully"
    echo "/tmp/terraform_outputs.json"
    return 0
}

# Export functions for use in other scripts
export -f check_aws_credentials
export -f get_aws_region
export -f check_aws_region_availability
export -f check_s3_bucket_exists
export -f create_s3_bucket_if_not_exists
export -f wait_for_stack_status
export -f get_terraform_outputs
