# terraform/ecr.tf
# Simple ECR repository for container images

resource "aws_ecr_repository" "order_api" {
  count = local.enable_kubernetes ? 1 : 0

  name                 = "${var.project_name}-order-api"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = false  # Keep costs down
  }

  tags = local.common_tags
}

# Lifecycle policy to clean up old images
resource "aws_ecr_lifecycle_policy" "order_api" {
  count = local.enable_kubernetes ? 1 : 0

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