# locals.tf - Essential conditional logic only

locals {
  # Basic feature flags
  enable_kubernetes = var.environment == "prod"
  enable_lambda     = var.environment == "dev"

  # Networking
  create_vpc = local.enable_kubernetes
  create_nat = local.enable_kubernetes

  # Resource naming
  resource_prefix = var.resource_prefix != "" ? var.resource_prefix : "${var.project_name}-${var.environment}"

  # Common tags
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}