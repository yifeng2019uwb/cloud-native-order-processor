# terraform/variables.tf
# Variables for profile-aware infrastructure deployment

# Database credentials
variable "db_username" {
  description = "Database master username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

# Required variables
variable "environment" {
  description = "Environment name (dev or prod)"
  type        = string
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "Environment must be 'dev' or 'prod'."
  }
}

variable "profile" {
  description = "Resource profile determining infrastructure scale and cost"
  type        = string
  validation {
    condition     = contains(["minimum", "regular"], var.profile)
    error_message = "Profile must be 'minimum' or 'regular'."
  }
}

variable "compute_type" {
  description = "Compute platform type based on profile"
  type        = string
  validation {
    condition     = contains(["lambda", "kubernetes"], var.compute_type)
    error_message = "Compute type must be 'lambda' or 'kubernetes'."
  }
}

# AWS configuration
variable "region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-west-2"
}

variable "project_name" {
  description = "Name of the project for resource naming and tagging"
  type        = string
  default     = "order-processor"
}

# Resource configuration
variable "resource_prefix" {
  description = "Prefix for resource naming (auto-generated from project_name and environment if not provided)"
  type        = string
  default     = ""
}

variable "availability_zones_count" {
  description = "Number of availability zones to use"
  type        = number
  default     = 2
}

# Optional database configuration (can override defaults)
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_backup_retention_period" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 1
}

# Optional logging configuration
variable "log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 7
}

# Optional S3 configuration
variable "s3_lifecycle_enabled" {
  description = "Enable S3 lifecycle rules for cost optimization"
  type        = bool
  default     = true
}

# Optional security configuration (for future use)
variable "enable_encryption" {
  description = "Enable encryption for supported resources (KMS vs AWS managed)"
  type        = bool
  default     = false  # false for minimum profile cost optimization
}

variable "publicly_accessible_rds" {
  description = "Make RDS instance publicly accessible (true for lambda profile)"
  type        = bool
  default     = null  # Auto-determined based on compute_type
}