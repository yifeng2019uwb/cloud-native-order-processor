# Add these to your existing outputs.tf
output "db_password" {
  description = "Database password for initialization"
  value       = var.db_password
  sensitive   = true
}

output "database_init_command" {
  description = "Command to initialize database"
  value       = "cd terraform && ./scripts/init-db.sh"
}