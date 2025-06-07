# SQS Queues for async processing
resource "aws_sqs_queue" "order_processing" {
  name                      = "${var.project_name}-${var.environment}-order-processing"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600
  receive_wait_time_seconds = 10

  # Add the redrive policy
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.order_processing_dlq.arn
    maxReceiveCount     = 5 
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-order-processing"
    Environment = var.environment
  }
}

resource "aws_sqs_queue" "order_processing_dlq" {
  name                      = "${var.project_name}-${var.environment}-order-processing-dlq"
  message_retention_seconds = 1209600 
  tags = {
    Name        = "${var.project_name}-${var.environment}-order-processing-dlq"
    Environment = var.environment
  }
}

resource "aws_sqs_queue" "inventory_updates" {
  name                      = "${var.project_name}-${var.environment}-inventory-updates"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600
  receive_wait_time_seconds = 10

  # Add the redrive policy
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.inventory_updates_dlq.arn
    maxReceiveCount     = 5 
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-inventory-updates"
    Environment = var.environment
  }
}

resource "aws_sqs_queue" "inventory_updates_dlq" {
  name                      = "${var.project_name}-${var.environment}-inventory_updates-dlq"
  message_retention_seconds = 1209600 
  tags = {
    Name        = "${var.project_name}-${var.environment}-inventory_updates-dlq"
    Environment = var.environment
  }
}

resource "aws_sqs_queue" "notifications" {
  name                      = "${var.project_name}-${var.environment}-notifications"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600
  receive_wait_time_seconds = 10

  # Add the redrive policy
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.notifications_dlq.arn
    maxReceiveCount     = 5 
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-notifications"
    Environment = var.environment
  }
}

resource "aws_sqs_queue" "notifications_dlq" {
  name                      = "${var.project_name}-${var.environment}-notifications-dlq"
  message_retention_seconds = 1209600 
  tags = {
    Name        = "${var.project_name}-${var.environment}-notifications-dlq"
    Environment = var.environment
  }
}