# terraform/messaging.tf
# Simple SNS + SQS setup

# SNS topic for order events
resource "aws_sns_topic" "order_events" {
  name = local.topic_names.order_events
  tags = local.common_tags
}

# SQS queue for order processing
resource "aws_sqs_queue" "order_processing" {
  name                      = local.queue_names.order_processing
  message_retention_seconds = 345600  # 4 days

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.order_dlq.arn
    maxReceiveCount     = 3
  })

  tags = local.common_tags
}

# Dead letter queue
resource "aws_sqs_queue" "order_dlq" {
  name = local.queue_names.order_dlq
  tags = local.common_tags
}

# SNS to SQS subscription
resource "aws_sns_topic_subscription" "order_events_to_sqs" {
  topic_arn = aws_sns_topic.order_events.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.order_processing.arn
}

# SQS policy to allow SNS to send messages
resource "aws_sqs_queue_policy" "order_processing" {
  queue_url = aws_sqs_queue.order_processing.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "sns.amazonaws.com"
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.order_processing.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_sns_topic.order_events.arn
          }
        }
      }
    ]
  })
}