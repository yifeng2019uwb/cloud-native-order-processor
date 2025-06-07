# terraform/s3.tf (or main.tf)

resource "aws_s3_bucket" "recovery_data_bucket" {
  bucket = "cloud-native-order-processor-recovery-data-${var.environment}"
  acl    = "private" # Moved acl here, or use aws_s3_bucket_acl

  tags = {
    Name        = "OrderProcessorRecoveryData"
    Environment = var.environment
    Project     = "CloudNativeOrderProcessor"
    Purpose     = "DataRecovery"
  }
  # REMOVE this block if it exists here:
  # server_side_encryption_configuration {
  #   rule {
  #     apply_server_side_encryption_by_default {
  #       sse_algorithm = "AES256"
  #     }
  #   }
  # }
}

resource "aws_s3_bucket_versioning" "recovery_data_bucket_versioning" {
  bucket = aws_s3_bucket.recovery_data_bucket.id
  versioning_configuration {
    status = "Enabled" # Crucial for data recovery: keeps previous versions of objects
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "recovery_data_bucket_encryption" {
  bucket = aws_s3_bucket.recovery_data_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256" # Encrypts data at rest using S3-managed keys
    }
  }
}

# Highly recommended: Block public access explicitly with dedicated resources
resource "aws_s3_bucket_public_access_block" "recovery_data_bucket_public_access" {
  bucket = aws_s3_bucket.recovery_data_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Optional: Add lifecycle rules for cost management (e.g., move older versions to Glacier)
/*
resource "aws_s3_bucket_lifecycle_configuration" "recovery_data_bucket_lifecycle" {
  bucket = aws_s3_bucket.recovery_data_bucket.id

  rule {
    id     = "move-old-versions-to-glacier"
    status = "Enabled"

    noncurrent_version_transition {
      days          = 30
      storage_class = "GLACIER"
    }

    noncurrent_version_expiration {
      days = 365 # Delete old non-current versions after a year
    }
  }

  rule {
    id     = "delete-old-objects"
    status = "Enabled"

    expiration {
      days = 730 # Delete current objects after two years (adjust as needed)
    }
  }
}
*/