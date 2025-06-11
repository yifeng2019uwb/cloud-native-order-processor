# ===== AUTOMATED CLEANUP MECHANISMS =====
# auto-destroy.tf

# Local values for auto-destroy configuration
locals {
  # Auto-destroy settings by cost profile
  auto_destroy_config = {
    minimal = {
      enabled = true
      max_lifetime_hours = 24    # 24 hours for minimal testing
      warning_hours = 2          # Warn 2 hours before destruction
      daily_shutdown = true      # Shutdown daily at night
      weekend_shutdown = true    # Shutdown on weekends
    }
    learning = {
      enabled = false            # Manual control for learning
      max_lifetime_hours = 72    # 3 days max
      warning_hours = 12         # 12 hour warning
      daily_shutdown = false     # Keep running for learning
      weekend_shutdown = true    # Shutdown on weekends
    }
    production = {
      enabled = false            # No auto-destroy for production
      max_lifetime_hours = 0     # Unlimited
      warning_hours = 0          # No warnings
      daily_shutdown = false     # Always on
      weekend_shutdown = false   # Always on
    }
  }


  current_destroy_config = local.auto_destroy_config[var.cost_profile]

  # Tags for auto-destroy resources
  auto_destroy_tags = {
    AutoDestroy = "enabled"
    Purpose = "cost-control"
    CreatedAt = timestamp()
    MaxLifetime = "${local.current_destroy_config.max_lifetime_hours}h"
  }
}

# AUTO-DESTROY: Lambda function for automated cleanup
resource "aws_lambda_function" "auto_destroyer" {
  count = local.current_destroy_config.enabled ? 1 : 0

  filename         = "auto-destroyer.zip"
  function_name    = "${var.project_name}-${var.environment}-auto-destroyer"
  role            = aws_iam_role.auto_destroyer_role[0].arn
  handler         = "index.handler"
  runtime         = "python3.9"
  timeout         = 900  # 15 minutes timeout

  source_code_hash = data.archive_file.auto_destroyer_zip[0].output_base64sha256

  environment {
    variables = {
      PROJECT_NAME = var.project_name
      ENVIRONMENT = var.environment
      MAX_LIFETIME_HOURS = local.current_destroy_config.max_lifetime_hours
      WARNING_HOURS = local.current_destroy_config.warning_hours
      SNS_TOPIC_ARN = aws_sns_topic.cost_alerts.arn
      DRY_RUN = "false"  # Set to "true" for testing
    }
  }

  tags = merge(local.auto_destroy_tags, {
    Name = "${var.project_name}-${var.environment}-auto-destroyer"
  })
}

# Auto-destroyer Lambda package
data "archive_file" "auto_destroyer_zip" {
  count = local.current_destroy_config.enabled ? 1 : 0

  type        = "zip"
  output_path = "auto-destroyer.zip"