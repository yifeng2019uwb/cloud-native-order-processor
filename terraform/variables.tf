# Variables
variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-west-2" # Or your preferred region
}

variable "project_name" {
  description = "A unique name for your project, used in resource tags and names."
  type        = string
  default     = "ecommerce-order" # Can be changed
}

variable "environment" {
  description = "The environment (e.g., dev, test, prod)."
  type        = string
  default     = "dev"
}

variable "vpc_cidr_block" {
  description = "The CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_1_cidr" {
  description = "The CIDR block for public subnet 1."
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_1_cidr" {
  description = "The CIDR block for private subnet 1 (for databases, EKS nodes)."
  type        = string
  default     = "10.0.2.0/24"
}

# DB Credentials (Sensitive - do not hardcode in production!)
variable "db_username" {
  description = "Username for the PostgreSQL database."
  type        = string
  default     = "postgresadmin" # Change this!
}

variable "db_password" {
  description = "Password for the PostgreSQL database."
  type        = string
  sensitive   = true # Mark as sensitive to prevent outputting to console
}