# Database configuration
import os

# DynamoDB Configuration
DYNAMODB_REGION = os.getenv("REGION", "us-west-2")
USERS_TABLE = os.getenv("USERS_TABLE")
ORDERS_TABLE = os.getenv("ORDERS_TABLE")
INVENTORY_TABLE = os.getenv("INVENTORY_TABLE")
