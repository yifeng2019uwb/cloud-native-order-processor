# terraform/locals.tf
# Simple logic for personal project

locals {
  # Feature flags
  enable_kubernetes = var.environment == "prod"

  # Infrastructure
  create_vpc = local.enable_kubernetes

  # Naming
  resource_prefix = "${var.project_name}-${var.environment}"

  # Tags
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}