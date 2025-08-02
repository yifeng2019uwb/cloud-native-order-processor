# terraform/dynamodb.tf
# DynamoDB tables for order processor

# ====================
# DYNAMODB TABLES
# ====================

# Users table
resource "aws_dynamodb_table" "users" {
  name           = local.db_names.users_table
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "Pk"
  range_key      = "Sk"

  attribute {
    name = "Pk"
    type = "S"
  }

  attribute {
    name = "Sk"
    type = "S"
  }

  attribute {
    name = "email"
    type = "S"
  }



  global_secondary_index {
    name            = "EmailIndex"
    hash_key        = "email"
    projection_type = "ALL"
  }

  tags = local.database_tags
}

# Orders table
resource "aws_dynamodb_table" "orders" {
  name           = local.db_names.orders_table
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "order_id"
  range_key      = "user_id"

  attribute {
    name = "order_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  global_secondary_index {
    name            = "UserOrdersIndex"
    hash_key        = "user_id"
    range_key       = "order_id"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "StatusIndex"
    hash_key        = "status"
    range_key       = "order_id"
    projection_type = "ALL"
  }

  tags = local.database_tags
}

# Inventory table
resource "aws_dynamodb_table" "inventory" {
  name           = local.db_names.inventory_table
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "product_id"

  attribute {
    name = "product_id"
    type = "S"
  }

  attribute {
    name = "category"
    type = "S"
  }

  global_secondary_index {
    name            = "CategoryIndex"
    hash_key        = "category"
    projection_type = "ALL"
  }

  tags = local.database_tags
}

# ====================
# DYNAMODB IAM POLICY
# ====================

# DynamoDB Access Policy (moved from iam.tf for better organization)
resource "aws_iam_policy" "dynamodb_access" {
  name = local.iam_names.service_db_role
  description = "Access to DynamoDB tables for order processor"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem",
          "dynamodb:DescribeTable"
        ]
        Resource = [
          aws_dynamodb_table.users.arn,
          "${aws_dynamodb_table.users.arn}/index/EmailIndex",
          aws_dynamodb_table.orders.arn,
          "${aws_dynamodb_table.orders.arn}/index/UserOrdersIndex",
          "${aws_dynamodb_table.orders.arn}/index/StatusIndex",
          aws_dynamodb_table.inventory.arn,
          "${aws_dynamodb_table.inventory.arn}/index/CategoryIndex"
        ]
      }
    ]
  })
}

# Attach DynamoDB policy to application role
resource "aws_iam_role_policy_attachment" "application_dynamodb" {
  role       = aws_iam_role.k8s_sa.name
  policy_arn = aws_iam_policy.dynamodb_access.arn
}