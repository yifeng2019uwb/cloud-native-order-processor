# terraform/ecr.tf
# Simple ECR repository for container images

# ECR Repository for order API
resource "aws_ecr_repository" "order_api" {
  count = local.enable_prod ? 1 : 0

  name                 = "${local.resource_prefix}-order-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.common_tags
}

# ECR Repository for inventory service
resource "aws_ecr_repository" "inventory_service" {
  count = local.enable_prod ? 1 : 0

  name                 = "${local.resource_prefix}-inventory-service"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.common_tags
}

# Lifecycle policy to clean up old images
resource "aws_ecr_lifecycle_policy" "order_api" {
  count = local.enable_prod ? 1 : 0

  repository = aws_ecr_repository.order_api[0].name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep only last 3 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 3
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}