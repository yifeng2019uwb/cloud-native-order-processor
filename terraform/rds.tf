# RDS PostgreSQL Instance - Order Service
resource "aws_db_instance" "postgres_order" {
  identifier = "${var.project_name}-${var.environment}-postgres-order"

  engine         = "postgres"
  engine_version = "15"
  instance_class = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "orderdb"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_order.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:00-sun:05:00"

  skip_final_snapshot = true
  deletion_protection = false

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
  instance_class = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "productdb"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_product.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window           = "03:30-04:30"
  maintenance_window      = "sun:05:00-sun:06:00"

  skip_final_snapshot = true
  deletion_protection = false

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
  instance_class = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "inventorydb"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_inventory.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window           = "04:00-05:00"
  maintenance_window      = "sun:06:00-sun:07:00"

  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name        = "${var.project_name}-${var.environment}-postgres-inventory"
    Environment = var.environment
    Service     = "inventory"
  }
}