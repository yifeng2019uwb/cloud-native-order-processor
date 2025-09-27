# terraform/redis.tf
# Redis configuration for both local K8s and AWS EKS

# ====================
# AWS ELASTICACHE REDIS (prod environment only)
# ====================

# ElastiCache subnet group (required for VPC)
resource "aws_elasticache_subnet_group" "redis" {
  count = local.enable_prod ? 1 : 0

  name       = local.redis_names.subnet_group
  subnet_ids = aws_subnet.private[*].id

  tags = local.common_tags
}

# Security group for Redis
resource "aws_security_group" "redis" {
  count = local.enable_prod ? 1 : 0

  name_prefix = "${local.resource_prefix}-redis-"
  vpc_id      = aws_vpc.main[0].id

  # Allow Redis port from EKS cluster
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster[0].id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = local.redis_names.security_group
  })
}

# Single ElastiCache node (most cost-effective)
resource "aws_elasticache_cluster" "redis" {
  count = local.enable_prod ? 1 : 0

  cluster_id           = local.redis_names.cluster
  engine               = "redis"
  node_type            = "cache.t3.micro"  # Free tier eligible
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis[0].name
  security_group_ids   = [aws_security_group.redis[0].id]

  # Disable SSL for simplicity in personal project
  transit_encryption_enabled = false

  # Minimal settings for personal project
  maintenance_window = "sun:05:00-sun:06:00"

  tags = local.common_tags
}

# ====================
# REDIS IAM ACCESS POLICY
# ====================

# IAM policy for Redis access (ElastiCache)
resource "aws_iam_policy" "redis_access" {
  count = local.enable_prod ? 1 : 0

  name        = local.iam_names.service_redis_role
  description = "Access to ElastiCache Redis for order processor"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "elasticache:DescribeCacheClusters",
          "elasticache:DescribeReplicationGroups"
        ]
        Resource = [
          aws_elasticache_cluster.redis[0].arn
        ]
      }
    ]
  })
}

# Attach Redis policy to application role
resource "aws_iam_role_policy_attachment" "application_redis" {
  count = local.enable_prod ? 1 : 0

  role       = aws_iam_role.k8s_sa.name
  policy_arn = aws_iam_policy.redis_access[0].arn
}