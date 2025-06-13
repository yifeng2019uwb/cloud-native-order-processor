# ===== Variables Configuration =====
# variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "order-processor"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "orderuser"
}

# No db_password variable needed - handled by Secrets Manager

# COST OPTIMIZATION: Add cost profile variable for flexible cost control
variable "cost_profile" {
  description = "Cost optimization profile: minimal, learning, prod, or production"
  type        = string
  default     = "prod"

  validation {
    condition = contains(["minimal", "learning", "prod", "production"], var.cost_profile)
    error_message = "Cost profile must be minimal, learning, or production."
  }
}