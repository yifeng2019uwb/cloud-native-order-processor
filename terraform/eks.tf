# terraform/eks.tf
# Simple EKS cluster for prod environment

# EKS Cluster
resource "aws_eks_cluster" "main" {
  count = local.enable_prod ? 1 : 0

  name     = "${local.resource_prefix}-cluster"
  role_arn = aws_iam_role.eks_cluster[0].arn
  version  = "1.28"

  vpc_config {
    subnet_ids = concat(aws_subnet.private[*].id, aws_subnet.public[*].id)
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]

  tags = local.common_tags
}