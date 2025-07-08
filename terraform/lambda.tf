# terraform/lambda.tf
# Simple Lambda function

# Placeholder code for initial deployment
data "archive_file" "lambda_placeholder" {
  count = local.enable_lambda ? 1 : 0

  type        = "zip"
  output_path = "${path.module}/placeholder.zip"

  source {
    content = <<-EOT
import json

def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'Order Processor API - Ready for FastAPI',
            'environment': 'dev'
        })
    }
EOT
    filename = "lambda_handler.py"
  }
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
  handler       = "lambda_handler.handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256

  filename         = data.archive_file.lambda_placeholder[0].output_path
  source_code_hash = data.archive_file.lambda_placeholder[0].output_base64sha256

  environment {
    variables = {
      ORDERS_TABLE    = aws_dynamodb_table.orders.name
      INVENTORY_TABLE = aws_dynamodb_table.inventory.name
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