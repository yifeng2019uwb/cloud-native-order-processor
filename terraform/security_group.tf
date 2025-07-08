# terraform/security_group.tf
# Simple security groups - only what's needed

# Security group for EKS pods (prod environment)
resource "aws_security_group" "eks_pods" {
  count = local.enable_kubernetes ? 1 : 0

  name_prefix = "${local.resource_prefix}-eks-pods-"
  vpc_id      = aws_vpc.main[0].id
  description = "Security group for EKS pods"

  ingress {
    description = "All traffic from VPC"
    from_port   = 0
    to_port     = 65535
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