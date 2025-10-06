# Database configuration
from .database_constants import (
    get_aws_region,
    get_users_table_name,
    get_orders_table_name,
    get_inventory_table_name,
    EnvironmentVariables,
    DefaultValues
)
from ..exceptions import CNOPConfigurationException

# DynamoDB Configuration
DYNAMODB_REGION = get_aws_region()
if not DYNAMODB_REGION:
    raise CNOPConfigurationException(f"{EnvironmentVariables.AWS_REGION} environment variable is required")
USERS_TABLE = get_users_table_name()
ORDERS_TABLE = get_orders_table_name()
INVENTORY_TABLE = get_inventory_table_name()
