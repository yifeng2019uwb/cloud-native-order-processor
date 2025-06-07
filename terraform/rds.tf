# RDS PostgreSQL Instance - Order Service
resource "aws_db_instance" "postgres_order" {
  identifier = "${var.project_name}-${var.environment}-postgres-order"

  engine         = "postgres"
  engine_version = "15"
  instance_class = "db.t4g.micro"

  allocated_storage     = 20
  max_allocated_storage = 40
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "orderdb"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_order.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  # Add this line to apply changes immediately
  apply_immediately = true 

  # Cost optimization settings
  backup_retention_period = 0  
  skip_final_snapshot     = true
  deletion_protection     = false
  
  # Enable auto-stop after inactivity
  # Note: RDS automatically stops after 7 days of no connections
  # and stays stopped until you manually start it
  
  # Free Performance Insights for t4g.micro
  performance_insights_enabled          = true
  performance_insights_retention_period = 7  

  # Disable unnecessary features
  enabled_cloudwatch_logs_exports = []
  auto_minor_version_upgrade      = false

  tags = {
    Name        = "${var.project_name}-${var.environment}-postgres-order"
    Environment = var.environment
    Service     = "order"
  }
}

# RDS PostgreSQL Instance - Product Service
resource "aws_db_instance" "postgres_product" {
  identifier = "${var.project_name}-${var.environment}-postgres-product"

  engine         = "postgres"
  engine_version = "15"
  instance_class = "db.t4g.micro"

  allocated_storage     = 20
  max_allocated_storage = 40
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "productdb"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_product.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  # Add this line to apply changes immediately
  apply_immediately = true 

  # Cost optimization settings
  backup_retention_period = 0  
  skip_final_snapshot     = true
  deletion_protection     = false
  
  # Enable auto-stop after inactivity
  # Note: RDS automatically stops after 7 days of no connections
  # and stays stopped until you manually start it
  
  # Free Performance Insights for t4g.micro
  performance_insights_enabled          = true
  performance_insights_retention_period = 7  

  # Disable unnecessary features
  enabled_cloudwatch_logs_exports = []
  auto_minor_version_upgrade      = false

  tags = {
    Name        = "${var.project_name}-${var.environment}-postgres-product"
    Environment = var.environment
    Service     = "product"
  }
}

# RDS PostgreSQL Instance - Inventory Service
resource "aws_db_instance" "postgres_inventory" {
  identifier = "${var.project_name}-${var.environment}-postgres-inventory"

  engine         = "postgres"
  engine_version = "15"
  instance_class = "db.t4g.micro"

  allocated_storage     = 20
  max_allocated_storage = 40
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "inventorydb"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_inventory.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  # Add this line to apply changes immediately
  apply_immediately = true 
  
  # Cost optimization settings
  backup_retention_period = 0  
  skip_final_snapshot     = true
  deletion_protection     = false
  
  # Enable auto-stop after inactivity
  # Note: RDS automatically stops after 7 days of no connections
  # and stays stopped until you manually start it
  
  # Free Performance Insights for t4g.micro
  performance_insights_enabled          = true
  performance_insights_retention_period = 7  

  # Disable unnecessary features
  enabled_cloudwatch_logs_exports = []
  auto_minor_version_upgrade      = false

  tags = {
    Name        = "${var.project_name}-${var.environment}-postgres-inventory"
    Environment = var.environment
    Service     = "inventory"
  }
}