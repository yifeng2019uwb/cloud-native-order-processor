# ===== ECR REPOSITORY WITH FORCE DELETE =====
# ecr.tf
resource "aws_ecr_repository" "order_api" {
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

# COST OPTIMIZATION: Conditional image scanning based on cost profile
# Comment out the image_scanning_configuration above and uncomment below:
# image_scanning_configuration {
#   scan_on_push = var.cost_profile == "production"  # COST EFFICIENT: Only scan in production
# }

# Aggressive cleanup policy - keep minimal images
# ORIGINAL: Keep only 2 images (already quite aggressive)
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

# COST OPTIMIZATION: More aggressive cleanup for minimal cost profile
# Comment out the policy above and uncomment below for ultra-aggressive cleanup:
# resource "aws_ecr_lifecycle_policy" "order_api" {
#   repository = aws_ecr_repository.order_api.name
#
#   policy = jsonencode({
#     rules = [
#       {
#         rulePriority = 1
#         description  = "Delete untagged images immediately"
#         selection = {
#           tagStatus   = "untagged"
#           countType   = "sinceImagePushed"
#           countUnit   = "hours"  # COST EFFICIENT: Hours instead of days
#           countNumber = 6        # COST EFFICIENT: 6 hours instead of 1 day
#         }
#         action = {
#           type = "expire"
#         }
#       },
#       {
#         rulePriority = 2
#         description  = "Keep minimal images based on cost profile"
#         selection = {
#           tagStatus   = "any"
#           countType   = "imageCountMoreThan"
#           countNumber = var.cost_profile == "minimal" ? 1 : 2  # COST EFFICIENT: Keep only 1 image for minimal
#         }
#         action = {
#           type = "expire"
#         }
#       },
#       {
#         rulePriority = 3
#         description  = "Delete old images aggressively"
#         selection = {
#           tagStatus   = "any"
#           countType   = "sinceImagePushed"
#           countUnit   = "days"
#           countNumber = var.cost_profile == "minimal" ? 1 : 7  # COST EFFICIENT: Delete after 1 day for minimal
#         }
#         action = {
#           type = "expire"
#         }
#       }
#     ]
#   })
# }