# terraform/locals.tf
# Simple logic for personal project

locals {
  # Feature flags
  enable_kubernetes = var.environment == "prod"
  enable_vpc = var.environment == "prod"

  # Infrastructure
  create_vpc = local.enable_vpc

  # Data lifecycle configuration (1 days = 1 years in personal project)
  data_lifecycle = {
    retention_days = 10    # Keep data for 10 days (equivalent to 10 years)
    archive_days   = 3    # Move to S3 after 3 day (equivalent to 3 year)
  }

  # Naming
  resource_prefix = "${var.project_name}-${var.environment}"

  # Tags
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}