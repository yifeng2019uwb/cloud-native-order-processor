# ===== ECR REPOSITORY =====
# ecr.tf
resource "aws_ecr_repository" "order_api" {
  name                 = "${var.project_name}-order-api"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  # Disable image scanning for cost savings
  image_scanning_configuration {
    scan_on_push = false
  }

  tags = {
    Name = "${var.project_name}-order-api"
  }
}

# Aggressive cleanup policy
resource "aws_ecr_lifecycle_policy" "order_api" {
  repository = aws_ecr_repository.order_api.name

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