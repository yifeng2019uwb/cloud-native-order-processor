# ===== FARGATE-ONLY EKS WITH EASY DESTROY =====
# eks.tf

resource "aws_kms_key" "eks" {
  description             = "EKS Secret Encryption"
  deletion_window_in_days = 7
}

resource "aws_kms_alias" "eks" {
  name          = "alias/eks-${var.project_name}-${var.environment}"
  target_key_id = aws_kms_key.eks.key_id
}

resource "aws_eks_cluster" "main" {
  count = local.enable_kubernetes ? 1 : 0

  name     = "${var.project_name}-${var.environment}-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.28"

encryption_config {
  provider {
    key_arn = aws_kms_key.eks.arn
  }
  resources = ["secrets"]
}


  vpc_config {
    subnet_ids              = concat(aws_subnet.private[*].id, aws_subnet.public[*].id)
    endpoint_private_access = true
    # ORIGINAL: Public access disabled (more secure but harder for learning)
    endpoint_public_access  = false
    public_access_cidrs     = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
  }

  # Minimal logging to reduce costs and easier cleanup
  # ORIGINAL: All logging disabled (already cost-optimized)
  enabled_cluster_log_types = [] # Disable all logging for easier cleanup

  tags = {
    Name = "${var.project_name}-${var.environment}-cluster"
  }

  # depends_on = [aws_iam_role_policy_attachment.eks_cluster_policy]

  # Ensure clean deletion
  timeouts {
    delete = "30m"
  }
}

# Fargate Profile with easy cleanup
# ORIGINAL: Fargate-only deployment (expensive ~$0.04048/vCPU/hour + $0.004445/GB/hour)
resource "aws_eks_fargate_profile" "main" {
  count = var.compute_type == "kubernetes" ? 1 : 0

  cluster_name           = aws_eks_cluster.main[0].name
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

  # depends_on = [
  #   aws_iam_role_policy_attachment.fargate_pod_execution_policy
  # ]

  # Ensure clean deletion
  timeouts {
    create = "30m"
    delete = "30m"
  }
}
