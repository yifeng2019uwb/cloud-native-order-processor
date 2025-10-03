"""
Tests for Asset Transaction DAO
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from src.data.dao.asset.asset_transaction_dao import AssetTransactionDAO
from src.data.entities.asset import (AssetTransaction, AssetTransactionItem,
                                     AssetTransactionStatus,
                                     AssetTransactionType)
from src.data.exceptions import CNOPDatabaseOperationException
from src.exceptions.shared_exceptions import CNOPTransactionNotFoundException


class TestAssetTransactionDAO:
    """Test AssetTransactionDAO class"""

    @pytest.fixture
    def mock_db_connection(self):
        """Create mock database connection"""
        mock_connection = MagicMock()
        mock_users_table = MagicMock()
        mock_connection.users_table = mock_users_table
        return mock_connection

    @pytest.fixture
    def asset_transaction_dao(self, mock_db_connection):
        """Create AssetTransactionDAO instance with mock connection"""
        return AssetTransactionDAO(mock_db_connection)

    @pytest.fixture
    def sample_transaction_create(self):
        """Sample transaction create for testing"""
        return AssetTransaction(
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("2.5"),
            price=Decimal("50000.00"),
            total_amount=Decimal("125000.00"),
            order_id="order-123"
        )

    @pytest.fixture
    def sample_asset_transaction(self):
        """Sample asset transaction for testing"""
        now = datetime.now(timezone.utc)
        return AssetTransaction(
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("2.5"),
            price=Decimal("50000.00"),
            total_amount=Decimal("125000.00"),
            order_id="order-123",
            status=AssetTransactionStatus.COMPLETED,
            created_at=now
        )

    def test_create_asset_transaction_success(self, asset_transaction_dao, sample_transaction_create, mock_db_connection):
        """Test successful asset transaction creation"""
        # Mock database response - the actual timestamp will be generated at runtime
        mock_db_connection.users_table.put_item.return_value = {
            'username': 'testuser123',
            'asset_id': 'BTC',
            'transaction_type': 'BUY',
            'quantity': '2.5',
            'price': '50000.00',
            'total_amount': '125000.00',
            'order_id': 'order-123',
            'status': 'COMPLETED',
            'created_at': '2024-01-01T12:00:00'
        }

        result = asset_transaction_dao.create_asset_transaction(sample_transaction_create)

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.asset_id == "BTC"
        assert result.transaction_type == AssetTransactionType.BUY
        assert result.quantity == Decimal("2.5")
        assert result.price == Decimal("50000.00")
        assert result.total_amount == Decimal("125000.00")
        assert result.order_id == "order-123"
        assert result.status == AssetTransactionStatus.COMPLETED

        # Verify database was called
        mock_db_connection.users_table.put_item.assert_called_once()
        call_args = mock_db_connection.users_table.put_item.call_args
        assert call_args[1]['Item']['transaction_type'] == 'BUY'
        assert call_args[1]['Item']['status'] == 'COMPLETED'

    def test_create_asset_transaction_sell_type(self, asset_transaction_dao, mock_db_connection):
        """Test asset transaction creation with SELL type"""
        transaction_create = AssetTransaction(
            username="testuser123",
            asset_id="ETH",
            transaction_type=AssetTransactionType.SELL,
            quantity=Decimal("10.0"),
            price=Decimal("3000.00"),
            total_amount=Decimal("30000.00")
        )

        mock_created_item = {
            'username': 'testuser123',
            'asset_id': 'ETH',
            'transaction_type': 'SELL',
            'quantity': '10.0',
            'price': '3000.00',
            'total_amount': '30000.00',
            'status': 'COMPLETED',
            'created_at': '2024-01-01T12:00:00'
        }
        mock_db_connection.users_table.put_item.return_value = mock_created_item

        result = asset_transaction_dao.create_asset_transaction(transaction_create)

        assert result.transaction_type == AssetTransactionType.SELL
        assert result.total_amount == Decimal("30000.00")

    def test_create_asset_transaction_no_order_id(self, asset_transaction_dao, mock_db_connection):
        """Test asset transaction creation without order_id"""
        transaction_create = AssetTransaction(
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("1.0"),
            price=Decimal("50000.00"),
            total_amount=Decimal("50000.00")
        )

        mock_created_item = {
            'username': 'testuser123',
            'asset_id': 'BTC',
            'transaction_type': 'BUY',
            'quantity': '1.0',
            'price': '50000.00',
            'total_amount': '50000.00',
            'status': 'COMPLETED',
            'created_at': '2024-01-01T12:00:00'
        }
        mock_db_connection.users_table.put_item.return_value = mock_created_item

        result = asset_transaction_dao.create_asset_transaction(transaction_create)

        assert result.order_id is None

    def test_create_asset_transaction_database_error(self, asset_transaction_dao, sample_transaction_create, mock_db_connection):
        """Test asset transaction creation with database error"""
        # Mock database error
        mock_db_connection.users_table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'PutItem'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            asset_transaction_dao.create_asset_transaction(sample_transaction_create)

    def test_get_asset_transaction_success(self, asset_transaction_dao, sample_asset_transaction, mock_db_connection):
        """Test successful asset transaction retrieval"""
        # Mock database response
        mock_item = {
            'Pk': 'TRANS#testuser123#BTC',
            'Sk': '2024-01-01T12:00:00Z',
            'username': 'testuser123',
            'asset_id': 'BTC',
            'transaction_type': 'BUY',
            'quantity': '2.5',
            'price': '50000.00',
            'total_amount': '125000.00',
            'order_id': 'order-123',
            'status': 'COMPLETED',
            'created_at': '2024-01-01T12:00:00'
        }
        mock_db_connection.users_table.get_item.return_value = {'Item': mock_item}

        result = asset_transaction_dao.get_asset_transaction('testuser123', 'BTC', '2024-01-01T12:00:00Z')

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.asset_id == "BTC"
        assert result.transaction_type == AssetTransactionType.BUY
        assert result.quantity == Decimal("2.5")
        assert result.price == Decimal("50000.00")
        assert result.total_amount == Decimal("125000.00")
        assert result.order_id == "order-123"
        assert result.status == AssetTransactionStatus.COMPLETED

        # Verify database was called
        mock_db_connection.users_table.get_item.assert_called_once_with(
            Key={'Pk': 'TRANS#testuser123#BTC', 'Sk': '2024-01-01T12:00:00Z'}
        )

    def test_get_asset_transaction_not_found(self, asset_transaction_dao, mock_db_connection):
        """Test asset transaction retrieval when not found"""
        # Mock empty database response
        mock_db_connection.users_table.get_item.return_value = {}

        # Should raise CNOPTransactionNotFoundException
        with pytest.raises(CNOPTransactionNotFoundException):
            asset_transaction_dao.get_asset_transaction('testuser123', 'BTC', '2024-01-01T12:00:00Z')

    def test_get_asset_transaction_database_error(self, asset_transaction_dao, mock_db_connection):
        """Test asset transaction retrieval with database error"""
        # Mock database error
        mock_db_connection.users_table.get_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'GetItem'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            asset_transaction_dao.get_asset_transaction('testuser123', 'BTC', '2024-01-01T12:00:00Z')

    def test_get_user_asset_transactions_success(self, asset_transaction_dao, mock_db_connection):
        """Test successful retrieval of user asset transactions"""
        # Mock database response
        mock_items = [
            {
                'Pk': 'TRANS#testuser123#BTC',
                'Sk': '2024-01-01T12:00:00Z',
                'username': 'testuser123',
                'asset_id': 'BTC',
                'transaction_type': 'BUY',
                'quantity': '2.5',
                'price': '50000.00',
                'total_amount': '125000.00',
                'order_id': 'order-123',
                'status': 'COMPLETED',
                'created_at': '2024-01-01T12:00:00'
            },
            {
                'Pk': 'TRANS#testuser123#BTC',
                'Sk': '2024-01-02T12:00:00Z',
                'username': 'testuser123',
                'asset_id': 'BTC',
                'transaction_type': 'SELL',
                'quantity': '1.0',
                'price': '55000.00',
                'total_amount': '55000.00',
                'status': 'COMPLETED',
                'created_at': '2024-01-02T12:00:00'
            }
        ]
        mock_db_connection.users_table.query.return_value = {'Items': mock_items}

        result = asset_transaction_dao.get_user_asset_transactions('testuser123', 'BTC')

        # Verify result
        assert len(result) == 2
        assert result[0].transaction_type == AssetTransactionType.BUY
        assert result[0].quantity == Decimal("2.5")
        assert result[1].transaction_type == AssetTransactionType.SELL
        assert result[1].quantity == Decimal("1.0")

        # Verify database was called with correct query
        mock_db_connection.users_table.query.assert_called_once()
        call_args = mock_db_connection.users_table.query.call_args
        assert 'KeyConditionExpression' in call_args[1]

    def test_get_user_asset_transactions_with_limit(self, asset_transaction_dao, mock_db_connection):
        """Test retrieval of user asset transactions with limit"""
        mock_items = [
            {
                'Pk': 'TRANS#testuser123#BTC',
                'Sk': '2024-01-01T12:00:00Z',
                'username': 'testuser123',
                'asset_id': 'BTC',
                'transaction_type': 'BUY',
                'quantity': '2.5',
                'price': '50000.00',
                'total_amount': '125000.00',
                'status': 'COMPLETED',
                'created_at': '2024-01-01T12:00:00'
            }
        ]
        mock_db_connection.users_table.query.return_value = {'Items': mock_items}

        result = asset_transaction_dao.get_user_asset_transactions('testuser123', 'BTC', limit=1)

        assert len(result) == 1
        mock_db_connection.users_table.query.assert_called_once()
        call_args = mock_db_connection.users_table.query.call_args
        assert call_args[1]['Limit'] == 1

    def test_get_user_asset_transactions_empty(self, asset_transaction_dao, mock_db_connection):
        """Test retrieval of user asset transactions when none exist"""
        # Mock empty database response
        mock_db_connection.users_table.query.return_value = {'Items': []}

        result = asset_transaction_dao.get_user_asset_transactions('testuser123', 'BTC')

        assert len(result) == 0

    def test_get_user_asset_transactions_database_error(self, asset_transaction_dao, mock_db_connection):
        """Test retrieval of user asset transactions with database error"""
        # Mock database error
        mock_db_connection.users_table.query.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'Query'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            asset_transaction_dao.get_user_asset_transactions('testuser123', 'BTC')

    def test_get_user_transactions_returns_empty(self, asset_transaction_dao, mock_db_connection):
        """Test get_user_transactions returns empty list (GSI not implemented)"""
        result = asset_transaction_dao.get_user_transactions('testuser123')

        assert result == []

    def test_get_user_transactions_with_limit_returns_empty(self, asset_transaction_dao, mock_db_connection):
        """Test get_user_transactions with limit returns empty list (GSI not implemented)"""
        result = asset_transaction_dao.get_user_transactions('testuser123', limit=10)

        assert result == []

    def test_delete_asset_transaction_success(self, asset_transaction_dao, mock_db_connection):
        """Test successful asset transaction deletion"""
        # Mock successful deletion with Attributes returned
        mock_db_connection.users_table.delete_item.return_value = {'Attributes': {'Pk': 'TRANS#testuser123#BTC', 'Sk': '2024-01-01T12:00:00Z'}}

        result = asset_transaction_dao.delete_asset_transaction('testuser123', 'BTC', '2024-01-01T12:00:00Z')

        # Verify result
        assert result is True

        # Verify database was called
        mock_db_connection.users_table.delete_item.assert_called_once_with(
            Key={'Pk': 'TRANS#testuser123#BTC', 'Sk': '2024-01-01T12:00:00Z'},
            ReturnValues='ALL_OLD'
        )

    def test_delete_asset_transaction_database_error(self, asset_transaction_dao, mock_db_connection):
        """Test asset transaction deletion with database error"""
        # Mock database error
        mock_db_connection.users_table.delete_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Database error'}},
            'DeleteItem'
        )

        with pytest.raises(CNOPDatabaseOperationException):
            asset_transaction_dao.delete_asset_transaction('testuser123', 'BTC', '2024-01-01T12:00:00Z')

    def test_asset_transaction_dao_initialization(self, mock_db_connection):
        """Test AssetTransactionDAO initialization"""
        dao = AssetTransactionDAO(mock_db_connection)

        assert dao.db == mock_db_connection
        assert dao.table == mock_db_connection.users_table

    def test_asset_transaction_dao_table_reference(self, mock_db_connection):
        """Test that AssetTransactionDAO uses correct table reference"""
        dao = AssetTransactionDAO(mock_db_connection)

        # Verify it uses users_table
        assert dao.table == mock_db_connection.users_table

    def test_total_amount_calculation(self, asset_transaction_dao, mock_db_connection):
        """Test that total_amount is calculated correctly during creation"""
        transaction_create = AssetTransaction(
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("3.0"),
            price=Decimal("40000.00"),
            total_amount=Decimal("120000.00"),
            order_id="order-456"
        )

        mock_created_item = {
            'username': 'testuser123',
            'asset_id': 'BTC',
            'transaction_type': 'BUY',
            'quantity': '3.0',
            'price': '40000.00',
            'total_amount': '120000.00',
            'order_id': 'order-456',
            'status': 'COMPLETED',
            'created_at': '2024-01-01T12:00:00'
        }
        mock_db_connection.users_table.put_item.return_value = mock_created_item

        result = asset_transaction_dao.create_asset_transaction(transaction_create)

        # Verify total_amount calculation: 3.0 * 40000.00 = 120000.00
        assert result.total_amount == Decimal("120000.00")

        # Verify the calculation was done correctly in the put_item call
        call_args = mock_db_connection.users_table.put_item.call_args
        # Check that total_amount is calculated correctly (3.0 * 40000.00 = 120000.00)
        assert call_args[1]['Item']['total_amount'] == '120000.000'  # Decimal precision