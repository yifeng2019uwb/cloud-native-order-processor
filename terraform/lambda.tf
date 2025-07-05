# terraform/lambda.tf
# Lambda function and all related resources

# Create a placeholder ZIP file for initial deployment
data "archive_file" "lambda_placeholder" {
  count = local.enable_lambda ? 1 : 0

  type        = "zip"
  output_path = "${path.module}/placeholder.zip"

  source {
    content = <<-EOT
import json
import os

def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'Order Processor API - Placeholder Function',
            'environment': os.getenv('ENVIRONMENT'),
            'instruction': 'Deploy your FastAPI app to replace this placeholder'
        })
    }
EOT
    filename = "lambda_handler.py"
  }
}

# Lambda execution role
resource "aws_iam_role" "lambda_execution" {
  count = local.enable_lambda ? 1 : 0

  name = "${var.resource_prefix}-lambda-execution-role"

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

  tags = {
    Name        = "${var.resource_prefix}-lambda-execution-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_execution_basic" {
  count = local.enable_lambda ? 1 : 0

  role       = aws_iam_role.lambda_execution[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Custom policy for Lambda to access shared resources
resource "aws_iam_policy" "lambda_execution_custom" {
  count = local.enable_lambda ? 1 : 0

  name        = "${var.resource_prefix}-lambda-execution-policy"
  description = "Custom policy for Lambda to access shared resources"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = [
          "${aws_s3_bucket.events.arn}/*",
          "${aws_s3_bucket.backups.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.order_events.arn
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage"
        ]
        Resource = aws_sqs_queue.order_processing.arn
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.db_credentials.arn
      }
    ]
  })

  tags = {
    Name        = "${var.resource_prefix}-lambda-execution-policy"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Attach custom policy to role
resource "aws_iam_role_policy_attachment" "lambda_execution_custom" {
  count = local.enable_lambda ? 1 : 0

  role       = aws_iam_role.lambda_execution[0].name
  policy_arn = aws_iam_policy.lambda_execution_custom[0].arn
}

# CloudWatch log group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  count = local.enable_lambda ? 1 : 0

  name              = "/aws/lambda/${var.resource_prefix}-order-api"
  retention_in_days = 7

  tags = {
    Name        = "${var.resource_prefix}-lambda-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Lambda function
resource "aws_lambda_function" "order_api" {
  count = local.enable_lambda ? 1 : 0

  function_name = "${local.resource_prefix}-order-api"
  role          = aws_iam_role.lambda_execution[0].arn
  handler       = "lambda_handler.handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256

  filename         = "placeholder.zip"
  source_code_hash = data.archive_file.lambda_placeholder[0].output_base64sha256

  environment {
    variables = {
      ENVIRONMENT = var.environment

      # Database connection
      DB_HOST     = aws_db_instance.postgres_main.address
      DB_PORT     = aws_db_instance.postgres_main.port
      DB_NAME     = aws_db_instance.postgres_main.db_name
      DB_USER     = aws_db_instance.postgres_main.username
      DB_PASSWORD = aws_db_instance.postgres_main.password

      # Messaging
      SNS_TOPIC_ARN = aws_sns_topic.order_events.arn
      SQS_QUEUE_URL = aws_sqs_queue.order_processing.url

      # Storage
      S3_BUCKET = aws_s3_bucket.events.bucket
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_execution_basic,
    aws_iam_role_policy_attachment.lambda_execution_custom,
    aws_cloudwatch_log_group.lambda_logs,
  ]

  tags = {
    Name        = "${var.resource_prefix}-order-api"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Lambda function alias for versioning
resource "aws_lambda_alias" "order_api_live" {
  count = local.enable_lambda ? 1 : 0

  name             = "live"
  description      = "Live version of the Order API"
  function_name    = aws_lambda_function.order_api[0].function_name
  function_version = "$LATEST"
}