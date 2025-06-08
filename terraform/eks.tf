# ===== FARGATE-ONLY EKS (No EC2 instances to manage) =====
# eks.tf
resource "aws_eks_cluster" "main" {
  name     = "${var.project_name}-${var.environment}-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.28"

  vpc_config {
    subnet_ids              = concat(aws_subnet.private[*].id, aws_subnet.public[*].id)  # Use all subnets
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]
  }

  # Minimal logging to reduce costs
  enabled_cluster_log_types = ["api"]

  tags = {
    Name = "${var.project_name}-${var.environment}-cluster"
  }

  depends_on = [aws_iam_role_policy_attachment.eks_cluster_policy]
}

# Fargate Profile (Serverless containers - pay only when running)
resource "aws_eks_fargate_profile" "main" {
  cluster_name           = aws_eks_cluster.main.name
  fargate_profile_name   = "${var.project_name}-${var.environment}-fargate"
  pod_execution_role_arn = aws_iam_role.fargate_pod_execution.arn
  subnet_ids             = aws_subnet.private[*].id  # Fargate runs in private subnets only

  selector {
    namespace = "order-processor"
  }

  selector {
    namespace = "kube-system"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-fargate"
  }

  depends_on = [
    aws_iam_role_policy_attachment.fargate_pod_execution_policy
  ]
}
