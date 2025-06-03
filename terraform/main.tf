# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
  # If using a specific profile, uncomment and set:
  # profile = "terraform-user"
}