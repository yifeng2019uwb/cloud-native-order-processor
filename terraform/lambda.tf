# terraform/lambda.tf
# Lambda + API Gateway resources for dev env

# Lambda function for FastAPI
resource "aws_lambda_function" "order_api" {
  count = local.enable_lambda ? 1 : 0

  function_name = "${var.resource_prefix}-order-api"
  role          = aws_iam_role.lambda_execution[0].arn
  handler       = "lambda_handler.handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256

  # Placeholder for deployment package
  filename         = "placeholder.zip"
  source_code_hash = data.archive_file.lambda_placeholder[0].output_base64sha256

  environment {
    variables = {
      ENVIRONMENT = var.environment
      AWS_REGION  = var.region

      # Database connection - now references shared RDS (no array indexing)
      DB_HOST     = aws_db_instance.postgres_main.address
      DB_PORT     = aws_db_instance.postgres_main.port
      DB_NAME     = aws_db_instance.postgres_main.db_name
      DB_USER     = aws_db_instance.postgres_main.username
      DB_PASSWORD = aws_db_instance.postgres_main.password

      # Messaging - shared resources (no array indexing)
      SNS_TOPIC_ARN = aws_sns_topic.order_events.arn
      SQS_QUEUE_URL = aws_sqs_queue.order_processing.url

      # Storage - shared resources (no array indexing)
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

# Create a placeholder ZIP file for initial deployment
data "archive_file" "lambda_placeholder" {
  count = local.enable_lambda ? 1 : 0

  type        = "zip"
  output_path = "${path.module}/placeholder.zip"

  source {
    content = <<-EOT
def handler(event, context):
    return {
        'statusCode': 200,
        'body': '{"message": "Placeholder Lambda function - deploy your FastAPI app!"}'
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

# API Gateway REST API
resource "aws_api_gateway_rest_api" "order_api" {
  count = local.enable_lambda ? 1 : 0

  name        = "${var.resource_prefix}-api"
  description = "Order Processor API for ${var.environment} environment"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name        = "${var.resource_prefix}-api"
    Environment = var.environment
    Project     = var.project_name
  }
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "order_api" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id = aws_api_gateway_rest_api.order_api[0].id

  # Trigger redeployment when configuration changes
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_rest_api.order_api[0].body,
      aws_api_gateway_method.proxy[0].id,
      aws_api_gateway_integration.lambda_proxy[0].id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_method.proxy,
    aws_api_gateway_integration.lambda_proxy
  ]
}

# API Gateway stage
resource "aws_api_gateway_stage" "order_api" {
  count = local.enable_lambda ? 1 : 0

  deployment_id = aws_api_gateway_deployment.order_api[0].id
  rest_api_id   = aws_api_gateway_rest_api.order_api[0].id
  stage_name    = var.environment
}

# API Gateway proxy resource (catch-all)
resource "aws_api_gateway_resource" "proxy" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id = aws_api_gateway_rest_api.order_api[0].id
  parent_id   = aws_api_gateway_rest_api.order_api[0].root_resource_id
  path_part   = "{proxy+}"
}

# API Gateway method (proxy)
resource "aws_api_gateway_method" "proxy" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id   = aws_api_gateway_rest_api.order_api[0].id
  resource_id   = aws_api_gateway_resource.proxy[0].id
  http_method   = "ANY"
  authorization = "NONE"
}

# API Gateway integration with Lambda
resource "aws_api_gateway_integration" "lambda_proxy" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id = aws_api_gateway_rest_api.order_api[0].id
  resource_id = aws_api_gateway_resource.proxy[0].id
  http_method = aws_api_gateway_method.proxy[0].http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.order_api[0].invoke_arn
}

# API Gateway method for root resource
resource "aws_api_gateway_method" "proxy_root" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id   = aws_api_gateway_rest_api.order_api[0].id
  resource_id   = aws_api_gateway_rest_api.order_api[0].root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

# API Gateway integration for root resource
resource "aws_api_gateway_integration" "lambda_root" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id = aws_api_gateway_rest_api.order_api[0].id
  resource_id = aws_api_gateway_rest_api.order_api[0].root_resource_id
  http_method = aws_api_gateway_method.proxy_root[0].http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.order_api[0].invoke_arn
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  count = local.enable_lambda ? 1 : 0

  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.order_api[0].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.order_api[0].execution_arn}/*/*"
}

# Lambda function alias for versioning
resource "aws_lambda_alias" "order_api_live" {
  count = local.enable_lambda ? 1 : 0

  name             = "live"
  description      = "Live version of the Order API"
  function_name    = aws_lambda_function.order_api[0].function_name
  function_version = "$LATEST"
}

# CloudWatch log group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  count = local.enable_lambda ? 1 : 0

  name              = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.order_api[0].id}/${var.environment}"
  retention_in_days = 7

  tags = {
    Name        = "${var.resource_prefix}-api-gateway-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}