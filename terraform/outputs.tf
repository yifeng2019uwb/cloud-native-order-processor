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
  value       = "Use AWS CLI: aws secretsmanager get-secret-value --secret-id ${aws_secretsmanager_secret.db_credentials.name}"
}

output "database_connection_example" {
  description = "Example of how to connect to the database"
  value       = "After getting credentials: PGPASSWORD=$(aws secretsmanager get-secret-value --secret-id ${aws_secretsmanager_secret.db_credentials.name} --query SecretString --output text | jq -r '.password') psql -h $(aws secretsmanager get-secret-value --secret-id ${aws_secretsmanager_secret.db_credentials.name} --query SecretString --output text | jq -r '.host') -U $(aws secretsmanager get-secret-value --secret-id ${aws_secretsmanager_secret.db_credentials.name} --query SecretString --output text | jq -r '.username') -d $(aws secretsmanager get-secret-value --secret-id ${aws_secretsmanager_secret.db_credentials.name} --query SecretString --output text | jq -r '.dbname')"
}

# COST OPTIMIZATION: Add cost monitoring and cleanup information
output "cost_profile_applied" {
  description = "Current cost optimization profile being used"
  value       = var.cost_profile
}

output "estimated_monthly_cost" {
  description = "Estimated monthly cost breakdown for current configuration"
  value = {
    cost_profile = var.cost_profile
    eks_cluster = "$72 (cluster) + ${var.cost_profile == "minimal" ? "$3-8 (spot instances)" : "$50+ (fargate)"}"
    rds_database = "$12-15 (db.t4g.micro)"
    s3_storage = "$1-3 (with lifecycle policies)"
    messaging = var.cost_profile == "minimal" ? "$0.50 (no encryption)" : "$2-3 (with KMS)"
    networking = var.cost_profile == "production" ? "$45+ (NAT Gateway)" : "$0-10 (VPC endpoints)"
    total_estimated = var.cost_profile == "minimal" ? "$90-110/month" : var.cost_profile == "learning" ? "$130-150/month" : "$200+/month"
  }
}

# output "cost_optimization_summary" {
#   description = "Summary of cost optimizations applied"
#   value = {
#     nat_gateway_disabled = var.cost_profile == "production" ? false : true
#     kms_encryption = "Review KMS usage in S3 and messaging for potential $3/month savings"
#     spot_instances = "Consider spot instances for EKS nodes (60-90% savings)"
#     lifecycle_policies = "Aggressive S3 cleanup (30 days events, 7 days backups)"
#     backup_retention = "RDS backups disabled (0 days retention)"
#     monitoring = "Performance Insights disabled, minimal CloudWatch"
#   }
# }

# COST OPTIMIZATION: Conditional database initialization output
# Comment out the database_initialization_status above and uncomment below:
# output "database_initialization_status" {
#   description = "Database initialization status (conditional based on cost profile)"
#   value       = var.cost_profile == "minimal" ? "Skipped for minimal cost profile - database created but not initialized" : "Database schema initialized with 3 tables: products, inventory, orders"
#   depends_on  = var.cost_profile == "minimal" ? [] : [null_resource.init_database]
# }

output "cleanup_instructions" {
  description = "Instructions for cost-efficient cleanup"
  value = {
    manual_cleanup = "Run: terraform destroy -auto-approve"
    cost_verification = "Verify all resources deleted in AWS Console to avoid unexpected charges"
    s3_verification = "S3 buckets should auto-delete due to force_destroy = true"
    recommended_schedule = "For practice: deploy -> test -> destroy within 24 hours to minimize costs"
  }
}

output "learning_next_steps" {
  description = "Next steps for cost-efficient learning"
  value = {
    current_profile = var.cost_profile
    cost_optimizations_to_try = var.cost_profile == "minimal" ? [
      "Already using minimal profile",
      "Consider spot instances for EKS nodes",
      "Test with AES256 instead of KMS encryption"
    ] : [
      "Try minimal profile: terraform apply -var='cost_profile=minimal'",
      "Disable NAT Gateway and use VPC endpoints",
      "Use spot instances instead of Fargate"
    ]
    architecture_learning = [
      "Practice VPC endpoint usage without NAT Gateway",
      "Test EKS with spot instances vs Fargate",
      "Experiment with S3 lifecycle policies",
      "Learn PostgreSQL connection via Secrets Manager"
    ]
  }
}