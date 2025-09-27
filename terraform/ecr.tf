# terraform/ecr.tf
# Basic ECR repositories for container images

# ECR Repositories for all services
resource "aws_ecr_repository" "repositories" {
  for_each = local.enable_prod ? {
    user_service     = "user-service"
    inventory_service = "inventory-service"
    order_service    = "order-service"
    auth_service     = "auth-service"
    gateway          = "gateway"
    frontend         = "frontend"
  } : {}

  name         = "${local.resource_prefix}-${each.value}"
  force_delete = true  # Allow deletion even with images
}