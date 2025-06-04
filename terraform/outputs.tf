# Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "app_security_group_id" {
  description = "Security group ID for application"
  value       = aws_security_group.app.id
}

# Order Database Outputs
output "rds_order_endpoint" {
  description = "Order RDS instance endpoint"
  value       = aws_db_instance.postgres_order.endpoint
}

output "rds_order_port" {
  description = "Order RDS instance port"
  value       = aws_db_instance.postgres_order.port
}

output "order_database_name" {
  description = "Order database name"
  value       = aws_db_instance.postgres_order.db_name
}

# Product Database Outputs
output "rds_product_endpoint" {
  description = "Product RDS instance endpoint"
  value       = aws_db_instance.postgres_product.endpoint
}

output "rds_product_port" {
  description = "Product RDS instance port"
  value       = aws_db_instance.postgres_product.port
}

output "product_database_name" {
  description = "Product database name"
  value       = aws_db_instance.postgres_product.db_name
}

# Inventory Database Outputs
output "rds_inventory_endpoint" {
  description = "Inventory RDS instance endpoint"
  value       = aws_db_instance.postgres_inventory.endpoint
}

output "rds_inventory_port" {
  description = "Inventory RDS instance port"
  value       = aws_db_instance.postgres_inventory.port
}

output "inventory_database_name" {
  description = "Inventory database name"
  value       = aws_db_instance.postgres_inventory.db_name
}

# Database Connection Strings (for Kubernetes secrets)
output "order_db_connection_string" {
  description = "Order database connection string"
  value       = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres_order.endpoint}:${aws_db_instance.postgres_order.port}/${aws_db_instance.postgres_order.db_name}"
  sensitive   = true
}

output "product_db_connection_string" {
  description = "Product database connection string"
  value       = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres_product.endpoint}:${aws_db_instance.postgres_product.port}/${aws_db_instance.postgres_product.db_name}"
  sensitive   = true
}

output "inventory_db_connection_string" {
  description = "Inventory database connection string"
  value       = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres_inventory.endpoint}:${aws_db_instance.postgres_inventory.port}/${aws_db_instance.postgres_inventory.db_name}"
  sensitive   = true
}