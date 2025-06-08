# ===== RDS WITH AUTO-PAUSE (Aurora Serverless alternative) =====
# rds.tf
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id  # Use both private subnets for RDS requirement

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  }
}

# Use t4g.micro with RDS Proxy for connection pooling
resource "aws_db_instance" "postgres_main" {
  identifier = "${var.project_name}-${var.environment}-postgres"

  engine         = "postgres"
  engine_version = "15.7"
  instance_class = "db.t4g.micro"  # Free tier eligible

  allocated_storage = 20
  storage_type      = "gp2"
  storage_encrypted = true

  db_name  = "orderprocessor"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  # Maximum cost optimization
  backup_retention_period = 0
  skip_final_snapshot     = true
  deletion_protection     = false
  apply_immediately       = true

  # Auto-pause settings (stops after 7 days of inactivity)
  performance_insights_enabled = false  # Disable to save costs
  enabled_cloudwatch_logs_exports = []
  auto_minor_version_upgrade = false
  
  # Allow connections from anywhere in VPC
  publicly_accessible = false

  tags = {
    Name        = "${var.project_name}-${var.environment}-postgres"
    AutoStop    = "7days"
  }
}

# Create tables rds.tf
# Null resource to initialize database schema automatically
resource "null_resource" "init_database" {
  depends_on = [aws_db_instance.postgres_main]

  provisioner "local-exec" {
    command = "./scripts/init-db.sh"
    working_dir = path.module
  }

  triggers = {
    database_endpoint = aws_db_instance.postgres_main.endpoint
    script_hash = filemd5("${path.module}/scripts/init-database.sql")
  }
}