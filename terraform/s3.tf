# s3.tf - Basic S3 buckets

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Events bucket
resource "aws_s3_bucket" "events" {
  bucket        = "${local.resource_prefix}-events-${random_string.bucket_suffix.result}"
  force_destroy = true

  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-events"
  })
}

# Backups bucket
resource "aws_s3_bucket" "backups" {
  bucket        = "${local.resource_prefix}-backups-${random_string.bucket_suffix.result}"
  force_destroy = true

  tags = merge(local.common_tags, {
    Name = "${local.resource_prefix}-backups"
  })
}

# Block public access
resource "aws_s3_bucket_public_access_block" "events" {
  bucket = aws_s3_bucket.events.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket = aws_s3_bucket.backups.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Basic encryption
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

# Versioning disabled
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