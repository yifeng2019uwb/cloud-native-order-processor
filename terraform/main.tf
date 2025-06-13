# terraform/main.tf
# Main Terraform configuration with profile support
# Foundation configuration only - specific resources in separate files

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      Profile     = var.profile
      ComputeType = var.compute_type
      ManagedBy   = "terraform"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Available AZs for the region
data "aws_availability_zones" "available" {
  state = "available"
}

# Local values for common configurations
# locals {
#   account_id = data.aws_caller_identity.current.account_id
#   region     = data.aws_region.current.name

#   # Common tags
#   common_tags = {
#     Project     = var.project_name
#     Environment = var.environment
#     Profile     = var.profile
#     ComputeType = var.compute_type
#     ManagedBy   = "terraform"
#   }

  # Resource naming
#   resource_prefix = "${var.project_name}-${var.environment}"

#   # Profile-specific configurations
#   is_lambda_profile = var.compute_type == "lambda"
#   is_k8s_profile    = var.compute_type == "kubernetes"

#   # Database configuration
#   db_config = {
#     engine         = "postgres"
#     engine_version = "15.4"
#     port          = 5432
#     database_name = "orderprocessor"
#     username      = "orderuser"
#   }
# }

# Random password for database (used by RDS resources)
# resource "random_password" "db_password" {
#   length  = 16
#   special = true
# }