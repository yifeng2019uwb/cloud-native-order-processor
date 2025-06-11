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
  # COST OPTIMIZATION: Always use smallest instance for practice project
  instance_class = "db.t4g.micro"  # ALWAYS MINIMAL: ~$12/month regardless of profile

  # COST OPTIMIZATION: Always use minimal storage for practice
  allocated_storage = 20  # ALWAYS MINIMAL: 20GB is minimum for PostgreSQL
  storage_type      = "gp2"  # ALWAYS MINIMAL: gp2 simpler than gp3 for practice
  storage_encrypted = true

  db_name  = "orderprocessor"
  username = var.db_username
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  # DESTROY-FRIENDLY SETTINGS (already optimized)
  backup_retention_period   = 0     # ALWAYS MINIMAL: No backups for practice
  skip_final_snapshot       = true  # ALWAYS MINIMAL: No snapshots for practice
  final_snapshot_identifier = null  # ALWAYS MINIMAL: No final snapshot
  deletion_protection       = false # ALWAYS MINIMAL: Allow easy deletion
  delete_automated_backups  = true  # ALWAYS MINIMAL: Delete all backups
  apply_immediately         = true  # ALWAYS MINIMAL: Apply changes immediately

  # COST OPTIMIZATION: Disable all monitoring/performance features for practice
  performance_insights_enabled    = false  # ALWAYS MINIMAL: No performance monitoring
  enabled_cloudwatch_logs_exports = []     # ALWAYS MINIMAL: No log exports
  auto_minor_version_upgrade      = false  # ALWAYS MINIMAL: Manual control

  # COST OPTIMIZATION: Always single AZ for practice (Multi-AZ doubles cost)
  multi_az = false  # ALWAYS MINIMAL: No HA needed for practice

  # COST OPTIMIZATION: Not publicly accessible (security + no extra costs)
  publicly_accessible = false  # ALWAYS MINIMAL: Private access only

  tags = {
    Name     = "${var.project_name}-${var.environment}-postgres"
    Purpose  = "Practice-Learning"  # CLEARLY MARK as practice
    AutoStop = "7days"
  }
}

# COST OPTIMIZATION: Alternative scalable settings for different learning needs
# Comment out the settings above and uncomment below ONLY if you need to test scaling:
# resource "aws_db_instance" "postgres_main" {
#   identifier = "${var.project_name}-${var.environment}-postgres"
#
#   engine         = "postgres"
#   engine_version = "15.7"
#   instance_class = var.cost_profile == "minimal" ? "db.t4g.micro" : var.cost_profile == "learning" ? "db.t4g.small" : "db.t4g.medium"  # COST SCALING: Only if testing RDS scaling
#
#   allocated_storage = var.cost_profile == "minimal" ? 20 : var.cost_profile == "learning" ? 50 : 100  # COST SCALING: Only if testing storage scaling
#   storage_type      = "gp2"
#   storage_encrypted = true
#
#   db_name  = "orderprocessor"
#   username = var.db_username
#   password = random_password.db_password.result
#
#   vpc_security_group_ids = [aws_security_group.rds.id]
#   db_subnet_group_name   = aws_db_subnet_group.main.name
#
#   backup_retention_period   = var.cost_profile == "production" ? 7 : 0     # COST SCALING: Only backups for production testing
#   skip_final_snapshot       = true
#   final_snapshot_identifier = null
#   deletion_protection       = false
#   delete_automated_backups  = true
#   apply_immediately         = true
#
#   performance_insights_enabled    = false
#   enabled_cloudwatch_logs_exports = []
#   auto_minor_version_upgrade      = false
#
#   multi_az = var.cost_profile == "production"  # COST SCALING: Only Multi-AZ for production testing
#   publicly_accessible = false
#
#   tags = {
#     Name     = "${var.project_name}-${var.environment}-postgres"
#     Purpose  = "Practice-Learning-Scaling"
#     AutoStop = "7days"
#   }
# }

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
  # COST OPTIMIZATION: Skip complex initialization for minimal cost
  count = var.cost_profile == "minimal" ? 0 : 1  # SKIP for minimal - just test basic connectivity

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

# COST OPTIMIZATION: For absolute minimal practice, comment out init entirely
# Comment out the null_resource above and uncomment below for zero initialization cost:
# resource "null_resource" "init_database" {
#   count = 0  # ALWAYS SKIP: No database initialization for pure practice
#
#   # Empty resource - database will be created but not initialized
#   # Use manual psql connection to test database connectivity
#   # This saves time and complexity for pure infrastructure practice
# }