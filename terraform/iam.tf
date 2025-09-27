# terraform/iam.tf
# Simple IAM roles

# ====================
# EKS ROLES (prod environment)
# ====================

# EKS cluster role
resource "aws_iam_role" "eks_cluster" {
  count = local.enable_prod ? 1 : 0

  name = local.iam_names.eks_cluster_role

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  count = local.enable_prod ? 1 : 0

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster[0].name
}

# EKS Node Group role
resource "aws_iam_role" "eks_node_group" {
  count = local.enable_prod ? 1 : 0

  name = "${local.resource_prefix}-eks-node-group-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  count = local.enable_prod ? 1 : 0

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node_group[0].name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  count = local.enable_prod ? 1 : 0

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node_group[0].name
}

resource "aws_iam_role_policy_attachment" "eks_container_registry_policy" {
  count = local.enable_prod ? 1 : 0

  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_node_group[0].name
}

# Get the OIDC issuer thumbprint
data "tls_certificate" "eks" {
  count = local.enable_prod ? 1 : 0
  url = aws_eks_cluster.main[0].identity[0].oidc[0].issuer
}

# EKS OIDC Provider for service account authentication
resource "aws_iam_openid_connect_provider" "eks" {
  count = local.enable_prod ? 1 : 0

  url = aws_eks_cluster.main[0].identity[0].oidc[0].issuer

  client_id_list = ["sts.amazonaws.com"]

  thumbprint_list = [
    data.tls_certificate.eks[0].certificates[0].sha1_fingerprint
  ]

  # Force recreation when cluster ID changes
  lifecycle {
    replace_triggered_by = [aws_eks_cluster.main[0].id]
  }

  tags = local.common_tags
}



# ====================
# APPLICATION SERVICE ROLE (for local K8s)
# ====================

# IAM User for application role assumption
resource "aws_iam_user" "application_user" {
  name = local.iam_names.application_user

  tags = merge(local.common_tags, {
    Purpose = "Application Role Assumption"
  })
}

# IAM Policy for the user to assume the application role
resource "aws_iam_policy" "assume_k8s_sa_role" {
  name = local.iam_names.k8s_sa_role
  description = "Policy to allow assuming the Kubernetes service account role"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Resource = aws_iam_role.k8s_sa.arn
      }
    ]
  })
}

# Attach the assume role policy to the user
resource "aws_iam_user_policy_attachment" "application_user_assume_role" {
  user       = aws_iam_user.application_user.name
  policy_arn = aws_iam_policy.assume_k8s_sa_role.arn
}

# Access key for local K8s (only when not using EKS)
resource "aws_iam_access_key" "application_user" {
  count = local.enable_prod ? 0 : 1  # Only create for local dev
  user  = aws_iam_user.application_user.name

  # Lifecycle to prevent recreation unless user changes
  lifecycle {
    create_before_destroy = true
  }
}

# IAM Role for Kubernetes Service Accounts (IRSA)
resource "aws_iam_role" "k8s_sa" {
  name = local.iam_names.k8s_sa_role

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat([
      {
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_user.application_user.arn
        }
        Action = "sts:AssumeRole"
      }
    ], local.enable_prod ? [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.eks[0].arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${replace(aws_iam_openid_connect_provider.eks[0].url, "https://", "")}:sub" = "system:serviceaccount:order-processor:order-processor-sa"
          }
        }
      }
    ] : [])
  })

  tags = merge(local.common_tags, {
    Purpose = "Application Service Access"
  })
}

# ====================
# CORE APPLICATION ROLE AND USER
# ====================
# Note: Resource-specific policies are now in their respective resource files
# for better organization and understanding of what each policy does.

# SQS Access Policy
resource "aws_iam_policy" "sqs_access" {
  name = local.iam_names.service_sqs_role
  description = "Access to SQS queues for order processor"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:GetQueueUrl"
        ]
        Resource = [
          aws_sqs_queue.order_processing.arn,
          aws_sqs_queue.order_dlq.arn
        ]
      }
    ]
  })
}

# SNS Access Policy
resource "aws_iam_policy" "sns_access" {
  name = local.iam_names.service_sns_role
  description = "Access to SNS topics for order processor"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sns:Publish",
          "sns:GetTopicAttributes"
        ]
        Resource = [
          aws_sns_topic.order_events.arn
        ]
      }
    ]
  })
}

# ECR Access Policy (for pulling images)
resource "aws_iam_policy" "ecr_access" {
  name = local.iam_names.service_ecr_role
  description = "Access to ECR repositories for order processor"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:DescribeRepositories"
        ]
        Resource = [
          "arn:aws:ecr:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:repository/${local.resource_prefix}-*"
        ]
      }
    ]
  })
}

# Secrets Manager Access Policy (for database credentials)
resource "aws_iam_policy" "secrets_access" {
  name = local.iam_names.service_secrets_role
  description = "Access to Secrets Manager for order processor"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          "arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:${local.resource_prefix}-*"
        ]
      }
    ]
  })
}



# ====================
# ATTACH POLICIES TO APPLICATION ROLE
# ====================
# Note: Resource-specific policy attachments are now in their respective resource files.

resource "aws_iam_role_policy_attachment" "application_sqs" {
  role       = aws_iam_role.k8s_sa.name
  policy_arn = aws_iam_policy.sqs_access.arn
}

resource "aws_iam_role_policy_attachment" "application_sns" {
  role       = aws_iam_role.k8s_sa.name
  policy_arn = aws_iam_policy.sns_access.arn
}

resource "aws_iam_role_policy_attachment" "application_ecr" {
  role       = aws_iam_role.k8s_sa.name
  policy_arn = aws_iam_policy.ecr_access.arn
}

resource "aws_iam_role_policy_attachment" "application_secrets" {
  role       = aws_iam_role.k8s_sa.name
  policy_arn = aws_iam_policy.secrets_access.arn
}
