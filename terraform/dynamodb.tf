# terraform/dynamodb.tf
# Simple DynamoDB for personal project

# Orders table
resource "aws_dynamodb_table" "orders" {
  name         = "${local.resource_prefix}-orders"
  billing_mode = "PAY_PER_REQUEST"  # No upfront costs
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  # For querying orders by customer
  attribute {
    name = "customer_id"
    type = "S"
  }

  global_secondary_index {
    name            = "CustomerIndex"
    hash_key        = "customer_id"
    range_key       = "SK"
    projection_type = "ALL"
  }

  tags = local.common_tags
}

# Inventory table (simple)
resource "aws_dynamodb_table" "inventory" {
  name         = "${local.resource_prefix}-inventory"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "product_id"

  attribute {
    name = "product_id"
    type = "S"
  }

  tags = local.common_tags
}

# User table (new - dedicated for user authentication)
resource "aws_dynamodb_table" "users" {
  name         = "${local.resource_prefix}-users"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  # For querying users by email
  attribute {
    name = "email"
    type = "S"
  }

  global_secondary_index {
    name            = "EmailIndex"
    hash_key        = "email"
    projection_type = "ALL"
  }

  tags = local.common_tags
}