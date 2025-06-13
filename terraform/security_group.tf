# security_group.tf - Basic security groups only

# RDS Security Group (only when VPC exists)
resource "aws_security_group" "rds" {
  count = local.create_vpc ? 1 : 0

  name_prefix = "${local.resource_prefix}-rds-"
  vpc_id      = aws_vpc.main[0].id
  description = "Security group for RDS PostgreSQL"

  ingress {
    description = "PostgreSQL from VPC"
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

  tags = local.common_tags

  lifecycle {
    create_before_destroy = true
  }
}