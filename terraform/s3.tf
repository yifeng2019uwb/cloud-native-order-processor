# ===== BASIC S3 BUCKETS (No intelligent tiering for practice) =====
# s3.tf
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket" "events" {
  bucket = "${var.project_name}-${var.environment}-events-${random_string.bucket_suffix.result}"

  tags = {
    Name    = "${var.project_name}-${var.environment}-events"
    Purpose = "EventSourcing"
  }
}

resource "aws_s3_bucket" "backups" {
  bucket = "${var.project_name}-${var.environment}-backups-${random_string.bucket_suffix.result}"

  tags = {
    Name    = "${var.project_name}-${var.environment}-backups"
    Purpose = "DatabaseBackups"
  }
}

# Basic encryption (not KMS to save costs)
resource "aws_s3_bucket_server_side_encryption_configuration" "events" {
  bucket = aws_s3_bucket.events.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Aggressive lifecycle for practice (delete old data quickly)
resource "aws_s3_bucket_lifecycle_configuration" "events" {
  bucket = aws_s3_bucket.events.id

  rule {
    id     = "practice_cleanup"
    status = "Enabled"

    filter {
      prefix = ""
    }

    expiration {
      days = 30  # Delete after 30 days for practice
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}