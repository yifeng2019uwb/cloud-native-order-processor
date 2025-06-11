# ===== COST OPTIMIZATION, BUDGETS AND ALERTS =====
# cost-optimization.tf

# Local values for cost configuration
locals {
  # Cost thresholds by profile
  cost_thresholds = {
    minimal    = 120  # $120/month budget
    learning   = 180  # $180/month budget
    production = 300  # $300/month budget
  }

  # Email for cost alerts (customize this)
  cost_alert_email = var.notification_email != "" ? var.notification_email : "your-email@example.com"

  # Cost optimization tags
  cost_tags = {
    CostOptimization = "enabled"
    BudgetProfile    = var.cost_profile
    AutoCleanup      = "enabled"
    Purpose          = "practice-learning"
  }
}

# COST CONTROL: Budget for monthly spend monitoring
resource "aws_budgets_budget" "monthly_cost_budget" {
  name         = "${var.project_name}-${var.environment}-monthly-budget"
  budget_type  = "COST"
  limit_amount = local.cost_thresholds[var.cost_profile]
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  time_period_start = formatdate("YYYY-MM-01_00:00", timestamp())

  cost_filters {
    tag {
      key = "Project"
      values = [var.project_name]
    }
  }

  # Alert at 80% of budget
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 80
    threshold_type           = "PERCENTAGE"
    notification_type        = "ACTUAL"
    subscriber_email_addresses = [local.cost_alert_email]
  }

  # Alert at 100% of budget (forecast)
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 100
    threshold_type           = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [local.cost_alert_email]
  }

  # Critical alert at 120% of budget
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 120
    threshold_type           = "PERCENTAGE"
    notification_type        = "ACTUAL"
    subscriber_email_addresses = [local.cost_alert_email]
  }

  tags = merge(local.cost_tags, {
    Name = "${var.project_name}-${var.environment}-budget"
  })
}

# COST CONTROL: Daily spend alert for immediate feedback during learning
resource "aws_budgets_budget" "daily_cost_budget" {
  count = var.cost_profile == "minimal" ? 1 : 0  # Only for minimal profile

  name         = "${var.project_name}-${var.environment}-daily-budget"
  budget_type  = "COST"
  limit_amount = "10"  # $10 daily limit for minimal profile
  limit_unit   = "USD"
  time_unit    = "DAILY"

  cost_filters {
    tag {
      key = "Project"
      values = [var.project_name]
    }
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                 = 80
    threshold_type           = "PERCENTAGE"
    notification_type        = "ACTUAL"
    subscriber_email_addresses = [local.cost_alert_email]
  }

  tags = merge(local.cost_tags, {
    Name = "${var.project_name}-${var.environment}-daily-budget"
  })
}

# COST MONITORING: CloudWatch billing alarm
resource "aws_cloudwatch_metric_alarm" "billing_alarm" {
  alarm_name          = "${var.project_name}-${var.environment}-billing-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = "86400"  # 24 hours
  statistic           = "Maximum"
  threshold           = local.cost_thresholds[var.cost_profile]
  alarm_description   = "This metric monitors aws billing charges for ${var.project_name}"
  alarm_actions       = [aws_sns_topic.cost_alerts.arn]

  dimensions = {
    Currency = "USD"
  }

  tags = merge(local.cost_tags, {
    Name = "${var.project_name}-${var.environment}-billing-alarm"
  })
}

# COST ALERTS: SNS topic for cost notifications
resource "aws_sns_topic" "cost_alerts" {
  name = "${var.project_name}-${var.environment}-cost-alerts"

  tags = merge(local.cost_tags, {
    Name = "${var.project_name}-${var.environment}-cost-alerts"
  })
}

# COST ALERTS: Email subscription for cost notifications
resource "aws_sns_topic_subscription" "cost_alerts_email" {
  count = var.notification_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.cost_alerts.arn
  protocol  = "email"
  endpoint  = local.cost_alert_email
}

# COST OPTIMIZATION: Resource tagging policy for cost tracking
resource "aws_organizations_policy" "cost_tracking_policy" {
  count = var.cost_profile == "production" ? 1 : 0  # Only for production learning

  name        = "${var.project_name}-cost-tracking"
  description = "Require cost tracking tags on all resources"
  type        = "TAG_POLICY"

  content = jsonencode({
    tags = {
      Project = {
        tag_key = "Project"
        enforced_for = ["*"]
      }
      Environment = {
        tag_key = "Environment"
        enforced_for = ["*"]
      }
      CostProfile = {
        tag_key = "CostProfile"
        enforced_for = ["*"]
      }
    }
  })
}

# COST OPTIMIZATION: Lambda function for cost optimization recommendations
resource "aws_lambda_function" "cost_optimizer" {
  count = var.cost_profile == "learning" || var.cost_profile == "production" ? 1 : 0

  filename         = "cost-optimizer.zip"
  function_name    = "${var.project_name}-${var.environment}-cost-optimizer"
  role            = aws_iam_role.cost_optimizer_role[0].arn
  handler         = "index.handler"
  runtime         = "python3.9"
  timeout         = 300

  # Create a simple cost optimization function
  source_code_hash = data.archive_file.cost_optimizer_zip[0].output_base64sha256

  environment {
    variables = {
      PROJECT_NAME = var.project_name
      ENVIRONMENT = var.environment
      COST_PROFILE = var.cost_profile
      SNS_TOPIC_ARN = aws_sns_topic.cost_alerts.arn
    }
  }

  tags = merge(local.cost_tags, {
    Name = "${var.project_name}-${var.environment}-cost-optimizer"
  })
}

# Cost optimizer Lambda package
data "archive_file" "cost_optimizer_zip" {
  count = var.cost_profile == "learning" || var.cost_profile == "production" ? 1 : 0

  type        = "zip"
  output_path = "cost-optimizer.zip"

  source {
    content = templatefile("${path.module}/scripts/cost-optimizer.py", {
      project_name = var.project_name
      environment = var.environment
    })
    filename = "index.py"
  }
}

# IAM role for cost optimizer Lambda
resource "aws_iam_role" "cost_optimizer_role" {
  count = var.cost_profile == "learning" || var.cost_profile == "production" ? 1 : 0

  name = "${var.project_name}-${var.environment}-cost-optimizer-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = local.cost_tags
}

# IAM policy for cost optimizer
resource "aws_iam_role_policy" "cost_optimizer_policy" {
  count = var.cost_profile == "learning" || var.cost_profile == "production" ? 1 : 0

  name = "${var.project_name}-${var.environment}-cost-optimizer-policy"
  role = aws_iam_role.cost_optimizer_role[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "ce:GetCostAndUsage",
          "ce:GetUsageReport",
          "ec2:DescribeInstances",
          "rds:DescribeDBInstances",
          "eks:ListClusters",
          "sns:Publish"
        ]
        Resource = "*"
      }
    ]
  })
}

# COST OPTIMIZATION: EventBridge rule to run cost optimizer daily
resource "aws_cloudwatch_event_rule" "daily_cost_check" {
  count = var.cost_profile == "learning" || var.cost_profile == "production" ? 1 : 0

  name                = "${var.project_name}-${var.environment}-daily-cost-check"
  description         = "Run cost optimization check daily"
  schedule_expression = "cron(0 9 * * ? *)"  # 9 AM UTC daily

  tags = local.cost_tags
}

# EventBridge target for cost optimizer
resource "aws_cloudwatch_event_target" "cost_optimizer_target" {
  count = var.cost_profile == "learning" || var.cost_profile == "production" ? 1 : 0

  rule      = aws_cloudwatch_event_rule.daily_cost_check[0].name
  target_id = "CostOptimizerTarget"
  arn       = aws_lambda_function.cost_optimizer[0].arn
}

# Lambda permission for EventBridge
resource "aws_lambda_permission" "allow_eventbridge" {
  count = var.cost_profile == "learning" || var.cost_profile == "production" ? 1 : 0

  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cost_optimizer[0].function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_cost_check[0].arn
}

# Outputs for cost monitoring
output "cost_optimization_summary" {
  description = "Cost optimization resources created"
  value = {
    monthly_budget_limit = local.cost_thresholds[var.cost_profile]
    daily_budget_enabled = var.cost_profile == "minimal"
    cost_alerts_topic = aws_sns_topic.cost_alerts.arn
    billing_alarm = aws_cloudwatch_metric_alarm.billing_alarm.alarm_name
    cost_optimizer_enabled = var.cost_profile == "learning" || var.cost_profile == "production"
    notification_email = local.cost_alert_email
  }
}

output "cost_monitoring_commands" {
  description = "Commands to monitor costs"
  value = {
    check_current_costs = "aws ce get-cost-and-usage --time-period Start=$(date -d 'first day of this month' +%Y-%m-%d),End=$(date +%Y-%m-%d) --granularity MONTHLY --metrics BlendedCost"
    check_daily_costs = "aws ce get-cost-and-usage --time-period Start=$(date -d '7 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) --granularity DAILY --metrics BlendedCost"
    list_budgets = "aws budgets describe-budgets --account-id $(aws sts get-caller-identity --query Account --output text)"
  }
}