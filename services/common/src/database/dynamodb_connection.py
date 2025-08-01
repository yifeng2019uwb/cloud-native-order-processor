# services/common/database/dynamodb_connection.py
import os
import boto3
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Universal session pattern for IRSA and AssumeRole

def get_boto3_session():
    region = os.getenv("AWS_REGION")
    # If running in EKS with IRSA, let boto3 handle it natively
    if os.getenv("AWS_WEB_IDENTITY_TOKEN_FILE"):
        return boto3.Session(region_name=region)
    # Otherwise, if AWS_ROLE_ARN is set, assume the role
    role_arn = os.getenv("AWS_ROLE_ARN")
    if role_arn:
        sts = boto3.client("sts", region_name=region)
        resp = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName="order-processor-session"
        )
        creds = resp["Credentials"]
        return boto3.Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
            region_name=region
        )
    # Fallback: use default credentials (for local dev, etc.)
    return boto3.Session(region_name=region)

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

        self.region = os.getenv("AWS_REGION")
        if not self.region:
            raise ValueError("AWS_REGION environment variable is required")

        # Use the universal session pattern
        session = get_boto3_session()
        self.dynamodb = session.resource('dynamodb', region_name=self.region)
        self.client = session.client('dynamodb', region_name=self.region)
        logger.info("DynamoDB connection initialized using universal session pattern (IRSA/AssumeRole/local)")

        # ✅ Get table references
        self.users_table = self.dynamodb.Table(self.users_table_name)
        self.orders_table = self.dynamodb.Table(self.orders_table_name)
        self.inventory_table = self.dynamodb.Table(self.inventory_table_name)

        logger.info(f"DynamoDB initialized - Users: {self.users_table_name}, Orders: {self.orders_table_name}, Inventory: {self.inventory_table_name}")

    def health_check(self) -> bool:
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

    def get_connection(self) -> 'DynamoDBConnection':
        """Get DynamoDB connection wrapper"""
        return DynamoDBConnection(self.users_table, self.orders_table, self.inventory_table)


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
def get_dynamodb():
    """FastAPI dependency to get DynamoDB connection"""
    return dynamodb_manager.get_connection()