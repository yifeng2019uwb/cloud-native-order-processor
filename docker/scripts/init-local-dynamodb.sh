#!/bin/bash
# Create DynamoDB tables in LocalStack for local deploy
# Run after LocalStack is up. Endpoint: http://localhost:4566 (from host) or http://localstack:4566 (from container)
# Requires: AWS CLI (install: pip install awscli, or use system package)

set -e

if ! command -v aws &>/dev/null; then
    echo "WARNING: AWS CLI not found. Install with: pip install awscli (or brew install awscli)"
    echo "Tables will need to be created manually or via another tool."
    exit 1
fi

ENDPOINT="${1:-http://localhost:4566}"
REGION="${2:-us-west-2}"

# Disable AWS CLI pager (prevents "less" from opening and blocking)
export AWS_PAGER=""

echo "Creating DynamoDB tables in LocalStack at $ENDPOINT (region: $REGION)..."

# Users table (suppress JSON output)
aws dynamodb create-table \
  --endpoint-url "$ENDPOINT" \
  --region "$REGION" \
  --table-name order-processor-local-users \
  --attribute-definitions \
    AttributeName=Pk,AttributeType=S \
    AttributeName=Sk,AttributeType=S \
    AttributeName=email,AttributeType=S \
  --key-schema \
    AttributeName=Pk,KeyType=HASH \
    AttributeName=Sk,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes '[
    {
      "IndexName": "EmailIndex",
      "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
      "Projection": {"ProjectionType": "ALL"}
    }
  ]' >/dev/null 2>&1 || echo "  users: already exists"

# Orders table
aws dynamodb create-table \
  --endpoint-url "$ENDPOINT" \
  --region "$REGION" \
  --table-name order-processor-local-orders \
  --attribute-definitions \
    AttributeName=Pk,AttributeType=S \
    AttributeName=Sk,AttributeType=S \
    AttributeName=GSI-PK,AttributeType=S \
    AttributeName=GSI-SK,AttributeType=S \
    AttributeName=GSI2-PK,AttributeType=S \
    AttributeName=GSI2-SK,AttributeType=N \
  --key-schema \
    AttributeName=Pk,KeyType=HASH \
    AttributeName=Sk,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes '[
    {
      "IndexName": "UserOrdersIndex",
      "KeySchema": [
        {"AttributeName": "GSI-PK", "KeyType": "HASH"},
        {"AttributeName": "GSI-SK", "KeyType": "RANGE"}
      ],
      "Projection": {"ProjectionType": "ALL"}
    },
    {
      "IndexName": "PendingLimitOrders",
      "KeySchema": [
        {"AttributeName": "GSI2-PK", "KeyType": "HASH"},
        {"AttributeName": "GSI2-SK", "KeyType": "RANGE"}
      ],
      "Projection": {"ProjectionType": "ALL"}
    }
  ]' >/dev/null 2>&1 || echo "  orders: already exists"

# Inventory table
aws dynamodb create-table \
  --endpoint-url "$ENDPOINT" \
  --region "$REGION" \
  --table-name order-processor-local-inventory \
  --attribute-definitions \
    AttributeName=product_id,AttributeType=S \
    AttributeName=category,AttributeType=S \
  --key-schema \
    AttributeName=product_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes '[
    {
      "IndexName": "CategoryIndex",
      "KeySchema": [{"AttributeName": "category", "KeyType": "HASH"}],
      "Projection": {"ProjectionType": "ALL"}
    }
  ]' >/dev/null 2>&1 || echo "  inventory: already exists"

echo "DynamoDB tables ready."
