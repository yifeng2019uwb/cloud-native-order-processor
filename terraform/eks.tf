# ===== FARGATE-ONLY EKS WITH PROPER DEPENDENCIES =====
# eks.tf

# KMS key for EKS secrets encryption
resource "aws_kms_key" "eks" {
  count = local.enable_kubernetes ? 1 : 0

  description             = "EKS Secret Encryption"
  deletion_window_in_days = 7

  tags = {
    Name        = "${var.project_name}-${var.environment}-eks-kms"
    Environment = var.environment
    Project     = var.project_name
  }
}

# KMS alias for easier reference
resource "aws_kms_alias" "eks" {
  count = local.enable_kubernetes ? 1 : 0

  name          = "alias/eks-${var.project_name}-${var.environment}"
  target_key_id = aws_kms_key.eks[0].key_id

  depends_on = [aws_kms_key.eks]
}

# EKS Cluster
resource "aws_eks_cluster" "main" {
  count = local.enable_kubernetes ? 1 : 0

  name     = "${var.project_name}-${var.environment}-cluster"
  role_arn = aws_iam_role.eks_cluster[0].arn
  version  = "1.28"

  # Secrets encryption using KMS
  encryption_config {
    provider {
      key_arn = aws_kms_key.eks[0].arn
    }
    resources = ["secrets"]
  }

  # VPC configuration
  vpc_config {
    subnet_ids              = concat(aws_subnet.private[*].id, aws_subnet.public[*].id)
    endpoint_private_access = true
    endpoint_public_access  = false  # Private access only
    public_access_cidrs     = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
  }

  # Minimal logging to reduce costs and easier cleanup
  enabled_cluster_log_types = [] # Disable all logging for cost optimization

  # Proper dependencies
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_vpc.main,
    aws_subnet.private,
    aws_subnet.public,
    aws_kms_key.eks
  ]

  # Ensure clean deletion
  timeouts {
    create = "30m"
    update = "30m"
    delete = "30m"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-cluster"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Fargate Profile for running pods
resource "aws_eks_fargate_profile" "main" {
  count = local.enable_kubernetes ? 1 : 0

  cluster_name           = aws_eks_cluster.main[0].name
  fargate_profile_name   = "${var.project_name}-${var.environment}-fargate"
  pod_execution_role_arn = aws_iam_role.fargate_pod_execution[0].arn
  subnet_ids             = aws_subnet.private[*].id

  # Selector for order-processor namespace
  selector {
    namespace = "order-processor"
    labels = {
      app = "order-service"
    }
  }

  # Selector for kube-system namespace (required for system pods)
  selector {
    namespace = "kube-system"
  }

  # Selector for default namespace (for testing)
  selector {
    namespace = "default"
  }

  # Proper dependencies
  depends_on = [
    aws_iam_role_policy_attachment.fargate_pod_execution_policy,
    aws_eks_cluster.main,
    aws_subnet.private
  ]

  # Ensure clean deletion
  timeouts {
    create = "30m"
    delete = "30m"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-fargate"
    Environment = var.environment
    Project     = var.project_name
  }
}

# EKS Add-ons for basic functionality
resource "aws_eks_addon" "coredns" {
  count = local.enable_kubernetes ? 1 : 0

  cluster_name             = aws_eks_cluster.main[0].name
  addon_name               = "coredns"
  addon_version            = "v1.10.1-eksbuild.5"  # Compatible with EKS 1.28
  resolve_conflicts        = "OVERWRITE"
  service_account_role_arn = null  # Use default service account

  depends_on = [
    aws_eks_fargate_profile.main
  ]

  timeouts {
    create = "20m"
    update = "20m"
    delete = "20m"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-coredns"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_eks_addon" "kube_proxy" {
  count = local.enable_kubernetes ? 1 : 0

  cluster_name             = aws_eks_cluster.main[0].name
  addon_name               = "kube-proxy"
  addon_version            = "v1.28.2-eksbuild.2"  # Compatible with EKS 1.28
  resolve_conflicts        = "OVERWRITE"
  service_account_role_arn = null  # Use default service account

  depends_on = [
    aws_eks_cluster.main
  ]

  timeouts {
    create = "20m"
    update = "20m"
    delete = "20m"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-kube-proxy"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_eks_addon" "vpc_cni" {
  count = local.enable_kubernetes ? 1 : 0

  cluster_name             = aws_eks_cluster.main[0].name
  addon_name               = "vpc-cni"
  addon_version            = "v1.15.1-eksbuild.1"  # Compatible with EKS 1.28
  resolve_conflicts        = "OVERWRITE"
  service_account_role_arn = null  # Use default service account

  depends_on = [
    aws_eks_cluster.main
  ]

  timeouts {
    create = "20m"
    update = "20m"
    delete = "20m"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-vpc-cni"
    Environment = var.environment
    Project     = var.project_name
  }
}