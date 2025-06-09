# ===== FARGATE-ONLY EKS WITH EASY DESTROY =====
# eks.tf
resource "aws_eks_cluster" "main" {
  name     = "${var.project_name}-${var.environment}-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.28"

  vpc_config {
    subnet_ids              = concat(aws_subnet.private[*].id, aws_subnet.public[*].id)
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]
  }

  # Minimal logging to reduce costs and easier cleanup
  enabled_cluster_log_types = []  # Disable all logging for easier cleanup

  tags = {
    Name = "${var.project_name}-${var.environment}-cluster"
  }

  depends_on = [aws_iam_role_policy_attachment.eks_cluster_policy]

  # Ensure clean deletion
  timeouts {
    delete = "30m"
  }
}

# Fargate Profile with easy cleanup
resource "aws_eks_fargate_profile" "main" {
  cluster_name           = aws_eks_cluster.main.name
  fargate_profile_name   = "${var.project_name}-${var.environment}-fargate"
  pod_execution_role_arn = aws_iam_role.fargate_pod_execution.arn
  subnet_ids             = aws_subnet.private[*].id

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

  # Ensure clean deletion
  timeouts {
    create = "30m"
    delete = "30m"
  }
}