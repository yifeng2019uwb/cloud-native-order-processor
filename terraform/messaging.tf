# ===== SIMPLIFIED MESSAGING (SNS + SQS) =====
# messaging.tf

resource "aws_kms_key" "sqs" {
  description             = "SQS encryption key"
  deletion_window_in_days = 7
}

resource "aws_kms_key" "sns" {
  description             = "SNS encryption key"
  deletion_window_in_days = 7
}

resource "aws_sns_topic" "order_events" {
  name = "${var.project_name}-${var.environment}-order-events"

  kms_master_key_id = aws_kms_key.sns.arn

  tags = {
    Name = "${var.project_name}-${var.environment}-order-events"
  }
}

resource "aws_sqs_queue" "order_processing" {
  name                      = "${var.project_name}-${var.environment}-order-processing"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600
  receive_wait_time_seconds = 10
  kms_master_key_id = aws_kms_key.sqs.arn

  # Minimal DLQ for practice
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.order_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-order-processing"
  }
}

resource "aws_sqs_queue" "order_dlq" {
  kms_master_key_id = aws_kms_key.sqs.arn
  tags = {
    Name = "${var.project_name}-${var.environment}-order-dlq"
  }
}

# SNS to SQS subscription
resource "aws_sns_topic_subscription" "order_events_to_sqs" {
  topic_arn = aws_sns_topic.order_events.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.order_processing.arn
}

resource "aws_sqs_queue_policy" "order_processing" {
  queue_url = aws_sqs_queue.order_processing.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "sqs:SendMessage"
        Resource  = aws_sqs_queue.order_processing.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sns_topic.order_events.arn
          }
        }
      }
    ]
  })
}