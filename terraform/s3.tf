# aws-terraform-backend-s3-only/backend.tf

resource "aws_s3_bucket" "terraform_state_bucket" {
  bucket = "yifeng2019uwb-order-processor-terraform-state"
  tags = {
    Name        = "TerraformStateBucket"
    Environment = "Shared"
    Purpose     = "TerraformState"
  }
}

resource "aws_s3_bucket_versioning" "terraform_state_bucket_versioning" {
  bucket = aws_s3_bucket.terraform_state_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state_bucket_encryption" {
  bucket = aws_s3_bucket.terraform_state_bucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state_bucket_public_access" {
  bucket = aws_s3_bucket.terraform_state_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# REMOVE THIS BLOCK if it exists in your backend.tf, as ACLs are not supported
# resource "aws_s3_bucket_acl" "terraform_state_bucket_acl" {
#   bucket = aws_s3_bucket.terraform_state_bucket.id
#   acl    = "private"
# }

output "s3_bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state_bucket.bucket
}