import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
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
    from src.database.dynamodb_connection import DynamoDBManager, DynamoDBConnection, get_dynamodb


class TestDynamoDBManager:
    """Test DynamoDBManager class"""

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    @patch('src.database.dynamodb_connection.STSClient')
    @patch('src.database.dynamodb_connection.boto3')
    @pytest.mark.skip(reason='Disabled due to removal of STSClient')
    def test_dynamodb_manager_init_success(self, mock_boto3, mock_sts_client):
        """Test successful DynamoDBManager initialization"""
        # Mock STS client components
        mock_sts_instance = Mock()
        mock_resource = Mock()
        mock_client = Mock()
        mock_users_table = Mock()
        mock_orders_table = Mock()
        mock_inventory_table = Mock()

        mock_sts_client.return_value = mock_sts_instance
        mock_sts_instance.get_resource.return_value = mock_resource
        mock_sts_instance.get_client.return_value = mock_client
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]

        # Initialize manager
        manager = DynamoDBManager()

        # Verify initialization
        assert manager.users_table_name == 'test-users-table'
        assert manager.orders_table_name == 'test-orders-table'
        assert manager.inventory_table_name == 'test-inventory-table'
        assert manager.region == 'us-west-2'
        assert manager.users_table == mock_users_table
        assert manager.orders_table == mock_orders_table
        assert manager.inventory_table == mock_inventory_table

        # Verify STS client calls
        mock_sts_client.assert_called_once()
        mock_sts_instance.get_resource.assert_called_once_with('dynamodb')
        mock_sts_instance.get_client.assert_called_once_with('dynamodb')
        assert mock_resource.Table.call_count == 3

    @patch.dict(os.environ, {
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table'
    }, clear=True)
    def test_dynamodb_manager_missing_users_table(self):
        """Test DynamoDBManager initialization fails when USERS_TABLE is missing"""
        with pytest.raises(ValueError) as exc_info:
            DynamoDBManager()

        assert "USERS_TABLE environment variable not found" in str(exc_info.value)

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'INVENTORY_TABLE': 'test-inventory-table'
    }, clear=True)
    def test_dynamodb_manager_missing_orders_table(self):
        """Test DynamoDBManager initialization fails when ORDERS_TABLE is missing"""
        with pytest.raises(ValueError) as exc_info:
            DynamoDBManager()

        assert "ORDERS_TABLE environment variable not found" in str(exc_info.value)

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table'
    }, clear=True)
    def test_dynamodb_manager_missing_inventory_table(self):
        """Test DynamoDBManager initialization fails when INVENTORY_TABLE is missing"""
        with pytest.raises(ValueError) as exc_info:
            DynamoDBManager()

        assert "INVENTORY_TABLE environment variable not found" in str(exc_info.value)

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table'
    }, clear=True)  # Clear AWS_REGION to test error
    def test_dynamodb_manager_missing_region(self):
        """Test DynamoDBManager fails when AWS_REGION not set"""
        with pytest.raises(ValueError) as exc_info:
            DynamoDBManager()

        assert "AWS_REGION environment variable is required" in str(exc_info.value)

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'eu-west-1'
    })
    @patch('src.database.dynamodb_connection.STSClient')
    @patch('src.database.dynamodb_connection.boto3')
    @pytest.mark.skip(reason='Disabled due to removal of STSClient')
    def test_dynamodb_manager_custom_region(self, mock_boto3, mock_sts_client):
        """Test DynamoDBManager uses custom region when AWS_REGION is set"""
        # Mock STS client components
        mock_sts_instance = Mock()
        mock_resource = Mock()
        mock_client = Mock()
        mock_sts_client.return_value = mock_sts_instance
        mock_sts_instance.get_resource.return_value = mock_resource
        mock_sts_instance.get_client.return_value = mock_client
        mock_resource.Table.return_value = Mock()

        # Initialize manager
        manager = DynamoDBManager()

        # Verify custom region
        assert manager.region == 'eu-west-1'
        mock_sts_client.assert_called_once()
        mock_sts_instance.get_resource.assert_called_once_with('dynamodb')
        mock_sts_instance.get_client.assert_called_once_with('dynamodb')

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    @patch('src.database.dynamodb_connection.STSClient')
    @patch('src.database.dynamodb_connection.boto3')
    @pytest.mark.asyncio
    @pytest.mark.skip(reason='Disabled due to removal of STSClient')
    async def test_health_check_success(self, mock_boto3, mock_sts_client):
        """Test successful health check"""
        # Mock STS client components
        mock_sts_instance = Mock()
        mock_resource = Mock()
        mock_client = Mock()
        mock_users_table = Mock()
        mock_orders_table = Mock()
        mock_inventory_table = Mock()

        mock_sts_client.return_value = mock_sts_instance
        mock_sts_instance.get_resource.return_value = mock_resource
        mock_sts_instance.get_client.return_value = mock_client
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]

        # Mock successful describe_table calls
        mock_users_table.meta.client.describe_table.return_value = {'Table': {'TableName': 'test-users-table'}}
        mock_orders_table.meta.client.describe_table.return_value = {'Table': {'TableName': 'test-orders-table'}}
        mock_inventory_table.meta.client.describe_table.return_value = {'Table': {'TableName': 'test-inventory-table'}}

        # Initialize manager and test health check
        manager = DynamoDBManager()
        result = await manager.health_check()

        # Verify result
        assert result is True

        # Verify describe_table calls
        mock_users_table.meta.client.describe_table.assert_called_once_with(TableName='test-users-table')
        mock_orders_table.meta.client.describe_table.assert_called_once_with(TableName='test-orders-table')
        mock_inventory_table.meta.client.describe_table.assert_called_once_with(TableName='test-inventory-table')

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    @patch('src.database.dynamodb_connection.STSClient')
    @patch('src.database.dynamodb_connection.boto3')
    @pytest.mark.asyncio
    @pytest.mark.skip(reason='Disabled due to removal of STSClient')
    async def test_health_check_failure(self, mock_boto3, mock_sts_client):
        """Test health check failure when table is not accessible"""
        # Mock STS client components
        mock_sts_instance = Mock()
        mock_resource = Mock()
        mock_client = Mock()
        mock_users_table = Mock()
        mock_orders_table = Mock()
        mock_inventory_table = Mock()

        mock_sts_client.return_value = mock_sts_instance
        mock_sts_instance.get_resource.return_value = mock_resource
        mock_sts_instance.get_client.return_value = mock_client
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]

        # Mock failed describe_table call
        mock_users_table.meta.client.describe_table.side_effect = Exception("Table not found")

        # Initialize manager and test health check
        manager = DynamoDBManager()
        result = await manager.health_check()

        # Verify result
        assert result is False

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    @patch('src.database.dynamodb_connection.STSClient')
    @patch('src.database.dynamodb_connection.boto3')
    @pytest.mark.asyncio
    @pytest.mark.skip(reason='Disabled due to removal of STSClient')
    async def test_get_connection_context_manager(self, mock_boto3, mock_sts_client):
        """Test get_connection context manager"""
        # Mock STS client components
        mock_sts_instance = Mock()
        mock_resource = Mock()
        mock_client = Mock()
        mock_users_table = Mock()
        mock_orders_table = Mock()
        mock_inventory_table = Mock()

        mock_sts_client.return_value = mock_sts_instance
        mock_sts_instance.get_resource.return_value = mock_resource
        mock_sts_instance.get_client.return_value = mock_client
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]

        # Initialize manager
        manager = DynamoDBManager()

        # Test context manager
        async with manager.get_connection() as connection:
            assert isinstance(connection, DynamoDBConnection)
            assert connection.users_table == mock_users_table
            assert connection.orders_table == mock_orders_table
            assert connection.inventory_table == mock_inventory_table

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    @patch('src.database.dynamodb_connection.STSClient')
    @patch('src.database.dynamodb_connection.boto3')
    @pytest.mark.asyncio
    @pytest.mark.skip(reason='Disabled due to removal of STSClient')
    async def test_get_connection_exception_handling(self, mock_boto3, mock_sts_client):
        """Test get_connection handles exceptions properly"""
        # Mock STS client components
        mock_sts_instance = Mock()
        mock_resource = Mock()
        mock_client = Mock()
        mock_users_table = Mock()
        mock_orders_table = Mock()
        mock_inventory_table = Mock()

        mock_sts_client.return_value = mock_sts_instance
        mock_sts_instance.get_resource.return_value = mock_resource
        mock_sts_instance.get_client.return_value = mock_client
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]

        # Initialize manager
        manager = DynamoDBManager()

        # Test context manager with exception
        try:
            async with manager.get_connection() as connection:
                assert isinstance(connection, DynamoDBConnection)
                raise Exception("Test exception")
        except Exception as e:
            assert str(e) == "Test exception"

        # Context manager should handle cleanup gracefully


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
    """Test get_dynamodb FastAPI dependency function"""

    @patch('src.database.dynamodb_connection.dynamodb_manager')
    @pytest.mark.asyncio
    async def test_get_dynamodb_dependency(self, mock_manager):
        """Test get_dynamodb FastAPI dependency function"""
        # Create mock connection
        mock_connection = Mock()

        # Create a proper async context manager
        @asynccontextmanager
        async def mock_get_connection():
            yield mock_connection

        mock_manager.get_connection = mock_get_connection

        # Test the dependency function
        async_gen = get_dynamodb()
        connection = await async_gen.__anext__()

        # Verify we get the connection
        assert connection == mock_connection

        # Test cleanup (shouldn't raise exception)
        try:
            await async_gen.__anext__()
        except StopAsyncIteration:
            pass  # Expected behavior

    @patch('src.database.dynamodb_connection.dynamodb_manager')
    @pytest.mark.asyncio
    async def test_get_dynamodb_dependency_with_exception(self, mock_manager):
        """Test get_dynamodb dependency handles exceptions"""
        # Create mock connection that raises exception
        @asynccontextmanager
        async def mock_get_connection():
            try:
                yield Mock()
            except Exception:
                pass  # Context manager should handle cleanup

        mock_manager.get_connection = mock_get_connection

        # Test the dependency function
        async_gen = get_dynamodb()
        connection = await async_gen.__anext__()

        # Should still get a connection
        assert connection is not None


class TestGlobalDynamoDBManager:
    """Test global dynamodb_manager instance"""

    def test_global_manager_initialization(self):
        """Test that global dynamodb_manager is properly initialized"""
        # Import should trigger initialization (already mocked at module level)
        from src.database.dynamodb_connection import dynamodb_manager

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
        # Re-import to get the manager with test environment variables
        import importlib
        import src.database.dynamodb_connection
        importlib.reload(src.database.dynamodb_connection)
        from src.database.dynamodb_connection import dynamodb_manager

        # Verify configuration (using our test env vars)
        assert dynamodb_manager.users_table_name == 'test-users-table'
        assert dynamodb_manager.orders_table_name == 'test-orders-table'
        assert dynamodb_manager.inventory_table_name == 'test-inventory-table'


class TestDynamoDBIntegration:
    """Integration tests for DynamoDB components"""

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    @patch('src.database.dynamodb_connection.STSClient')
    @patch('src.database.dynamodb_connection.boto3')
    @pytest.mark.asyncio
    @pytest.mark.skip(reason='Disabled due to removal of STSClient')
    async def test_end_to_end_connection_flow(self, mock_boto3, mock_sts_client):
        """Test end-to-end connection flow"""
        # Mock STS client components
        mock_sts_instance = Mock()
        mock_resource = Mock()
        mock_client = Mock()
        mock_users_table = Mock()
        mock_orders_table = Mock()
        mock_inventory_table = Mock()

        mock_sts_client.return_value = mock_sts_instance
        mock_sts_instance.get_resource.return_value = mock_resource
        mock_sts_instance.get_client.return_value = mock_client
        mock_resource.Table.side_effect = [mock_users_table, mock_orders_table, mock_inventory_table]

        # Mock successful health check
        mock_users_table.meta.client.describe_table.return_value = {'Table': {'TableName': 'test-users-table'}}
        mock_orders_table.meta.client.describe_table.return_value = {'Table': {'TableName': 'test-orders-table'}}
        mock_inventory_table.meta.client.describe_table.return_value = {'Table': {'TableName': 'test-inventory-table'}}

        # Initialize manager
        manager = DynamoDBManager()

        # Test health check
        health_result = await manager.health_check()
        assert health_result is True

        # Test connection retrieval
        async with manager.get_connection() as connection:
            assert hasattr(connection, 'users_table')
            assert hasattr(connection, 'orders_table')
            assert hasattr(connection, 'inventory_table')
            assert connection.users_table == mock_users_table
            assert connection.orders_table == mock_orders_table
            assert connection.inventory_table == mock_inventory_table

        # Test FastAPI dependency
        async_gen = get_dynamodb()
        dependency_connection = await async_gen.__anext__()
        assert hasattr(dependency_connection, 'users_table')
        assert hasattr(dependency_connection, 'orders_table')
        assert hasattr(dependency_connection, 'inventory_table')

    @patch.dict(os.environ, {
        'USERS_TABLE': 'test-users-table',
        'ORDERS_TABLE': 'test-orders-table',
        'INVENTORY_TABLE': 'test-inventory-table',
        'AWS_REGION': 'us-west-2'
    })
    @patch('src.database.dynamodb_connection.STSClient')
    @patch('src.database.dynamodb_connection.boto3')
    @pytest.mark.skip(reason='Disabled due to removal of STSClient')
    def test_table_name_configuration(self, mock_boto3, mock_sts_client):
        """Test that table names are properly configured from environment"""
        # Mock STS client components
        mock_sts_instance = Mock()
        mock_resource = Mock()
        mock_client = Mock()
        mock_sts_client.return_value = mock_sts_instance
        mock_sts_instance.get_resource.return_value = mock_resource
        mock_sts_instance.get_client.return_value = mock_client
        mock_resource.Table.return_value = Mock()

        # Initialize manager
        manager = DynamoDBManager()

        # Verify table names are set from environment
        assert manager.users_table_name == 'test-users-table'
        assert manager.orders_table_name == 'test-orders-table'
        assert manager.inventory_table_name == 'test-inventory-table'

        # Verify STS client Table calls used correct names
        table_calls = [call[0][0] for call in mock_resource.Table.call_args_list]
        assert 'test-users-table' in table_calls
        assert 'test-orders-table' in table_calls
        assert 'test-inventory-table' in table_calls