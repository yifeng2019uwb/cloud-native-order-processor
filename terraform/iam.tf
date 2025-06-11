# ===== IAM ROLES (Minimal required permissions) =====
# iam.tf
# EKS Cluster Role
resource "aws_iam_role" "eks_cluster" {
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
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

# Fargate Pod Execution Role
resource "aws_iam_role" "fargate_pod_execution" {
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
}

resource "aws_iam_role_policy_attachment" "fargate_pod_execution_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSFargatePodExecutionRolePolicy"
  role       = aws_iam_role.fargate_pod_execution.name
}

# COST OPTIMIZATION: Add EKS Node Group Role for Spot Instances
# Add these when using spot instances instead of Fargate:
# resource "aws_iam_role" "eks_node_group" {
#   count = var.cost_profile == "minimal" ? 1 : 0  # COST EFFICIENT: Only when using spot instances
#   name  = "${var.project_name}-${var.environment}-eks-node-group-role"
#
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = "sts:AssumeRole"
#         Effect = "Allow"
#         Principal = {
#           Service = "ec2.amazonaws.com"
#         }
#       }
#     ]
#   })
# }
#
# resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
#   count      = var.cost_profile == "minimal" ? 1 : 0  # COST EFFICIENT: Only when using spot instances
#   policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
#   role       = aws_iam_role.eks_node_group[0].name
# }
#
# resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
#   count      = var.cost_profile == "minimal" ? 1 : 0  # COST EFFICIENT: Only when using spot instances
#   policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
#   role       = aws_iam_role.eks_node_group[0].name
# }
#
# resource "aws_iam_role_policy_attachment" "eks_container_registry_policy" {
#   count      = var.cost_profile == "minimal" ? 1 : 0  # COST EFFICIENT: Only when using spot instances
#   policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
#   role       = aws_iam_role.eks_node_group[0].name
# }

# Service Account Role for Applications
data "tls_certificate" "eks" {
  url = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

resource "aws_iam_role" "order_service" {
  name = "${var.project_name}-${var.environment}-order-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.eks.arn
        }
        Condition = {
          StringEquals = {
            "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:sub" = "system:serviceaccount:order-processor:order-service"
            "${replace(aws_iam_openid_connect_provider.eks.url, "https://", "")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })
}

# Minimal policy for order service
# ORIGINAL: Includes SNS and SQS permissions (may not be needed for minimal testing)
resource "aws_iam_role_policy" "order_service_policy" {
  name = "${var.project_name}-${var.environment}-order-service-policy"
  role = aws_iam_role.order_service.id

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
      }
    ]
  })
}

# COST OPTIMIZATION: Minimal permissions policy for cost-conscious profiles
# Comment out the policy above and uncomment below for ultra-minimal permissions:
# resource "aws_iam_role_policy" "order_service_policy" {
#   name = "${var.project_name}-${var.environment}-order-service-policy"
#   role = aws_iam_role.order_service.id
#
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = concat(
#       # Always include S3 access for basic functionality
#       [
#         {
#           Effect = "Allow"
#           Action = [
#             "s3:GetObject",
#             "s3:PutObject"
#           ]
#           Resource = [
#             "${aws_s3_bucket.events.arn}/*",
#             "${aws_s3_bucket.backups.arn}/*"
#           ]
#         }
#       ],
#       # COST EFFICIENT: Only add messaging permissions for learning/production profiles
#       var.cost_profile == "minimal" ? [] : [
#         {
#           Effect = "Allow"
#           Action = [
#             "sns:Publish"
#           ]
#           Resource = aws_sns_topic.order_events.arn
#         },
#         {
#           Effect = "Allow"
#           Action = [
#             "sqs:SendMessage",
#             "sqs:ReceiveMessage",
#             "sqs:DeleteMessage"
#           ]
#           Resource = aws_sqs_queue.order_processing.arn
#         }
#       ]
#     )
#   })
# }