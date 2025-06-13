# ===== IAM ROLES (env-aware with proper dependencies) =====
# iam.tf

# ====================
# EKS CLUSTER ROLES (Kubernetes only)
# ====================

# EKS Cluster Service Role
resource "aws_iam_role" "eks_cluster" {
  count = local.enable_kubernetes ? 1 : 0

  name = "${var.project_name}-${var.environment}-eks-cluster-role"

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

  tags = {
    Name        = "${var.project_name}-${var.environment}-eks-cluster-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Attach EKS Cluster Policy
resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  count = local.enable_kubernetes ? 1 : 0

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster[0].name
}

# ====================
# FARGATE POD EXECUTION ROLES (Kubernetes only)
# ====================

# Fargate Pod Execution Role
resource "aws_iam_role" "fargate_pod_execution" {
  count = local.enable_kubernetes ? 1 : 0

  name = "${var.project_name}-${var.environment}-fargate-pod-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks-fargate-pods.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-fargate-pod-execution-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Attach Fargate Pod Execution Policy
resource "aws_iam_role_policy_attachment" "fargate_pod_execution_policy" {
  count = local.enable_kubernetes ? 1 : 0

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSFargatePodExecutionRolePolicy"
  role       = aws_iam_role.fargate_pod_execution[0].name
}

# ====================
# EKS OIDC AND SERVICE ACCOUNT ROLES (Kubernetes only)
# ====================

# Get OIDC issuer certificate
data "tls_certificate" "eks" {
  count = local.enable_kubernetes ? 1 : 0
  url   = aws_eks_cluster.main[0].identity[0].oidc[0].issuer
}

# Create OIDC Identity Provider
resource "aws_iam_openid_connect_provider" "eks" {
  count = local.enable_kubernetes ? 1 : 0

  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks[0].certificates[0].sha1_fingerprint]
  url             = data.tls_certificate.eks[0].url

  tags = {
    Name        = "${var.project_name}-${var.environment}-eks-oidc"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Service Account Role for Order Service (Kubernetes pods)
resource "aws_iam_role" "order_service" {
  count = local.enable_kubernetes ? 1 : 0

  name = "${var.project_name}-${var.environment}-order-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.eks[0].arn
        }
        Condition = {
          StringEquals = {
            "${replace(aws_iam_openid_connect_provider.eks[0].url, "https://", "")}:sub" = "system:serviceaccount:order-processor:order-service"
            "${replace(aws_iam_openid_connect_provider.eks[0].url, "https://", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-order-service-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Policy for Order Service (access to shared resources)
resource "aws_iam_policy" "order_service_policy" {
  count = local.enable_kubernetes ? 1 : 0

  name        = "${var.project_name}-${var.environment}-order-service-policy"
  description = "Policy for order service running in EKS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = [
          "${aws_s3_bucket.events.arn}/*",
          "${aws_s3_bucket.backups.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.order_events.arn
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage"
        ]
        Resource = aws_sqs_queue.order_processing.arn
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.db_credentials.arn
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-order-service-policy"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Attach policy to order service role
resource "aws_iam_role_policy_attachment" "order_service_policy" {
  count = local.enable_kubernetes ? 1 : 0

  role       = aws_iam_role.order_service[0].name
  policy_arn = aws_iam_policy.order_service_policy[0].arn
}

# ====================
# LAMBDA EXECUTION ROLES (Lambda only)
# ====================
# Note: Lambda IAM resources are defined in lambda.tf to keep them co-located
# This avoids circular dependencies and keeps related resources together

# ====================
# SHARED RESOURCE ACCESS POLICIES
# ====================

# Shared policy for accessing common resources (used by both Lambda and EKS)
resource "aws_iam_policy" "shared_resources_access" {
  name        = "${var.project_name}-${var.environment}-shared-resources-policy"
  description = "Policy for accessing shared resources (S3, SNS, SQS, Secrets)"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.events.arn,
          "${aws_s3_bucket.events.arn}/*",
          aws_s3_bucket.backups.arn,
          "${aws_s3_bucket.backups.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish",
          "sns:GetTopicAttributes"
        ]
        Resource = aws_sns_topic.order_events.arn
      },
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
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = aws_secretsmanager_secret.db_credentials.arn
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.region}:*:log-group:/aws/*"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-shared-resources-policy"
    Environment = var.environment
    Project     = var.project_name
  }
}