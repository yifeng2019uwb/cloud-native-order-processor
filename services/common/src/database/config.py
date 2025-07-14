# Database configuration
import os

# DynamoDB Configuration
DYNAMODB_REGION = os.getenv("AWS_REGION")
if not DYNAMODB_REGION:
    raise ValueError("AWS_REGION environment variable is required")
USERS_TABLE = os.getenv("USERS_TABLE")
ORDERS_TABLE = os.getenv("ORDERS_TABLE")
INVENTORY_TABLE = os.getenv("INVENTORY_TABLE")
