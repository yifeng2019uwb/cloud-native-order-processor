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

output "database_secret_arn" {
  description = "ARN of the database credentials in Secrets Manager"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "database_secret_name" {
  description = "Name of the database secret in Secrets Manager"
  value       = aws_secretsmanager_secret.db_credentials.name
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

output "database_initialization_status" {
  description = "Database initialization completed"
  value       = "Database schema initialized with 3 tables: products, inventory, orders"
  depends_on  = [null_resource.init_database]
}

# Instructions for accessing database
output "database_access_instructions" {
  description = "How to access the database credentials"
  value = "Use AWS CLI: aws secretsmanager get-secret-value --secret-id ${aws_secretsmanager_secret.db_credentials.name}"
}

output "database_connection_example" {
  description = "Example of how to connect to the database"
  value = "After getting credentials: PGPASSWORD=$(aws secretsmanager get-secret-value --secret-id ${aws_secretsmanager_secret.db_credentials.name} --query SecretString --output text | jq -r '.password') psql -h $(aws secretsmanager get-secret-value --secret-id ${aws_secretsmanager_secret.db_credentials.name} --query SecretString --output text | jq -r '.host') -U $(aws secretsmanager get-secret-value --secret-id ${aws_secretsmanager_secret.db_credentials.name} --query SecretString --output text | jq -r '.username') -d $(aws secretsmanager get-secret-value --secret-id ${aws_secretsmanager_secret.db_credentials.name} --query SecretString --output text | jq -r '.dbname')"
}