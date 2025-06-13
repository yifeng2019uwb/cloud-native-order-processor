# terraform/variables.tf
# Essential variables for profile-aware infrastructure

# ====================
# REQUIRED VARIABLES
# ====================

variable "environment" {
  description = "Environment name (dev or prod)"
  type        = string
}

# ====================
# BASIC CONFIGURATION
# ====================

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "order-processor"
}

variable "resource_prefix" {
  description = "Resource prefix (auto-generated if empty)"
  type        = string
  default     = ""
}

# ====================
# DATABASE CONFIGURATION
# ====================

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "orderuser"
  sensitive   = true
}
