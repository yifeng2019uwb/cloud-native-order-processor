# Lambda Function: Order Processor
resource "aws_lambda_function" "order_processor" {
  filename      = "../services/order_processor.zip"
  function_name = "${var.project_name}-${var.environment}-order-processor"
  role          = aws_iam_role.lambda_role.arn
  handler       = "dummy_order_processor"
  runtime       = "python3.11"
  timeout       = 30

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      ORDER_DB_HOST       = aws_db_instance.postgres_order.address
      ORDER_DB_PORT       = aws_db_instance.postgres_order.port
      ORDER_DB_NAME       = aws_db_instance.postgres_order.db_name
      ORDER_DB_USER       = var.db_username
      ORDER_DB_PASSWORD   = var.db_password
      INVENTORY_QUEUE_URL = aws_sqs_queue.inventory_updates.url
      SNS_TOPIC_ARN       = aws_sns_topic.order_notifications.arn
    }
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-order-processor"
    Environment = var.environment
  }

  depends_on = [aws_iam_role_policy_attachment.lambda_vpc_execution]
}

# Lambda Function: Inventory Manager
resource "aws_lambda_function" "inventory_manager" {
  filename      = "../services/inventory_manager.zip"
  function_name = "${var.project_name}-${var.environment}-inventory-manager"
  role          = aws_iam_role.lambda_role.arn
  handler       = "dummy_inventory_manager"
  runtime       = "python3.11"
  timeout       = 30

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      INVENTORY_DB_HOST     = aws_db_instance.postgres_inventory.address
      INVENTORY_DB_PORT     = aws_db_instance.postgres_inventory.port
      INVENTORY_DB_NAME     = aws_db_instance.postgres_inventory.db_name
      INVENTORY_DB_USER     = var.db_username
      INVENTORY_DB_PASSWORD = var.db_password
      PRODUCT_DB_HOST       = aws_db_instance.postgres_product.address
      PRODUCT_DB_PORT       = aws_db_instance.postgres_product.port
      PRODUCT_DB_NAME       = aws_db_instance.postgres_product.db_name
      PRODUCT_DB_USER       = var.db_username
      PRODUCT_DB_PASSWORD   = var.db_password
    }
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-inventory-manager"
    Environment = var.environment
  }

  depends_on = [aws_iam_role_policy_attachment.lambda_vpc_execution]
}

# Lambda Function: Notification Handler
resource "aws_lambda_function" "notification_handler" {
  filename      = "../services/notification_handler.zip"
  function_name = "${var.project_name}-${var.environment}-notification-handler"
  role          = aws_iam_role.lambda_role.arn
  handler       = "notification_handler.py"
  runtime       = "python3.11"
  timeout       = 30

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.order_notifications.arn
    }
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-notification-handler"
    Environment = var.environment
  }

  depends_on = [aws_iam_role_policy_attachment.lambda_vpc_execution]
}

# SQS Event Source Mapping for Order Processing
resource "aws_lambda_event_source_mapping" "order_processing_trigger" {
  event_source_arn = aws_sqs_queue.order_processing.arn
  function_name    = aws_lambda_function.order_processor.arn
  batch_size       = 5
}

# SQS Event Source Mapping for Inventory Updates
resource "aws_lambda_event_source_mapping" "inventory_trigger" {
  event_source_arn = aws_sqs_queue.inventory_updates.arn
  function_name    = aws_lambda_function.inventory_manager.arn
  batch_size       = 10
}

# SQS Event Source Mapping for Notifications
resource "aws_lambda_event_source_mapping" "notification_trigger" {
  event_source_arn = aws_sqs_queue.notifications.arn
  function_name    = aws_lambda_function.notification_handler.arn
  batch_size       = 10
}

# CloudWatch Log Groups for Lambda Functions
resource "aws_cloudwatch_log_group" "order_processor_logs" {
  name              = "/aws/lambda/${aws_lambda_function.order_processor.function_name}"
  retention_in_days = 14

  tags = {
    Name        = "${var.project_name}-${var.environment}-order-processor-logs"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "inventory_manager_logs" {
  name              = "/aws/lambda/${aws_lambda_function.inventory_manager.function_name}"
  retention_in_days = 14

  tags = {
    Name        = "${var.project_name}-${var.environment}-inventory-manager-logs"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "notification_handler_logs" {
  name              = "/aws/lambda/${aws_lambda_function.notification_handler.function_name}"
  retention_in_days = 14

  tags = {
    Name        = "${var.project_name}-${var.environment}-notification-handler-logs"
    Environment = var.environment
  }
}