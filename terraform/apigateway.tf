# terraform/apigateway.tf
# Simple API Gateway (TLS is enforced by default on API Gateway)

# API Gateway REST API (HTTPS enforced by default)
resource "aws_api_gateway_rest_api" "order_api" {
  count = local.enable_lambda ? 1 : 0

  name        = "${var.resource_prefix}-api"
  description = "Order Processor API for ${var.environment} environment"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name        = "${var.resource_prefix}-api"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Proxy resource
resource "aws_api_gateway_resource" "proxy" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id = aws_api_gateway_rest_api.order_api[0].id
  parent_id   = aws_api_gateway_rest_api.order_api[0].root_resource_id
  path_part   = "{proxy+}"
}

# Proxy method
resource "aws_api_gateway_method" "proxy" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id   = aws_api_gateway_rest_api.order_api[0].id
  resource_id   = aws_api_gateway_resource.proxy[0].id
  http_method   = "ANY"
  authorization = "NONE"
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

# Root method
resource "aws_api_gateway_method" "proxy_root" {
  count = local.enable_lambda ? 1 : 0

  rest_api_id   = aws_api_gateway_rest_api.order_api[0].id
  resource_id   = aws_api_gateway_rest_api.order_api[0].root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
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

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_rest_api.order_api[0].body,
      aws_api_gateway_method.proxy[0].id,
      aws_api_gateway_integration.lambda_proxy[0].id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_method.proxy,
    aws_api_gateway_integration.lambda_proxy,
    aws_api_gateway_method.proxy_root,
    aws_api_gateway_integration.lambda_root
  ]
}

# Stage
resource "aws_api_gateway_stage" "order_api" {
  count = local.enable_lambda ? 1 : 0

  deployment_id = aws_api_gateway_deployment.order_api[0].id
  rest_api_id   = aws_api_gateway_rest_api.order_api[0].id
  stage_name    = var.environment
}

# Lambda permission
resource "aws_lambda_permission" "api_gateway" {
  count = local.enable_lambda ? 1 : 0

  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.order_api[0].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.order_api[0].execution_arn}/*/*"
}