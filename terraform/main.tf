# Configure the AWS Provider
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "yifeng2019uwb-order-processor-terraform-state" 
    key            = "terraform.tfstate" 
    region         = "us-west-2"        
    encrypt        = true              
  }
}

provider "aws" {
  region = var.aws_region
}