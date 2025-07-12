# terraform/apigateway.tf
# Simple API Gateway setup

# API Gateway account settings for CloudWatch logging
resource "aws_api_gateway_account" "main" {
  count = local.enable_lambda ? 1 : 0

  cloudwatch_role_arn = aws_iam_role.api_gateway_logging[0].arn

  depends_on = [aws_iam_role_policy.api_gateway_logging]
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "order_api" {
  count = local.enable_lambda ? 1 : 0

  name        = "${local.resource_prefix}-api"
  description = "Order Processor API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = local.common_tags
}

# Proxy resource for all paths
resource "aws_api_gateway_resource" "proxy" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id = aws_api_gateway_rest_api.order_api[0].id
  parent_id   = aws_api_gateway_rest_api.order_api[0].root_resource_id
  path_part   = "{proxy+}"
}

# ANY method for proxy
resource "aws_api_gateway_method" "proxy" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id   = aws_api_gateway_rest_api.order_api[0].id
  resource_id   = aws_api_gateway_resource.proxy[0].id
  http_method   = "ANY"
  authorization = "NONE"

  # Enable method-level logging
  request_parameters = {
    "method.request.path.proxy" = true
  }
}

# Lambda integration
resource "aws_api_gateway_integration" "lambda_proxy" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id = aws_api_gateway_rest_api.order_api[0].id
  resource_id = aws_api_gateway_resource.proxy[0].id
  http_method = aws_api_gateway_method.proxy[0].http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.order_api[0].invoke_arn
}

# Root method (for health checks)
resource "aws_api_gateway_method" "proxy_root" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id   = aws_api_gateway_rest_api.order_api[0].id
  resource_id   = aws_api_gateway_rest_api.order_api[0].root_resource_id
  http_method   = "ANY"
  authorization = "NONE"

  # Enable method-level logging
  request_parameters = {}
}

# Root integration
resource "aws_api_gateway_integration" "lambda_root" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id = aws_api_gateway_rest_api.order_api[0].id
  resource_id = aws_api_gateway_rest_api.order_api[0].root_resource_id
  http_method = aws_api_gateway_method.proxy_root[0].http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.order_api[0].invoke_arn
}

# Deployment
resource "aws_api_gateway_deployment" "order_api" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id = aws_api_gateway_rest_api.order_api[0].id

  depends_on = [
    aws_api_gateway_method.proxy,
    aws_api_gateway_integration.lambda_proxy,
    aws_api_gateway_method.proxy_root,
    aws_api_gateway_integration.lambda_root
  ]

  lifecycle {
    create_before_destroy = true
  }
}

# CloudWatch log group for API Gateway (simplified)
resource "aws_cloudwatch_log_group" "api_gateway" {
  count = local.enable_lambda ? 1 : 0

  name              = "/aws/apigateway/${local.resource_prefix}-api"
  retention_in_days = 7

  tags = local.common_tags
}



# IAM role for API Gateway logging
resource "aws_iam_role" "api_gateway_logging" {
  count = local.enable_lambda ? 1 : 0

  name = "${local.resource_prefix}-api-gateway-logging"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# IAM policy for API Gateway logging
resource "aws_iam_role_policy" "api_gateway_logging" {
  count = local.enable_lambda ? 1 : 0

  name = "${local.resource_prefix}-api-gateway-logging"
  role = aws_iam_role.api_gateway_logging[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:PutLogEvents",
          "logs:GetLogEvents",
          "logs:FilterLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Stage with logging enabled
resource "aws_api_gateway_stage" "order_api" {
  count = local.enable_lambda ? 1 : 0

  deployment_id = aws_api_gateway_deployment.order_api[0].id
  rest_api_id   = aws_api_gateway_rest_api.order_api[0].id
  stage_name    = var.environment

  # Enable CloudWatch access logging
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway[0].arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      caller         = "$context.identity.caller"
      user           = "$context.identity.user"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      resourcePath   = "$context.resourcePath"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      integrationLatency = "$context.integrationLatency"
      responseLatency    = "$context.responseLatency"
    })
  }

  # Enable detailed CloudWatch logging
  xray_tracing_enabled = true

  depends_on = [aws_iam_role_policy.api_gateway_logging]
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  count = local.enable_lambda ? 1 : 0

  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.order_api[0].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.order_api[0].execution_arn}/*/*"
}