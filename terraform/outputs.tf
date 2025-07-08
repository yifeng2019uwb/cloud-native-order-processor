# terraform/outputs.tf
# Simple outputs for personal project

# Lambda (dev environment)
output "api_url" {
  description = "API Gateway URL"
  value       = local.enable_lambda ? "https://${aws_api_gateway_rest_api.order_api[0].id}.execute-api.${var.region}.amazonaws.com/${var.environment}" : null
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = local.enable_lambda ? aws_lambda_function.order_api[0].function_name : null
}

# Kubernetes (prod environment)
output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = local.enable_kubernetes ? aws_eks_cluster.main[0].name : null
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = local.enable_kubernetes ? aws_ecr_repository.order_api[0].repository_url : null
}

# Database
output "dynamodb_orders_table" {
  description = "DynamoDB orders table name"
  value       = aws_dynamodb_table.orders.name
}

# Messaging
output "sqs_queue_url" {
  description = "SQS queue URL"
  value       = aws_sqs_queue.order_processing.url
}

output "sns_topic_arn" {
  description = "SNS topic ARN"
  value       = aws_sns_topic.order_events.arn
}

# Storage
output "s3_bucket" {
  description = "S3 events bucket"
  value       = aws_s3_bucket.events.bucket
}

# Quick connection info
output "connection_info" {
  description = "Connection info for FastAPI app"
  value = {
    api_endpoint     = local.enable_lambda ? "https://${aws_api_gateway_rest_api.order_api[0].id}.execute-api.${var.region}.amazonaws.com/${var.environment}" : "TBD after EKS setup"
    orders_table     = aws_dynamodb_table.orders.name
    inventory_table  = aws_dynamodb_table.inventory.name
    queue_url        = aws_sqs_queue.order_processing.url
    topic_arn        = aws_sns_topic.order_events.arn
    s3_bucket        = aws_s3_bucket.events.bucket
  }
}