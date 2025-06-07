# S3 to save terraform state

resource "aws_s3_bucket" "terraform_state_bucket" {
  # Choose a globally unique name for your S3 bucket
  # Example: "your-company-name-terraform-state-bucket"
  bucket = "yifeng2019uwb-order-processor-terraform-state"

  # Enable bucket versioning to keep a history of your state files.
  # This is crucial for recovery if a state file gets corrupted or accidentally deleted.
  versioning {
    enabled = true
  }

  # Enable server-side encryption for security
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  # Block public access to the bucket
  acl = "private"

  tags = {
    Name        = "TerraformStateBucket"
    Environment = "Shared"
    Purpose     = "TerraformState"
  }
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state_bucket.bucket
}