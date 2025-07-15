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

  # Rule for frequent snapshots (every 5 minutes)
  rule {
    id     = "frequent-snapshots"
    status = "Enabled"

    # Keep recent snapshots for 7 days
    expiration {
      days = 7
    }

    # Apply to snapshot prefix
    filter {
      prefix = "snapshots/"
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

# CloudWatch Event Rule for daily snapshots (reduced frequency for cost optimization)
resource "aws_cloudwatch_event_rule" "snapshot_rule" {
  name                = "${local.resource_prefix}-snapshot-rule"
  description         = "Trigger DynamoDB snapshot once per day (reduced from every 5 minutes for cost savings)"
  # Cost optimization: Reduce S3 and Lambda requests by running daily instead of every 5 minutes
  schedule_expression = "rate(1 day)"

  tags = local.common_tags
}

# CloudWatch Event Target (Lambda function for snapshots)
resource "aws_cloudwatch_event_target" "snapshot_target" {
  rule      = aws_cloudwatch_event_rule.snapshot_rule.name
  target_id = "DynamoDBSnapshot"
  arn       = aws_lambda_function.snapshot_function.arn
}

# Lambda function for creating snapshots
resource "aws_lambda_function" "snapshot_function" {
  filename         = "placeholder.zip"
  function_name    = "${local.resource_prefix}-snapshot"
  role            = aws_iam_role.snapshot_role.arn
  handler         = "index.handler"
  runtime         = "python3.11"
  timeout         = 300
  memory_size     = 256

  environment {
    variables = {
      DYNAMODB_ORDERS_TABLE = aws_dynamodb_table.orders.name
      DYNAMODB_INVENTORY_TABLE = aws_dynamodb_table.inventory.name
      DYNAMODB_USERS_TABLE = aws_dynamodb_table.users.name
      S3_BUCKET = aws_s3_bucket.main.bucket
      S3_PREFIX = "snapshots/"
    }
  }

  tags = local.common_tags
}

# IAM role for snapshot Lambda
resource "aws_iam_role" "snapshot_role" {
  name = "${local.resource_prefix}-snapshot-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# IAM policy for snapshot Lambda
resource "aws_iam_role_policy" "snapshot_policy" {
  name = "${local.resource_prefix}-snapshot-policy"
  role = aws_iam_role.snapshot_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:Scan",
          "dynamodb:GetItem",
          "dynamodb:Query"
        ]
        Resource = [
          aws_dynamodb_table.orders.arn,
          aws_dynamodb_table.inventory.arn,
          aws_dynamodb_table.users.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.main.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Lambda permission for CloudWatch Events
resource "aws_lambda_permission" "allow_cloudwatch_snapshot" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.snapshot_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.snapshot_rule.arn
}