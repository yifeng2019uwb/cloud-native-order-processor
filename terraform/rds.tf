# ===== SHARED RDS CONFIGURATION =====
# rds.tf - RDS as shared resource across all profiles

# Generate a random password
resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# DB Subnet Group - conditional based on VPC existence
resource "aws_db_subnet_group" "main" {
  count = local.create_vpc ? 1 : 0

  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  }
}

# RDS instance - always created (shared resource)
resource "aws_db_instance" "postgres_main" {
  identifier = "${var.project_name}-${var.environment}-postgres"

  engine         = "postgres"
  engine_version = "15.7"
  instance_class = "db.t4g.micro"  # Always minimal for cost

  # Storage configuration
  allocated_storage = 20
  storage_type      = "gp2"
  storage_encrypted = true

  # Database configuration
  db_name  = "orderprocessor"
  username = var.db_username
  password = random_password.db_password.result

  # Network configuration - conditional based on profile
  vpc_security_group_ids = local.create_vpc ? [aws_security_group.rds[0].id] : null
  db_subnet_group_name   = local.create_vpc ? aws_db_subnet_group.main[0].name : null

  # Public access for Lambda profile (no VPC), private for Kubernetes
  publicly_accessible = local.enable_lambda ? true : false

  # Destroy-friendly settings
  backup_retention_period   = 0
  skip_final_snapshot       = true
  final_snapshot_identifier = null
  deletion_protection       = false
  delete_automated_backups  = true
  apply_immediately         = true

  # Cost optimization settings
  performance_insights_enabled    = false
  enabled_cloudwatch_logs_exports = []
  auto_minor_version_upgrade      = false
  multi_az                        = false

  tags = {
    Name     = "${var.project_name}-${var.environment}-postgres"
    Purpose  = "Practice-Learning"
    AutoStop = "7days"
  }
}

# Secrets Manager secret - always created
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${var.project_name}-${var.environment}-db-credentials"
  description             = "Database credentials for ${var.project_name}"
  recovery_window_in_days = 0  # Immediate deletion

  tags = {
    Name = "${var.project_name}-${var.environment}-db-credentials"
  }
}

# Store complete connection info - always created
resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_username
    password = random_password.db_password.result
    engine   = "postgres"
    host     = aws_db_instance.postgres_main.endpoint
    port     = tonumber(aws_db_instance.postgres_main.port)
    dbname   = aws_db_instance.postgres_main.db_name
  })

  depends_on = [aws_db_instance.postgres_main]
}