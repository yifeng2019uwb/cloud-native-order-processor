# terraform/outputs.tf
# Essential outputs for development and deployment

# ====================
# PRODUCTION DEPLOYMENT (when needed)
# ====================

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = local.enable_prod ? aws_eks_cluster.main[0].name : null
}

output "ecr_repository_url" {
  description = "ECR repository URL for container deployment"
  value       = local.enable_prod ? aws_ecr_repository.order_api[0].repository_url : null
}

# ====================
# APPLICATION CONFIGURATION (single source of truth)
# ====================

output "app_config" {
  description = "Complete configuration for application environment variables"
  value = {
    # API
    api_endpoint = local.enable_prod ? "TBD after EKS setup" : "http://localhost:8000"

    # Database tables
    users_table     = aws_dynamodb_table.users.name
    orders_table    = aws_dynamodb_table.orders.name
    inventory_table = aws_dynamodb_table.inventory.name

    # Messaging (if you use them)
    queue_url = aws_sqs_queue.order_processing.url
    topic_arn = aws_sns_topic.order_events.arn
    s3_bucket = aws_s3_bucket.main.bucket
    logs_bucket = aws_s3_bucket.logs.bucket

          # IAM Role for Kubernetes service accounts (IRSA)
      k8s_sa_role_arn = aws_iam_role.k8s_sa.arn
    aws_account_id = data.aws_caller_identity.current.account_id

    # Redis configuration
    redis_endpoint = local.enable_prod ? aws_elasticache_cluster.redis[0].cache_nodes[0].address : "redis.order-processor.svc.cluster.local"
    redis_port     = 6379
    redis_auth_required = false  # No auth for simplicity in personal project
    redis_ssl_required = local.enable_prod  # SSL only in prod for security
  }
}

# Individual outputs for easier access
output "k8s_sa_role_arn" {
  description = "ARN of the Kubernetes service account role"
  value       = aws_iam_role.k8s_sa.arn
}

output "eks_oidc_provider_arn" {
  description = "ARN of the EKS OIDC provider for IRSA"
  value       = local.enable_prod ? aws_iam_openid_connect_provider.eks[0].arn : null
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
  value       = local.enable_prod ? null : aws_iam_access_key.application_user[0].id
  sensitive   = false
}

output "application_user_access_key_secret" {
  description = "Access key secret for local K8s (only for local dev)"
  value       = local.enable_prod ? null : aws_iam_access_key.application_user[0].secret
  sensitive   = true
}

# Individual Redis outputs
output "redis_endpoint" {
  description = "Redis endpoint"
  value       = local.enable_prod ? aws_elasticache_cluster.redis[0].cache_nodes[0].address : "redis.order-processor.svc.cluster.local"
}