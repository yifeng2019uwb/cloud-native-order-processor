# ===== RDS WITH EASY DESTROY SETTINGS =====
# rds.tf

# Generate a random password first
resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  }
}

# Create RDS instance with destroy-friendly settings
resource "aws_db_instance" "postgres_main" {
  identifier = "${var.project_name}-${var.environment}-postgres"

  engine         = "postgres"
  engine_version = "15.7"
  instance_class = "db.t4g.micro"

  allocated_storage = 20
  storage_type      = "gp2"
  storage_encrypted = true

  db_name  = "orderprocessor"
  username = var.db_username
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  # DESTROY-FRIENDLY SETTINGS
  backup_retention_period   = 0     # No backups to retain
  skip_final_snapshot       = true  # Don't create final snapshot
  final_snapshot_identifier = null  # No final snapshot
  deletion_protection       = false # Allow deletion
  delete_automated_backups  = true  # Delete automated backups
  apply_immediately         = true  # Apply changes immediately

  performance_insights_enabled    = false
  enabled_cloudwatch_logs_exports = []
  auto_minor_version_upgrade      = false

  publicly_accessible = false

  tags = {
    Name     = "${var.project_name}-${var.environment}-postgres"
    AutoStop = "7days"
  }
}

# Create Secrets Manager secret with immediate deletion
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${var.project_name}-${var.environment}-db-credentials"
  description             = "Database credentials for ${var.project_name}"
  recovery_window_in_days = 0 # IMMEDIATE DELETION - no recovery period

  tags = {
    Name = "${var.project_name}-${var.environment}-db-credentials"
  }

  depends_on = [aws_db_instance.postgres_main]
}

# Store the complete connection info
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

# Database initialization using secrets
resource "null_resource" "init_database" {
  depends_on = [
    aws_db_instance.postgres_main,
    aws_secretsmanager_secret_version.db_credentials
  ]

  provisioner "local-exec" {
    command     = "bash -c 'export SECRET_ARN=\"${aws_secretsmanager_secret.db_credentials.arn}\" && export DB_IDENTIFIER=\"${aws_db_instance.postgres_main.identifier}\" && ${path.module}/scripts/init-db.sh'"
    working_dir = path.module
  }

  triggers = {
    database_endpoint = aws_db_instance.postgres_main.endpoint
    script_hash       = filemd5("${path.module}/scripts/init-database.sql")
    secret_version    = aws_secretsmanager_secret_version.db_credentials.version_id
  }
}