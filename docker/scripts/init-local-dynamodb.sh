#!/bin/bash
# Create DynamoDB tables in LocalStack for local deploy
# Run after LocalStack is up. Endpoint: http://localhost:4566 (from host) or http://localstack:4566 (from container)
# Uses boto3 (Python) — no AWS CLI required

ENDPOINT="${1:-http://localhost:4566}"
REGION="${2:-us-west-2}"

echo "Creating DynamoDB tables in LocalStack at $ENDPOINT (region: $REGION)..."

python3 - "$ENDPOINT" "$REGION" << 'EOF'
import sys
import boto3

endpoint = sys.argv[1]
region = sys.argv[2]

client = boto3.client(
    'dynamodb',
    endpoint_url=endpoint,
    region_name=region,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

# Users table
try:
    client.create_table(
        TableName='order-processor-local-users',
        AttributeDefinitions=[
            {'AttributeName': 'Pk', 'AttributeType': 'S'},
            {'AttributeName': 'Sk', 'AttributeType': 'S'},
            {'AttributeName': 'email', 'AttributeType': 'S'},
        ],
        KeySchema=[
            {'AttributeName': 'Pk', 'KeyType': 'HASH'},
            {'AttributeName': 'Sk', 'KeyType': 'RANGE'},
        ],
        BillingMode='PAY_PER_REQUEST',
        GlobalSecondaryIndexes=[{
            'IndexName': 'EmailIndex',
            'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}],
            'Projection': {'ProjectionType': 'ALL'}
        }]
    )
    print('  users: created')
except client.exceptions.ResourceInUseException:
    print('  users: already exists')

# Orders table
try:
    client.create_table(
        TableName='order-processor-local-orders',
        AttributeDefinitions=[
            {'AttributeName': 'Pk', 'AttributeType': 'S'},
            {'AttributeName': 'Sk', 'AttributeType': 'S'},
            {'AttributeName': 'GSI-PK', 'AttributeType': 'S'},
            {'AttributeName': 'GSI-SK', 'AttributeType': 'S'},
            {'AttributeName': 'GSI2-PK', 'AttributeType': 'S'},
            {'AttributeName': 'GSI2-SK', 'AttributeType': 'N'},
        ],
        KeySchema=[
            {'AttributeName': 'Pk', 'KeyType': 'HASH'},
            {'AttributeName': 'Sk', 'KeyType': 'RANGE'},
        ],
        BillingMode='PAY_PER_REQUEST',
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'UserOrdersIndex',
                'KeySchema': [
                    {'AttributeName': 'GSI-PK', 'KeyType': 'HASH'},
                    {'AttributeName': 'GSI-SK', 'KeyType': 'RANGE'},
                ],
                'Projection': {'ProjectionType': 'ALL'}
            },
            {
                'IndexName': 'PendingLimitOrders',
                'KeySchema': [
                    {'AttributeName': 'GSI2-PK', 'KeyType': 'HASH'},
                    {'AttributeName': 'GSI2-SK', 'KeyType': 'RANGE'},
                ],
                'Projection': {'ProjectionType': 'ALL'}
            }
        ]
    )
    print('  orders: created')
except client.exceptions.ResourceInUseException:
    print('  orders: already exists')

# Inventory table
try:
    client.create_table(
        TableName='order-processor-local-inventory',
        AttributeDefinitions=[
            {'AttributeName': 'product_id', 'AttributeType': 'S'},
            {'AttributeName': 'category', 'AttributeType': 'S'},
        ],
        KeySchema=[
            {'AttributeName': 'product_id', 'KeyType': 'HASH'},
        ],
        BillingMode='PAY_PER_REQUEST',
        GlobalSecondaryIndexes=[{
            'IndexName': 'CategoryIndex',
            'KeySchema': [{'AttributeName': 'category', 'KeyType': 'HASH'}],
            'Projection': {'ProjectionType': 'ALL'}
        }]
    )
    print('  inventory: created')
except client.exceptions.ResourceInUseException:
    print('  inventory: already exists')

print('DynamoDB tables ready.')
EOF
