# terraform/outputs.tf
# Profile-aware outputs for both Lambda and Kubernetes deployments

# Environment and profile information
output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "profile" {
  description = "Resource profile"
  value       = var.profile
}

output "compute_type" {
  description = "Compute platform type"
  value       = var.compute_type
}

output "region" {
  description = "AWS region"
  value       = var.region
}

# Lambda-specific outputs (minimum profile)
output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = var.compute_type == "lambda" ? aws_lambda_function.order_api[0].function_name : null
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = var.compute_type == "lambda" ? aws_lambda_function.order_api[0].arn : null
}

output "lambda_invoke_arn" {
  description = "Invoke ARN of the Lambda function"
  value       = var.compute_type == "lambda" ? aws_lambda_function.order_api[0].invoke_arn : null
}

output "api_gateway_url" {
  description = "API Gateway invocation URL"
  value       = var.compute_type == "lambda" ? "https://${aws_api_gateway_rest_api.order_api[0].id}.execute-api.${var.region}.amazonaws.com/${var.environment}" : null
}

output "api_gateway_id" {
  description = "API Gateway REST API ID"
  value       = var.compute_type == "lambda" ? aws_api_gateway_rest_api.order_api[0].id : null
}

# Kubernetes-specific outputs (regular profile)
output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = var.compute_type == "kubernetes" ? aws_eks_cluster.main[0].name : null
}

output "eks_cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = var.compute_type == "kubernetes" ? aws_eks_cluster.main[0].endpoint : null
}

output "eks_cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = var.compute_type == "kubernetes" ? aws_eks_cluster.main[0].vpc_config[0].cluster_security_group_id : null
}

output "eks_cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = var.compute_type == "kubernetes" ? aws_eks_cluster.main[0].certificate_authority[0].data : null
}

# output "eks_node_group_arn" {
#   description = "Amazon Resource Name (ARN) of the EKS Node Group"
#   value       = var.compute_type == "kubernetes" ? aws_eks_node_group.main[0].arn : null
# }

# Database outputs (shared across profiles)
output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.postgres_main.endpoint
}

output "database_port" {
  description = "RDS instance port"
  value       = aws_db_instance.postgres_main.port
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.postgres_main.db_name
}

output "database_username" {
  description = "Database username"
  value       = aws_db_instance.postgres_main.username
  sensitive   = true
}

# output "database_password_ssm_parameter" {
#   description = "SSM parameter name containing database password"
#   value       = aws_ssm_parameter.db_password.name
# }

# Messaging outputs (shared across profiles)
output "sns_order_events_topic_arn" {
  description = "ARN of the SNS topic for order events"
  value       = aws_sns_topic.order_events.arn
}

# output "sqs_order_processing_queue_url" {
#   description = "URL of the SQS queue for order processing"
#   value       = aws_sqs_queue.order_processing.url
# }

output "sqs_order_processing_queue_arn" {
  description = "ARN of the SQS queue for order processing"
  value       = aws_sqs_queue.order_processing.arn
}

# output "sqs_order_processing_dlq_url" {
#   description = "URL of the SQS dead letter queue"
#   value       = aws_sqs_queue.order_processing_dlq.url
# }

# Storage outputs (shared across profiles)
output "s3_events_bucket_name" {
  description = "Name of the S3 bucket for events"
  value       = aws_s3_bucket.events.bucket
}

output "s3_events_bucket_arn" {
  description = "ARN of the S3 bucket for events"
  value       = aws_s3_bucket.events.arn
}

# ECR outputs (for regular profile with Docker images)
output "ecr_order_api_repository_url" {
  description = "URL of the ECR repository for order API"
  value = var.compute_type == "kubernetes" ? aws_ecr_repository.order_api[0].repository_url : null
}

output "ecr_order_api_repository_arn" {
  description = "ARN of the ECR repository for order API"
  value       = var.compute_type == "kubernetes" ? aws_ecr_repository.order_api[0].arn : null
}

# IAM outputs for application use
output "lambda_execution_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = var.compute_type == "lambda" ? aws_iam_role.lambda_execution[0].arn : null
}

output "order_service_role_arn" {
  description = "ARN of the order service role (EKS service account role)"
  value       = var.compute_type == "kubernetes" ? aws_iam_role.order_service[0].arn : null
}

# VPC outputs (only for regular profile)
output "vpc_id" {
  description = "ID of the VPC"
  value       = var.compute_type == "kubernetes" ? aws_vpc.main[0].id : null
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = var.compute_type == "kubernetes" ? aws_subnet.private[*].id : null
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = var.compute_type == "kubernetes" ? aws_subnet.public[*].id : null
}

# CloudWatch outputs
# output "application_log_group_name" {
#   description = "Name of the CloudWatch log group for application logs"
#   value       = aws_cloudwatch_log_group.application.name
# }

output "lambda_log_group_name" {
  description = "Name of the CloudWatch log group for Lambda logs"
  value       = var.compute_type == "lambda" ? aws_cloudwatch_log_group.lambda_logs[0].name : null
}

# Deployment information
output "deployment_summary" {
  description = "Summary of deployed resources"
  value = {
    environment    = var.environment
    profile        = var.profile
    compute_type   = var.compute_type
    region         = var.region

    # Endpoints
    api_url        = var.compute_type == "lambda" ? "https://${aws_api_gateway_rest_api.order_api[0].id}.execute-api.${var.region}.amazonaws.com/${var.environment}" : null
    eks_endpoint   = var.compute_type == "kubernetes" ? aws_eks_cluster.main[0].endpoint : null

    # Database
    database_host  = aws_db_instance.postgres_main.address

    # Messaging
    sns_topic      = aws_sns_topic.order_events.arn
    sqs_queue      = aws_sqs_queue.order_processing.url

    # Storage
    s3_bucket      = aws_s3_bucket.events.bucket
  }
}