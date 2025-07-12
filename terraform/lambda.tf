# terraform/lambda.tf
# Simple Lambda function

# Build Lambda package locally with dependencies
resource "null_resource" "build_lambda_package" {
  count = local.enable_lambda ? 1 : 0

  triggers = {
    requirements = filemd5("${path.module}/../lambda_package/requirements.txt")
    handler      = filemd5("${path.module}/../lambda_package/lambda_handler.py")
  }

  provisioner "local-exec" {
    command = <<-EOT
      cd ${path.module}/../lambda_package

      # Use our build script
      chmod +x build.sh
      ./build.sh

      echo "Lambda package built successfully using build.sh"
    EOT
  }
}

# Use the built Lambda package directly
locals {
  lambda_package_path = "${path.module}/../lambda_package/lambda_package.zip"
}

# CloudWatch log group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  count = local.enable_lambda ? 1 : 0

  name              = "/aws/lambda/${local.resource_prefix}-order-api"
  retention_in_days = 7

  tags = local.common_tags
}

# Lambda function
resource "aws_lambda_function" "order_api" {
  count = local.enable_lambda ? 1 : 0

  function_name = "${local.resource_prefix}-order-api"
  role          = aws_iam_role.lambda_execution[0].arn
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256

  filename         = local.lambda_package_path
  source_code_hash = filebase64sha256(local.lambda_package_path)

  environment {
    variables = {
      ORDERS_TABLE    = aws_dynamodb_table.orders.name
      INVENTORY_TABLE = aws_dynamodb_table.inventory.name
      USERS_TABLE     = aws_dynamodb_table.users.name
      SNS_TOPIC_ARN   = aws_sns_topic.order_events.arn
      SQS_QUEUE_URL   = aws_sqs_queue.order_processing.url
      S3_BUCKET       = aws_s3_bucket.events.bucket
      # AWS_REGION      = var.region
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_execution_basic,
    aws_cloudwatch_log_group.lambda_logs
  ]

  tags = local.common_tags
}