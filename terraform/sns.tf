# SNS Topic for notifications
resource "aws_sns_topic" "order_notifications" {
  name = "${var.project_name}-${var.environment}-order-notifications"

  tags = {
    Name        = "${var.project_name}-${var.environment}-order-notifications"
    Environment = var.environment
  }
}