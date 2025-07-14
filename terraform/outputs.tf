# terraform/outputs.tf
# Essential outputs for development and deployment

# ====================
# PRODUCTION DEPLOYMENT (when needed)
# ====================

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = local.enable_kubernetes ? aws_eks_cluster.main[0].name : null
}

output "ecr_repository_url" {
  description = "ECR repository URL for container deployment"
  value       = local.enable_kubernetes ? aws_ecr_repository.order_api[0].repository_url : null
}

# ====================
# APPLICATION CONFIGURATION (single source of truth)
# ====================

output "app_config" {
  description = "Complete configuration for application environment variables"
  value = {
    # API
    api_endpoint = local.enable_kubernetes ? "TBD after EKS setup" : "http://localhost:8000"

    # Database tables
    users_table     = aws_dynamodb_table.users.name
    orders_table    = aws_dynamodb_table.orders.name
    inventory_table = aws_dynamodb_table.inventory.name

    # Messaging (if you use them)
    queue_url = aws_sqs_queue.order_processing.url
    topic_arn = aws_sns_topic.order_events.arn
    s3_bucket = aws_s3_bucket.main.bucket
    logs_bucket = aws_s3_bucket.logs.bucket

    # IAM Role for application services
    application_role_arn = aws_iam_role.application_service.arn
    aws_account_id = data.aws_caller_identity.current.account_id
  }
}

# Individual outputs for easier access
output "application_role_arn" {
  description = "ARN of the IAM role for application services"
  value       = aws_iam_role.application_service.arn
}

output "application_user_arn" {
  description = "ARN of the IAM user for application role assumption"
  value       = aws_iam_user.application_user.arn
}

output "aws_account_id" {
  description = "Current AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  description = "Current AWS region"
  value       = data.aws_region.current.name
}

# ====================
# LOCAL K8S CREDENTIALS (only for local dev)
# ====================

output "application_user_access_key_id" {
  description = "Access key ID for local K8s (only for local dev)"
  value       = local.enable_kubernetes ? null : aws_iam_access_key.application_user[0].id
  sensitive   = false
}

output "application_user_access_key_secret" {
  description = "Access key secret for local K8s (only for local dev)"
  value       = local.enable_kubernetes ? null : aws_iam_access_key.application_user[0].secret
  sensitive   = true
}