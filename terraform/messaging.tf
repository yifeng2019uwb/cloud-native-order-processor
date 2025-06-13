# messaging.tf - Basic SNS + SQS

# SNS Topic
resource "aws_sns_topic" "order_events" {
  name = "${local.resource_prefix}-order-events"

  tags = local.common_tags
}

# SQS Queue
resource "aws_sqs_queue" "order_processing" {
  name                      = "${local.resource_prefix}-order-processing"
  message_retention_seconds = 345600  # 4 days
  receive_wait_time_seconds = 10

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.order_dlq.arn
    maxReceiveCount     = 3
  })

  tags = local.common_tags
}

# Dead Letter Queue
resource "aws_sqs_queue" "order_dlq" {
  name = "${local.resource_prefix}-order-dlq"

  tags = local.common_tags
}

# SNS to SQS subscription
resource "aws_sns_topic_subscription" "order_events_to_sqs" {
  topic_arn = aws_sns_topic.order_events.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.order_processing.arn
}

# SQS policy
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