# terraform/outputs.tf
# Essential outputs for development and deployment

# ====================
# DEVELOPMENT ESSENTIALS
# ====================

# Main API endpoint
output "api_url" {
  description = "API Gateway URL for testing and frontend integration"
  value       = local.enable_lambda ? "https://${aws_api_gateway_rest_api.order_api[0].id}.execute-api.${var.region}.amazonaws.com/${var.environment}" : null
}

# Lambda function name for deployment scripts
output "lambda_function_name" {
  description = "Lambda function name for CI/CD deployment"
  value       = local.enable_lambda ? aws_lambda_function.order_api[0].function_name : null
}

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
    api_endpoint = local.enable_lambda ? "https://${aws_api_gateway_rest_api.order_api[0].id}.execute-api.${var.region}.amazonaws.com/${var.environment}" : "TBD after EKS setup"

    # Database tables
    users_table     = aws_dynamodb_table.users.name
    orders_table    = aws_dynamodb_table.orders.name
    inventory_table = aws_dynamodb_table.inventory.name

    # Messaging (if you use them)
    queue_url = aws_sqs_queue.order_processing.url
    topic_arn = aws_sns_topic.order_events.arn
    s3_bucket = aws_s3_bucket.events.bucket
  }
}