# Outputs
output "vpc_id" {
  description = "The ID of the created VPC."
  value       = aws_vpc.main_vpc.id
}

output "rds_endpoint" {
  description = "The endpoint address of the PostgreSQL RDS instance."
  value       = aws_db_instance.postgres_db.address
}

output "rds_port" {
  description = "The port of the PostgreSQL RDS instance."
  value       = aws_db_instance.postgres_db.port
}

output "db_username" {
  description = "Username for the PostgreSQL database (for reference, sensitive info in secrets)."
  value       = var.db_username
}