import os
import sys
from contextlib import asynccontextmanager
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add the common directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.utils.dependency_constants import (
    BOTO3_SESSION, BOTO3_CLIENT, BOTO3_RESOURCE, DYNAMODB_BOTO3_SESSION, DYNAMODB_BOTO3_CLIENT,
    DYNAMODB_BOTO3_RESOURCE, ENV_AWS_REGION, ENV_INVENTORY_TABLE, ENV_USERS_TABLE,ENV_ORDERS_TABLE)


# =============================================================================
# LOCAL TEST VARIABLES - Avoid hardcoded values in tests
# =============================================================================

# Test environment variables
TEST_USERS_TABLE = 'test-users-table'
TEST_ORDERS_TABLE = 'test-orders-table'
TEST_INVENTORY_TABLE = 'test-inventory-table'
TEST_AWS_REGION = 'us-west-2'

TEST_FIELD_TABLE = "Table"
TEST_FIELD_TABLE_NAME = "TableName"

# Set environment variables before importing the module
os.environ.setdefault(ENV_USERS_TABLE, TEST_USERS_TABLE)
os.environ.setdefault(ENV_ORDERS_TABLE, TEST_ORDERS_TABLE)
os.environ.setdefault(ENV_INVENTORY_TABLE, TEST_INVENTORY_TABLE)
os.environ.setdefault(ENV_AWS_REGION, TEST_AWS_REGION)

# Mock boto3 before any imports
with patch(BOTO3_RESOURCE), patch(BOTO3_CLIENT):
    from src.data.database.dynamodb_connection import (DynamoDBConnection,
                                                       DynamoDBManager,
                                                       get_dynamodb_manager)
    from src.exceptions.shared_exceptions import CNOPInternalServerException


class TestDynamoDBManager:
    """Test DynamoDBManager class"""

    @patch(DYNAMODB_BOTO3_SESSION)
    def test_dynamodb_manager_init_success(self, mock_boto3_session):
        mock_session = MagicMock()
        mock_resource = MagicMock()
        mock_users_table = MagicMock()
        mock_orders_table = MagicMock()
        mock_inventory_table = MagicMock()
        mock_boto3_session.return_value = mock_session
        mock_session.resource.return_value = mock_resource
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]

        manager = DynamoDBManager()
        assert manager.users_table_name == TEST_USERS_TABLE
        assert manager.orders_table_name == TEST_ORDERS_TABLE
        assert manager.inventory_table_name == TEST_INVENTORY_TABLE
        assert manager.region == TEST_AWS_REGION
        assert manager.users_table == mock_users_table
        assert manager.orders_table == mock_orders_table
        assert manager.inventory_table == mock_inventory_table


    @patch(DYNAMODB_BOTO3_SESSION)
    def test_dynamodb_manager_custom_region(self, mock_boto3_session):
        mock_session = MagicMock()
        mock_resource = MagicMock()
        mock_users_table = MagicMock()
        mock_orders_table = MagicMock()
        mock_inventory_table = MagicMock()
        mock_boto3_session.return_value = mock_session
        mock_session.resource.return_value = mock_resource
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]

        manager = DynamoDBManager()
        assert manager.region == TEST_AWS_REGION
        assert manager.users_table == mock_users_table
        assert manager.orders_table == mock_orders_table
        assert manager.inventory_table == mock_inventory_table

    @patch(DYNAMODB_BOTO3_SESSION)
    def test_health_check_success(self, mock_boto3_session):
        mock_session = MagicMock()
        mock_resource = MagicMock()
        mock_users_table = MagicMock()
        mock_orders_table = MagicMock()
        mock_inventory_table = MagicMock()
        mock_boto3_session.return_value = mock_session
        mock_session.resource.return_value = mock_resource
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]
        mock_users_table.meta.client.describe_table.return_value = {TEST_FIELD_TABLE: {TEST_FIELD_TABLE_NAME: TEST_USERS_TABLE}}
        mock_orders_table.meta.client.describe_table.return_value = {TEST_FIELD_TABLE: {TEST_FIELD_TABLE_NAME: TEST_ORDERS_TABLE}}
        mock_inventory_table.meta.client.describe_table.return_value = {TEST_FIELD_TABLE: {TEST_FIELD_TABLE_NAME: TEST_INVENTORY_TABLE}}

        manager = DynamoDBManager()
        result = manager.health_check()
        assert result is True
        mock_users_table.meta.client.describe_table.assert_called_once_with(TableName=TEST_USERS_TABLE)
        mock_orders_table.meta.client.describe_table.assert_called_once_with(TableName=TEST_ORDERS_TABLE)
        mock_inventory_table.meta.client.describe_table.assert_called_once_with(TableName=TEST_INVENTORY_TABLE)

    @patch(DYNAMODB_BOTO3_SESSION)
    def test_health_check_failure(self, mock_boto3_session):
        mock_session = MagicMock()
        mock_resource = MagicMock()
        mock_users_table = MagicMock()
        mock_orders_table = MagicMock()
        mock_inventory_table = MagicMock()
        mock_boto3_session.return_value = mock_session
        mock_session.resource.return_value = mock_resource
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]
        mock_users_table.meta.client.describe_table.side_effect = Exception("Table not found")

        manager = DynamoDBManager()
        result = manager.health_check()
        assert result is False

    @patch(DYNAMODB_BOTO3_SESSION)
    def test_get_connection(self, mock_boto3_session):
        mock_session = MagicMock()
        mock_resource = MagicMock()
        mock_users_table = MagicMock()
        mock_orders_table = MagicMock()
        mock_inventory_table = MagicMock()
        mock_boto3_session.return_value = mock_session
        mock_session.resource.return_value = mock_resource
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]

        manager = DynamoDBManager()
        connection = manager.get_connection()
        assert isinstance(connection, DynamoDBConnection)
        assert connection.users_table == mock_users_table
        assert connection.orders_table == mock_orders_table
        assert connection.inventory_table == mock_inventory_table


class TestDynamoDBConnection:
    """Test DynamoDBConnection class"""

    def test_dynamodb_connection_init(self):
        """Test DynamoDBConnection initialization"""
        # Create mock tables
        mock_users_table = Mock()
        mock_orders_table = Mock()
        mock_inventory_table = Mock()

        # Initialize connection
        connection = DynamoDBConnection(mock_users_table, mock_orders_table, mock_inventory_table)

        # Verify initialization
        assert connection.users_table == mock_users_table
        assert connection.orders_table == mock_orders_table
        assert connection.inventory_table == mock_inventory_table

    def test_dynamodb_connection_table_access(self):
        """Test that DynamoDBConnection provides table access"""
        # Create mock tables with different names for verification
        users_table_name = "users"
        orders_table_name = "orders"
        inventory_table_name = "inventory"
        mock_users_table = Mock()
        mock_users_table.name = users_table_name
        mock_orders_table = Mock()
        mock_orders_table.name = orders_table_name
        mock_inventory_table = Mock()
        mock_inventory_table.name = inventory_table_name

        # Initialize connection
        connection = DynamoDBConnection(mock_users_table, mock_orders_table, mock_inventory_table)

        # Verify table access
        assert connection.users_table.name == users_table_name
        assert connection.orders_table.name == orders_table_name
        assert connection.inventory_table.name == inventory_table_name


class TestGetDynamoDBManagerFunction:
    """Test get_dynamodb_manager function"""

    def test_get_dynamodb_manager_singleton(self):
        """Test get_dynamodb_manager returns singleton instance"""
        # Clear any existing manager
        import src.data.database.dynamodb_connection as module
        module._manager = None

        # Test the function returns a manager
        result = get_dynamodb_manager()
        assert result is not None
        assert isinstance(result, DynamoDBManager)

    def test_get_dynamodb_manager_singleton_behavior(self):
        """Test get_dynamodb_manager returns same instance"""
        # Clear any existing manager
        import src.data.database.dynamodb_connection as module
        module._manager = None

        # Get two instances
        manager1 = get_dynamodb_manager()
        manager2 = get_dynamodb_manager()

        assert manager1 is manager2




class TestDynamoDBIntegration:
    """Integration tests for DynamoDB components"""

    @patch(DYNAMODB_BOTO3_SESSION)
    def test_end_to_end_connection_flow(self, mock_boto3_session):
        mock_session = MagicMock()
        mock_resource = MagicMock()
        mock_users_table = MagicMock()
        mock_orders_table = MagicMock()
        mock_inventory_table = MagicMock()
        mock_boto3_session.return_value = mock_session
        mock_session.resource.return_value = mock_resource
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]
        mock_users_table.meta.client.describe_table.return_value = {TEST_FIELD_TABLE: {TEST_FIELD_TABLE_NAME: TEST_USERS_TABLE}}
        mock_orders_table.meta.client.describe_table.return_value = {TEST_FIELD_TABLE: {TEST_FIELD_TABLE_NAME: TEST_ORDERS_TABLE}}
        mock_inventory_table.meta.client.describe_table.return_value = {TEST_FIELD_TABLE: {TEST_FIELD_TABLE_NAME: TEST_INVENTORY_TABLE}}

        manager = DynamoDBManager()
        health_result = manager.health_check()
        assert health_result is True
        connection = manager.get_connection()
        assert hasattr(connection, 'users_table')
        assert hasattr(connection, 'orders_table')
        assert hasattr(connection, 'inventory_table')
        assert connection.users_table == mock_users_table
        assert connection.orders_table == mock_orders_table
        assert connection.inventory_table == mock_inventory_table

    @patch(DYNAMODB_BOTO3_SESSION)
    def test_table_name_configuration(self, mock_boto3_session):
        mock_session = MagicMock()
        mock_resource = MagicMock()
        mock_users_table = MagicMock()
        mock_orders_table = MagicMock()
        mock_inventory_table = MagicMock()
        mock_boto3_session.return_value = mock_session
        mock_session.resource.return_value = mock_resource
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]

        manager = DynamoDBManager()
        assert manager.users_table_name == TEST_USERS_TABLE
        assert manager.orders_table_name == TEST_ORDERS_TABLE
        assert manager.inventory_table_name == TEST_INVENTORY_TABLE
        table_calls = [call[0][0] for call in mock_resource.Table.call_args_list]
        assert TEST_USERS_TABLE in table_calls
        assert TEST_ORDERS_TABLE in table_calls
        assert TEST_INVENTORY_TABLE in table_calls