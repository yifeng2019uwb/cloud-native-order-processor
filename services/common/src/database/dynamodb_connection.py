# services/common/database/dynamodb_connection.py
import os
import boto3
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

# Import STS client
try:
    from ..aws.sts_client import STSClient
except ImportError:
    # Fallback for when common package is not installed
    STSClient = None


class DynamoDBManager:
    """DynamoDB Manager - Only handles connections and table references"""

    def __init__(self):
        # ✅ Get table names from environment variables (set by Terraform)
        self.users_table_name = os.getenv("USERS_TABLE")
        self.orders_table_name = os.getenv("ORDERS_TABLE")
        self.inventory_table_name = os.getenv("INVENTORY_TABLE")

        # ✅ Validate required tables are configured
        if not self.users_table_name:
            raise ValueError("USERS_TABLE environment variable not found")
        if not self.orders_table_name:
            raise ValueError("ORDERS_TABLE environment variable not found")
        if not self.inventory_table_name:
            raise ValueError("INVENTORY_TABLE environment variable not found")

        # Initialize boto3 client and resource with STS support
        self.region = os.getenv("AWS_REGION")
        if not self.region:
            raise ValueError("AWS_REGION environment variable is required")

        # Use STS client if available, otherwise fallback to direct boto3
        if STSClient:
            sts_client = STSClient()
            self.dynamodb = sts_client.get_resource('dynamodb')
            self.client = sts_client.get_client('dynamodb')
            logger.info("Using STS client for DynamoDB connection")
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
            self.client = boto3.client('dynamodb', region_name=self.region)
            logger.info("Using direct boto3 for DynamoDB connection")

        # ✅ Get table references
        self.users_table = self.dynamodb.Table(self.users_table_name)
        self.orders_table = self.dynamodb.Table(self.orders_table_name)
        self.inventory_table = self.dynamodb.Table(self.inventory_table_name)

        logger.info(f"DynamoDB initialized - Users: {self.users_table_name}, Orders: {self.orders_table_name}, Inventory: {self.inventory_table_name}")

    async def health_check(self) -> bool:
        """Check if all DynamoDB tables are accessible"""
        try:
            # Test connection by describing tables
            self.users_table.meta.client.describe_table(TableName=self.users_table_name)
            self.orders_table.meta.client.describe_table(TableName=self.orders_table_name)
            self.inventory_table.meta.client.describe_table(TableName=self.inventory_table_name)
            return True
        except Exception as e:
            logger.error(f"DynamoDB health check failed: {e}")
            return False

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator['DynamoDBConnection', None]:
        """Get DynamoDB connection wrapper"""
        connection = DynamoDBConnection(self.users_table, self.orders_table, self.inventory_table)
        try:
            yield connection
        finally:
            # DynamoDB doesn't need explicit connection cleanup
            pass


class DynamoDBConnection:
    """
    DynamoDB connection wrapper - ONLY provides table access
    NO CRUD operations - those belong in DAO layer
    """

    def __init__(self, users_table, orders_table, inventory_table):
        # ✅ ONLY store table references - NO business logic
        self.users_table = users_table
        self.orders_table = orders_table
        self.inventory_table = inventory_table


# ✅ Global DynamoDB manager instance
dynamodb_manager = DynamoDBManager()


# ✅ FastAPI dependency for getting database connection
async def get_dynamodb():
    """FastAPI dependency to get DynamoDB connection"""
    async with dynamodb_manager.get_connection() as conn:
        yield conn