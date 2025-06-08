# ===== OUTPUTS =====
# outputs.tf
output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.postgres_main.endpoint
  sensitive   = true
}

output "database_connection_string" {
  description = "Database connection string"
  value       = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres_main.endpoint}:${aws_db_instance.postgres_main.port}/${aws_db_instance.postgres_main.db_name}"
  sensitive   = true
}

output "s3_events_bucket_name" {
  description = "S3 bucket name for event sourcing"
  value       = aws_s3_bucket.events.bucket
}

output "sns_order_events_topic_arn" {
  description = "SNS topic ARN for order events"
  value       = aws_sns_topic.order_events.arn
}

output "sqs_order_processing_queue_url" {
  description = "SQS queue URL for order processing"
  value       = aws_sqs_queue.order_processing.url
}

output "ecr_order_api_repository_url" {
  description = "ECR repository URL for order API"
  value       = aws_ecr_repository.order_api.repository_url
}

output "order_service_role_arn" {
  description = "IAM role ARN for order service"
  value       = aws_iam_role.order_service.arn
}