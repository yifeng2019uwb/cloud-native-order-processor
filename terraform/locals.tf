# locals.tf - Centralized conditional logic
locals {
  # Profile-based feature flags
  enable_kubernetes = var.compute_type == "kubernetes"
  enable_lambda     = var.compute_type == "lambda"

  # Networking configuration
  create_vpc = local.enable_kubernetes
  create_nat = local.enable_kubernetes && var.profile == "regular"

  # Common tags
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    Profile     = var.profile
    ComputeType = var.compute_type
    ManagedBy   = "terraform"
  }
}