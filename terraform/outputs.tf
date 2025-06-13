# terraform/outputs.tf
# Essential outputs for both Lambda and Kubernetes deployments

# ====================
# BASIC INFO
# ====================

output "environment" {
  description = "Environment name"
  value       = var.environment
}

# ====================
# LAMBDA OUTPUTS (dev)
# ====================

output "lambda_function_name" {
  description = "Lambda function name"
  value       = local.enable_lambda ? aws_lambda_function.order_api[0].function_name : null
}

output "api_gateway_url" {
  description = "API Gateway URL"
  value       = local.enable_lambda ? "https://${aws_api_gateway_rest_api.order_api[0].id}.execute-api.${var.region}.amazonaws.com/${var.environment}" : null
}

# ====================
# KUBERNETES OUTPUTS (prod)
# ====================

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = local.enable_kubernetes ? aws_eks_cluster.main[0].name : null
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = local.enable_kubernetes ? aws_eks_cluster.main[0].endpoint : null
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = local.enable_kubernetes ? aws_ecr_repository.order_api[0].repository_url : null
}

# ====================
# SHARED RESOURCES
# ====================

output "database_endpoint" {
  description = "Database endpoint"
  value       = aws_db_instance.postgres_main.endpoint
}

output "database_port" {
  description = "Database port"
  value       = aws_db_instance.postgres_main.port
}

output "sns_topic_arn" {
  description = "SNS topic ARN"
  value       = aws_sns_topic.order_events.arn
}

output "sqs_queue_url" {
  description = "SQS queue URL"
  value       = aws_sqs_queue.order_processing.url
}

output "s3_events_bucket" {
  description = "S3 events bucket name"
  value       = aws_s3_bucket.events.bucket
}

# Add to outputs.tf temporarily
output "debug_resource_prefix" {
  value = local.resource_prefix
}