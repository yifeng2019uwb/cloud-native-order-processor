# terraform/eks.tf
# Simple EKS cluster for prod environment

# EKS Cluster
resource "aws_eks_cluster" "main" {
  count = local.enable_kubernetes ? 1 : 0

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

# Fargate Profile
resource "aws_eks_fargate_profile" "main" {
  count = local.enable_kubernetes ? 1 : 0

  cluster_name           = aws_eks_cluster.main[0].name
  fargate_profile_name   = "${local.resource_prefix}-fargate"
  pod_execution_role_arn = aws_iam_role.fargate_pod_execution[0].arn
  subnet_ids             = aws_subnet.private[*].id

  selector {
    namespace = "default"
  }

  selector {
    namespace = "order-processor"
  }

  depends_on = [
    aws_iam_role_policy_attachment.fargate_pod_execution_policy
  ]

  tags = local.common_tags
}