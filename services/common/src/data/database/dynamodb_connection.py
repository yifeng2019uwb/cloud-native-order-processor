"""
DynamoDB connection manager for microservices.

Provides centralized DynamoDB connection management with connection pooling,
retry logic, and health monitoring for all services.
"""

import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from ...exceptions.shared_exceptions import CNOPInternalServerException
from ...shared.logging import BaseLogger, LogActions, Loggers
from .database_constants import (
    EnvironmentVariables,
    DefaultValues,
    DatabaseConfig,
    get_aws_region,
    get_users_table_name,
    get_orders_table_name,
    get_inventory_table_name,
    get_aws_web_identity_token_file,
    get_aws_role_arn
)

logger = BaseLogger(Loggers.DATABASE, log_to_file=True)

# Universal session pattern for IRSA and AssumeRole

def get_boto3_session():
    region = get_aws_region()
    # If running in EKS with IRSA, let boto3 handle it natively
    if get_aws_web_identity_token_file():
        return boto3.Session(region_name=region)
    # Otherwise, if AWS_ROLE_ARN is set, assume the role
    role_arn = get_aws_role_arn()
    if role_arn:
        sts = boto3.client(DatabaseConfig.STS_SERVICE_NAME, region_name=region)
        resp = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName=DatabaseConfig.ROLE_SESSION_NAME
        )
        creds = resp[DatabaseConfig.CREDENTIALS]
        return boto3.Session(
            aws_access_key_id=creds[DatabaseConfig.ACCESS_KEY_ID],
            aws_secret_access_key=creds[DatabaseConfig.SECRET_ACCESS_KEY],
            aws_session_token=creds[DatabaseConfig.SESSION_TOKEN],
            region_name=region
        )
    # Fallback: use default credentials (for local dev, etc.)
    return boto3.Session(region_name=region)

class DynamoDBManager:
    """DynamoDB Manager - Only handles connections and table references"""

    def __init__(self):
        """Initialize DynamoDB manager with table references"""
        # Get environment variables using constants - check if they exist first
        self.users_table_name = get_users_table_name()
        if not self.users_table_name:
            raise CNOPInternalServerException(f"{EnvironmentVariables.USERS_TABLE} environment variable not found")

        self.orders_table_name =get_orders_table_name()
        if not self.orders_table_name:
            raise CNOPInternalServerException(f"{EnvironmentVariables.ORDERS_TABLE} environment variable not found")

        self.inventory_table_name = get_inventory_table_name()
        if not self.inventory_table_name:
            raise CNOPInternalServerException(f"{EnvironmentVariables.INVENTORY_TABLE} environment variable not found")

        self.region = get_aws_region()
        if not self.region:
            raise CNOPInternalServerException(f"{EnvironmentVariables.AWS_REGION} environment variable is required")

        # Use the universal session pattern
        session = get_boto3_session()
        self.dynamodb = session.resource(DatabaseConfig.DYNAMODB_SERVICE_NAME, region_name=self.region)
        self.client = session.client(DatabaseConfig.DYNAMODB_SERVICE_NAME, region_name=self.region)
        logger.info(
            action=LogActions.DB_CONNECT,
            message="DynamoDB connection initialized using universal session pattern (IRSA/AssumeRole/local)"
        )

        # Get table references
        self.users_table = self.dynamodb.Table(self.users_table_name)
        self.orders_table = self.dynamodb.Table(self.orders_table_name)
        self.inventory_table = self.dynamodb.Table(self.inventory_table_name)

        logger.info(
            action=LogActions.DB_CONNECT,
            message=f"DynamoDB initialized - Users: {self.users_table_name}, Orders: {self.orders_table_name}, Inventory: {self.inventory_table_name}"
        )

    def health_check(self) -> bool:
        """Check if all DynamoDB tables are accessible"""
        try:
            # Test connection by describing tables
            self.users_table.meta.client.describe_table(TableName=self.users_table_name)
            self.orders_table.meta.client.describe_table(TableName=self.orders_table_name)
            self.inventory_table.meta.client.describe_table(TableName=self.inventory_table_name)
            return True
        except Exception as e:
            logger.error(
                action=LogActions.ERROR,
                message=f"DynamoDB health check failed: {e}"
            )
            return False

    def get_connection(self) -> 'DynamoDBConnection':
        """Get DynamoDB connection wrapper"""
        return DynamoDBConnection(self.users_table, self.orders_table, self.inventory_table)

    def get_client(self):
        """Get DynamoDB client for batch operations"""
        return self.client


class DynamoDBConnection:
    """
    DynamoDB connection wrapper - ONLY provides table access
    NO CRUD operations - those belong in DAO layer
    """

    def __init__(self, users_table, orders_table, inventory_table):
        # Store table references only
        self.users_table = users_table
        self.orders_table = orders_table
        self.inventory_table = inventory_table


# Optional improvement: Make it more explicit
_manager: Optional[DynamoDBManager] = None

def get_dynamodb_manager() -> DynamoDBManager:
    global _manager
    if _manager is None:
        _manager = DynamoDBManager()
    return _manager