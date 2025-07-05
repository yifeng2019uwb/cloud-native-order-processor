# terraform/variables.tf

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

# ====================
# SIMPLE TLS ADDITION (just this one new variable)
# ====================

variable "enable_api_https_only" {
  description = "Force HTTPS-only for API Gateway (TLS 1.2+)"
  type        = bool
  default     = true
}