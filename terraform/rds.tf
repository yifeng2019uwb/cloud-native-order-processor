# --- Database: RDS PostgreSQL ---
resource "aws_db_subnet_group" "db_subnet_group" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = [aws_subnet.private_subnet_1.id] # Place RDS in private subnets

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "${var.project_name}-rds-sg"
  description = "Allow inbound access to RDS instance"
  vpc_id      = aws_vpc.main_vpc.id

  ingress {
    from_port   = 5432 # PostgreSQL default port
    to_port     = 5432
    protocol    = "tcp"
    # Allow access from any resource within the VPC (e.g., your EKS pods later)
    cidr_blocks = [aws_vpc.main_vpc.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

resource "aws_db_instance" "postgres_db" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "14.7" # Choose a stable version
  instance_class       = "db.t3.micro" # Smallest instance for testing
  identifier           = "${var.project_name}-postgres-db"
  username             = var.db_username
  password             = var.db_password
  db_subnet_group_name = aws_db_subnet_group.db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot  = true # Set to false for production
  publicly_accessible  = false # Crucial: Keep private in VPC
  multi_az             = false # For testing, can be true for production
  final_snapshot_identifier = "${var.project_name}-final-snapshot" # Required if skip_final_snapshot is false
  # Enable deletion protection for production
  # deletion_protection = true

  tags = {
    Name        = "${var.project_name}-postgres-db"
    Environment = var.environment
  }
}