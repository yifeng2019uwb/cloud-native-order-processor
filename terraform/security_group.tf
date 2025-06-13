# ===== SECURITY GROUPS =====
# security_group.tf

# RDS Security Group
resource "aws_security_group" "rds" {
  count = local.enable_kubernetes ? 1 : 0

  name_prefix = "${var.project_name}-${var.environment}-rds-"
  vpc_id      = aws_vpc.main[0].id
  description = "Security group for RDS PostgreSQL"

  ingress {
    description = "PostgreSQL from EKS"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main[0].cidr_block]
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  }
}