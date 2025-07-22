# terraform/security_group.tf
# Simple security groups - only what's needed

# Security Group for EKS cluster
resource "aws_security_group" "eks_cluster" {
  count = local.enable_prod ? 1 : 0

  name_prefix = "${local.resource_prefix}-eks-cluster-"
  vpc_id      = aws_vpc.main[0].id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = local.sg_names.eks_cluster
  })
}