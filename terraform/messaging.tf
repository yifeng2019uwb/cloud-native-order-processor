# ===== SIMPLIFIED MESSAGING (SNS + SQS) =====
# messaging.tf

# ORIGINAL: Separate KMS keys for SQS and SNS (costs ~$2/month total)
resource "aws_kms_key" "sqs" {
  description             = "SQS encryption key"
  deletion_window_in_days = 7
}

resource "aws_kms_key" "sns" {
  description             = "SNS encryption key"
  deletion_window_in_days = 7
}

# COST OPTIMIZATION: Use single shared key or no encryption for practice
# Comment out both KMS keys above and uncomment below:
# resource "aws_kms_key" "messaging" {
#   count                   = var.cost_profile == "minimal" ? 0 : 1  # COST EFFICIENT: No KMS for minimal
#   description             = "Shared messaging encryption key"
#   deletion_window_in_days = 7
# }

resource "aws_sns_topic" "order_events" {
  name = "${var.project_name}-${var.environment}-order-events"

  # ORIGINAL: Always use KMS encryption (costs extra)
  kms_master_key_id = aws_kms_key.sns.arn

  tags = {
    Name = "${var.project_name}-${var.environment}-order-events"
  }
}

# COST OPTIMIZATION: Conditional encryption for practice
# Comment out kms_master_key_id above and uncomment below:
# kms_master_key_id = var.cost_profile == "minimal" ? null : aws_kms_key.messaging[0].arn  # COST EFFICIENT: No encryption for minimal

resource "aws_sqs_queue" "order_processing" {
  name                      = "${var.project_name}-${var.environment}-order-processing"
  delay_seconds             = 0
  max_message_size          = 262144
  # ORIGINAL: 4 days retention (could be shorter for practice)
  message_retention_seconds = 345600
  receive_wait_time_seconds = 10
  # ORIGINAL: Always use KMS encryption (costs extra)
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

# COST OPTIMIZATION: Shorter retention and conditional encryption
# Comment out message_retention_seconds and kms_master_key_id above and uncomment below:
# message_retention_seconds = var.cost_profile == "minimal" ? 86400 : 345600  # COST EFFICIENT: 1 day vs 4 days
# kms_master_key_id = var.cost_profile == "minimal" ? null : aws_kms_key.messaging[0].arn  # COST EFFICIENT: No encryption for minimal

resource "aws_sqs_queue" "order_dlq" {
  # ORIGINAL: Always use KMS encryption (costs extra)
  kms_master_key_id = aws_kms_key.sqs.arn
  tags = {
    Name = "${var.project_name}-${var.environment}-order-dlq"
  }
}

# COST OPTIMIZATION: Conditional DLQ encryption and shorter retention
# Comment out kms_master_key_id above and add settings below:
# resource "aws_sqs_queue" "order_dlq" {
#   name                      = "${var.project_name}-${var.environment}-order-dlq"
#   message_retention_seconds = var.cost_profile == "minimal" ? 86400 : 1209600  # COST EFFICIENT: 1 day vs 14 days
#   kms_master_key_id = var.cost_profile == "minimal" ? null : aws_kms_key.messaging[0].arn  # COST EFFICIENT: No encryption for minimal
#   tags = {
#     Name = "${var.project_name}-${var.environment}-order-dlq"
#   }
# }

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