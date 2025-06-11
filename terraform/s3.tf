# ===== S3 BUCKETS WITH FORCE DELETE =====
# s3.tf

# ORIGINAL: Custom KMS key (costs ~$1/month)
resource "aws_kms_key" "s3" {
  description             = "S3 encryption key"
  deletion_window_in_days = 7
}

# COST OPTIMIZATION: Comment out KMS key above for free AES256 encryption
# resource "aws_kms_key" "s3" {
#   count                   = var.cost_profile == "minimal" ? 0 : 1  # COST EFFICIENT: No KMS for minimal profile
#   description             = "S3 encryption key"
#   deletion_window_in_days = 7
# }

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket" "events" {
  bucket        = "${var.project_name}-${var.environment}-events-${random_string.bucket_suffix.result}"
  force_destroy = true # FORCE DELETE - remove all objects when destroying

  tags = {
    Name    = "${var.project_name}-${var.environment}-events"
    Purpose = "EventSourcing"
  }
}

# Add after aws_s3_bucket.events
resource "aws_s3_bucket_public_access_block" "events" {
  bucket = aws_s3_bucket.events.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "backups" {
  bucket        = "${var.project_name}-${var.environment}-backups-${random_string.bucket_suffix.result}"
  force_destroy = true # FORCE DELETE - remove all objects when destroying

  tags = {
    Name    = "${var.project_name}-${var.environment}-backups"
    Purpose = "DatabaseBackups"
  }
}

# Add after aws_s3_bucket.backups
resource "aws_s3_bucket_public_access_block" "backups" {
  bucket = aws_s3_bucket.backups.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Basic encryption (not KMS to save costs)
# ORIGINAL: Uses custom KMS key (costs extra ~$1/month)
resource "aws_s3_bucket_server_side_encryption_configuration" "events" {
  bucket = aws_s3_bucket.events.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
  }
}

# COST OPTIMIZATION: Use free AES256 encryption instead of KMS
# Comment out the encryption configs above and uncomment below:
# resource "aws_s3_bucket_server_side_encryption_configuration" "events" {
#   bucket = aws_s3_bucket.events.id
#
#   rule {
#     apply_server_side_encryption_by_default {
#       sse_algorithm = "AES256"  # COST EFFICIENT: Free vs $1/month KMS
#     }
#   }
# }
#
# resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
#   bucket = aws_s3_bucket.backups.id
#
#   rule {
#     apply_server_side_encryption_by_default {
#       sse_algorithm = "AES256"  # COST EFFICIENT: Free vs $1/month KMS
#     }
#   }
# }

# Aggressive lifecycle for practice (delete old data quickly)
resource "aws_s3_bucket_lifecycle_configuration" "events" {
  bucket = aws_s3_bucket.events.id

  rule {
    id     = "practice_cleanup"
    status = "Enabled"

    filter {
      prefix = ""
    }

    # ORIGINAL: 30 days retention (could be more aggressive for practice)
    expiration {
      days = 30 # Delete after 30 days for practice
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
    }

    # Force delete incomplete multipart uploads
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}

# COST OPTIMIZATION: More aggressive cleanup for minimal cost
# Comment out the expiration above and uncomment below:
# expiration {
#   days = var.cost_profile == "minimal" ? 1 : 7  # COST EFFICIENT: 1 day for minimal testing
# }

# Add lifecycle for backups bucket too
resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "practice_cleanup"
    status = "Enabled"

    filter {
      prefix = ""
    }

    # ORIGINAL: 7 days for backups (could be shorter for practice)
    expiration {
      days = 7 # Delete backups after 7 days for practice
    }

    noncurrent_version_expiration {
      noncurrent_days = 1
    }

    # Force delete incomplete multipart uploads
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}

# COST OPTIMIZATION: More aggressive backup cleanup
# Comment out the expiration above and uncomment below:
# expiration {
#   days = var.cost_profile == "minimal" ? 1 : 3  # COST EFFICIENT: 1 day for minimal testing
# }

# Disable versioning to make deletion easier
resource "aws_s3_bucket_versioning" "events" {
  bucket = aws_s3_bucket.events.id
  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id
  versioning_configuration {
    status = "Disabled"
  }
}