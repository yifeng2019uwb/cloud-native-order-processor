# ===== ECR REPOSITORY WITH FORCE DELETE =====
# ecr.tf
resource "aws_ecr_repository" "order_api" {
  name                 = "${var.project_name}-order-api"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = true # FORCE DELETE - remove all images when destroying

  # Disable image scanning for cost savings
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-order-api"
  }
}

# Aggressive cleanup policy - keep minimal images
resource "aws_ecr_lifecycle_policy" "order_api" {
  repository = aws_ecr_repository.order_api.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Delete untagged images immediately"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Keep only last 2 images for easy cleanup"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 2 # Keep only 2 images instead of 3
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}