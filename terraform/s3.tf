# terraform/s3.tf
# Simple S3 bucket for personal project

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Main bucket for everything (events, backups, archive)
resource "aws_s3_bucket" "main" {
  bucket        = "${local.resource_prefix}-storage-${random_string.bucket_suffix.result}"
  force_destroy = true

  tags = local.common_tags
}

# Dedicated bucket for application logs
resource "aws_s3_bucket" "logs" {
  bucket        = "${local.resource_prefix}-logs-${random_string.bucket_suffix.result}"
  force_destroy = true

  tags = merge(local.common_tags, {
    Purpose = "Application Logs"
  })
}

# Block public access
resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Block public access for logs bucket
resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Basic encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Encryption for logs bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# DynamoDB backup configuration
resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Lifecycle policy for DynamoDB backups
resource "aws_s3_bucket_lifecycle_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    id     = "dynamodb-backups"
    status = "Enabled"

    # Move to cheaper storage after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # Move to glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Delete after 1 year
    expiration {
      days = 365
    }

    # Apply to all objects (required filter)
    filter {
      prefix = ""
    }
  }


}

# Lifecycle policy for application logs
resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "application-logs"
    status = "Enabled"

    # Move to cheaper storage after 30 days (minimum for STANDARD_IA)
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # Move to glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Delete after 180 days
    expiration {
      days = 180
    }

    # Apply to all objects (required filter)
    filter {
      prefix = ""
    }
  }
}



# ====================
# S3 IAM POLICY
# ====================

# S3 Access Policy (moved from iam.tf for better organization)
resource "aws_iam_policy" "s3_access" {
  name = local.iam_names.service_s3_role
  description = "Access to S3 buckets for order processor"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          aws_s3_bucket.main.arn,
          "${aws_s3_bucket.main.arn}/*",
          aws_s3_bucket.logs.arn,
          "${aws_s3_bucket.logs.arn}/*"
        ]
      }
    ]
  })
}

# Attach S3 policy to application role
resource "aws_iam_role_policy_attachment" "application_s3" {
  role       = aws_iam_role.k8s_sa.name
  policy_arn = aws_iam_policy.s3_access.arn
}