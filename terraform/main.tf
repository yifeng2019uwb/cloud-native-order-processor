# ===== Main Configuration =====
# main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }

  # ORIGINAL S3 backend (works but costs ~$0.023/month per state file)
  backend "s3" {
    bucket  = "yifeng-order-processor-terraform-state"
    key     = "terraform.tfstate"
    region  = "us-west-2"
    encrypt = true
  }

  # COST OPTIMIZATION: For ephemeral environments, use local backend instead
  # Comment out S3 backend above and uncomment below for cost savings:
  # backend "local" {
  #   path = "./terraform.tfstate"
  # }
}

provider "aws" {
  region = var.aws_region

  # ORIGINAL tags (fixed cost profile)
  # default_tags {
  #   tags = {
  #     Project     = var.project_name
  #     Environment = var.environment
  #     ManagedBy   = "Terraform"
  #     CostProfile = "MinimalPractice"  # COST ISSUE: Fixed value, not flexible
  #   }
  # }

  # COST OPTIMIZATION: Variable-based cost profile for flexibility
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      CostProfile = var.cost_profile        # COST EFFICIENT: Use variable for different profiles
      AutoCleanup = "enabled"               # COST EFFICIENT: Tag for CI/CD auto-cleanup
    }
  }
}