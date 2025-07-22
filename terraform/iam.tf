# terraform/iam.tf
# Simple IAM roles

# ====================
# EKS ROLES (prod environment)
# ====================

# EKS cluster role
resource "aws_iam_role" "eks_cluster" {
  count = local.enable_prod ? 1 : 0

  name = "${local.resource_prefix}-eks-cluster-role"

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

# EKS OIDC Provider for service account authentication
resource "aws_iam_openid_connect_provider" "eks" {
  count = local.enable_prod ? 1 : 0

  url = "https://oidc.eks.${data.aws_region.current.name}.amazonaws.com/id/${aws_eks_cluster.main[0].id}"

  client_id_list = ["sts.amazonaws.com"]

  thumbprint_list = [
    "9e99a48a9960b14926bb7f3b02e22da2b0ab7280"
  ]

  tags = local.common_tags
}



# ====================
# APPLICATION SERVICE ROLE (for local K8s)
# ====================

# IAM User for application role assumption
resource "aws_iam_user" "application_user" {
  name = "${local.resource_prefix}-application-user"

  tags = merge(local.common_tags, {
    Purpose = "Application Role Assumption"
  })
}

# IAM Policy for the user to assume the application role
resource "aws_iam_policy" "assume_application_role" {
  name = "${local.resource_prefix}-assume-application-role"
  description = "Policy to allow assuming the application service role"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Resource = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.resource_prefix}-application-service-role"
      }
    ]
  })
}

# Attach the assume role policy to the user
resource "aws_iam_user_policy_attachment" "application_user_assume_role" {
  user       = aws_iam_user.application_user.name
  policy_arn = aws_iam_policy.assume_application_role.arn
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

# IAM Role for application services (Kubernetes pods)
resource "aws_iam_role" "application_service" {
  name = "${local.resource_prefix}-application-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_user.application_user.arn
        }
        Action = "sts:AssumeRole"
      },
      {
        Effect = "Allow"
        Principal = {
          Federated = local.enable_prod ? aws_iam_openid_connect_provider.eks[0].arn : null
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = local.enable_prod ? {
          StringEquals = {
            "${replace(aws_iam_openid_connect_provider.eks[0].url, "https://", "")}:sub" = "system:serviceaccount:order-processor:order-processor-sa"
          }
        } : null
      }
    ]
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
  name = "${local.resource_prefix}-sqs-access"
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
  name = "${local.resource_prefix}-sns-access"
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
  name = "${local.resource_prefix}-ecr-access"
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
  name = "${local.resource_prefix}-secrets-access"
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
  role       = aws_iam_role.application_service.name
  policy_arn = aws_iam_policy.sqs_access.arn
}

resource "aws_iam_role_policy_attachment" "application_sns" {
  role       = aws_iam_role.application_service.name
  policy_arn = aws_iam_policy.sns_access.arn
}

resource "aws_iam_role_policy_attachment" "application_ecr" {
  role       = aws_iam_role.application_service.name
  policy_arn = aws_iam_policy.ecr_access.arn
}

resource "aws_iam_role_policy_attachment" "application_secrets" {
  role       = aws_iam_role.application_service.name
  policy_arn = aws_iam_policy.secrets_access.arn
}
