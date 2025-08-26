import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock, call
from contextlib import asynccontextmanager

# Add the common directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Set environment variables before importing the module
os.environ.setdefault('USERS_TABLE', 'test-users-table')
os.environ.setdefault('ORDERS_TABLE', 'test-orders-table')
os.environ.setdefault('INVENTORY_TABLE', 'test-inventory-table')
os.environ.setdefault('AWS_REGION', 'us-west-2')

# Mock boto3 before any imports
with patch('boto3.resource'), patch('boto3.client'):
    from src.data.database.dynamodb_connection import DynamoDBManager, DynamoDBConnection, get_dynamodb, dynamodb_manager
    from src.exceptions.shared_exceptions import CNOPInternalServerException


class TestDynamoDBManager:
    """Test DynamoDBManager class"""

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    @patch('src.data.database.dynamodb_connection.boto3.Session')
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
        assert manager.users_table_name == 'test-users-table'
        assert manager.orders_table_name == 'test-orders-table'
        assert manager.inventory_table_name == 'test-inventory-table'
        assert manager.region == 'us-west-2'
        assert manager.users_table == mock_users_table
        assert manager.orders_table == mock_orders_table
        assert manager.inventory_table == mock_inventory_table

    def test_init_missing_users_table(self):
        """Test initialization with missing USERS_TABLE environment variable"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(CNOPInternalServerException) as exc_info:
                DynamoDBManager()
        assert "USERS_TABLE environment variable not found" in str(exc_info.value)

    def test_init_missing_orders_table(self):
        """Test initialization with missing ORDERS_TABLE environment variable"""
        with patch.dict(os.environ, {'USERS_TABLE': 'test-users'}, clear=True):
            with pytest.raises(CNOPInternalServerException) as exc_info:
                DynamoDBManager()
        assert "ORDERS_TABLE environment variable not found" in str(exc_info.value)

    def test_init_missing_inventory_table(self):
        """Test initialization with missing INVENTORY_TABLE environment variable"""
        with patch.dict(os.environ, {
            'USERS_TABLE': 'test-users',
            'ORDERS_TABLE': 'test-orders'
        }, clear=True):
            with pytest.raises(CNOPInternalServerException) as exc_info:
                DynamoDBManager()
        assert "INVENTORY_TABLE environment variable not found" in str(exc_info.value)

    def test_init_missing_aws_region(self):
        """Test initialization with missing AWS_REGION environment variable"""
        with patch.dict(os.environ, {
            'USERS_TABLE': 'test-users',
            'ORDERS_TABLE': 'test-orders',
            'INVENTORY_TABLE': 'test-inventory'
        }, clear=True):
            with pytest.raises(CNOPInternalServerException) as exc_info:
                DynamoDBManager()
        assert "AWS_REGION environment variable is required" in str(exc_info.value)

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table'
    }, clear=True)  # Clear AWS_REGION to test error
    def test_dynamodb_manager_missing_region(self):
        """Test DynamoDBManager initialization fails when AWS_REGION is missing"""
        with patch.dict(os.environ, {
            'USERS_TABLE': 'test-users-table',
            'ORDERS_TABLE': 'test-orders-table',
            'INVENTORY_TABLE': 'test-inventory-table'
        }, clear=True):
            with pytest.raises(CNOPInternalServerException) as exc_info:
                DynamoDBManager()
            assert "AWS_REGION environment variable is required" in str(exc_info.value)

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'eu-west-1'
    })
    @patch('src.data.database.dynamodb_connection.boto3.Session')
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
        assert manager.region == 'eu-west-1'
        assert manager.users_table == mock_users_table
        assert manager.orders_table == mock_orders_table
        assert manager.inventory_table == mock_inventory_table

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    @patch('src.data.database.dynamodb_connection.boto3.Session')
    def test_health_check_success(self, mock_boto3_session):
        mock_session = MagicMock()
        mock_resource = MagicMock()
        mock_users_table = MagicMock()
        mock_orders_table = MagicMock()
        mock_inventory_table = MagicMock()
        mock_boto3_session.return_value = mock_session
        mock_session.resource.return_value = mock_resource
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]
        mock_users_table.meta.client.describe_table.return_value = {'Table': {'TableName': 'test-users-table'}}
        mock_orders_table.meta.client.describe_table.return_value = {'Table': {'TableName': 'test-orders-table'}}
        mock_inventory_table.meta.client.describe_table.return_value = {'Table': {'TableName': 'test-inventory-table'}}

        manager = DynamoDBManager()
        result = manager.health_check()
        assert result is True
        mock_users_table.meta.client.describe_table.assert_called_once_with(TableName='test-users-table')
        mock_orders_table.meta.client.describe_table.assert_called_once_with(TableName='test-orders-table')
        mock_inventory_table.meta.client.describe_table.assert_called_once_with(TableName='test-inventory-table')

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    @patch('src.data.database.dynamodb_connection.boto3.Session')
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

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    @patch('src.data.database.dynamodb_connection.boto3.Session')
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
        mock_users_table = Mock()
        mock_users_table.name = 'users'
        mock_orders_table = Mock()
        mock_orders_table.name = 'orders'
        mock_inventory_table = Mock()
        mock_inventory_table.name = 'inventory'

        # Initialize connection
        connection = DynamoDBConnection(mock_users_table, mock_orders_table, mock_inventory_table)

        # Verify table access
        assert connection.users_table.name == 'users'
        assert connection.orders_table.name == 'orders'
        assert connection.inventory_table.name == 'inventory'


class TestGetDynamoDBFunction:
    """Test get_dynamodb function"""

    @patch('src.data.database.dynamodb_connection.dynamodb_manager')
    def test_get_dynamodb_dependency(self, mock_manager):
        """Test get_dynamodb FastAPI dependency function"""
        # Create mock connection
        mock_connection = Mock()
        mock_manager.get_connection.return_value = mock_connection

        # Test the dependency function
        result = get_dynamodb()
        assert result == mock_connection
        mock_manager.get_connection.assert_called_once()

    @patch('src.data.database.dynamodb_connection.dynamodb_manager')
    def test_get_dynamodb_dependency_with_exception(self, mock_manager):
        """Test get_dynamodb dependency handles exceptions"""
        # Create mock connection that raises exception
        mock_manager.get_connection.side_effect = Exception("Connection failed")

        # Test the dependency function
        with pytest.raises(Exception) as exc_info:
            get_dynamodb()
        assert "Connection failed" in str(exc_info.value)


class TestGlobalDynamoDBManager:
    """Test global dynamodb_manager instance"""

    def test_global_manager_initialization(self):
        """Test that global dynamodb_manager is properly initialized"""

        # Verify manager is initialized
        assert dynamodb_manager is not None
        assert hasattr(dynamodb_manager, 'users_table_name')
        assert hasattr(dynamodb_manager, 'orders_table_name')
        assert hasattr(dynamodb_manager, 'inventory_table_name')

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    def test_global_manager_configuration(self):
        """Test global manager has correct configuration"""
        # Verify manager is initialized
        assert dynamodb_manager is not None
        assert hasattr(dynamodb_manager, 'users_table_name')
        assert hasattr(dynamodb_manager, 'orders_table_name')
        assert hasattr(dynamodb_manager, 'inventory_table_name')


class TestDynamoDBIntegration:
    """Integration tests for DynamoDB components"""

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    @patch('src.data.database.dynamodb_connection.boto3.Session')
    def test_end_to_end_connection_flow(self, mock_boto3_session):
        mock_session = MagicMock()
        mock_resource = MagicMock()
        mock_users_table = MagicMock()
        mock_orders_table = MagicMock()
        mock_inventory_table = MagicMock()
        mock_boto3_session.return_value = mock_session
        mock_session.resource.return_value = mock_resource
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]
        mock_users_table.meta.client.describe_table.return_value = {'Table': {'TableName': 'test-users-table'}}
        mock_orders_table.meta.client.describe_table.return_value = {'Table': {'TableName': 'test-orders-table'}}
        mock_inventory_table.meta.client.describe_table.return_value = {'Table': {'TableName': 'test-inventory-table'}}

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

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    @patch('src.data.database.dynamodb_connection.boto3.Session')
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
        assert manager.users_table_name == 'test-users-table'
        assert manager.orders_table_name == 'test-orders-table'
        assert manager.inventory_table_name == 'test-inventory-table'
        table_calls = [call[0][0] for call in mock_resource.Table.call_args_list]
        assert 'test-users-table' in table_calls
        assert 'test-orders-table' in table_calls
        assert 'test-inventory-table' in table_calls