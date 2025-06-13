# ===== ECR REPOSITORY WITH FORCE DELETE =====
# ecr.tf
resource "aws_ecr_repository" "order_api" {
  count = local.enable_kubernetes ? 1 : 0

  name                 = "${var.project_name}-order-api"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = true # FORCE DELETE - remove all images when destroying

  # Disable image scanning for cost savings
  # ORIGINAL: Image scanning enabled (costs extra)
  image_scanning_configuration {
    scan_on_push = true  # COST ISSUE: Scanning costs ~$0.09 per image scan
  }

  tags = {
    Name = "${var.project_name}-order-api"
  }
}

# Aggressive cleanup policy - keep minimal images
# ORIGINAL: Keep only 2 images (already quite aggressive)
resource "aws_ecr_lifecycle_policy" "order_api" {
  count = local.enable_kubernetes ? 1 : 0

  repository = aws_ecr_repository.order_api[0].name

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
