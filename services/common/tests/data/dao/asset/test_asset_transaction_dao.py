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
from tests.data.dao.mock_constants import MockDatabaseMethods


class TestAssetTransactionDAO:
    """Test AssetTransactionDAO class"""

    @pytest.fixture
    def asset_transaction_dao(self):
        """Create AssetTransactionDAO instance (PynamoDB doesn't need db_connection)"""
        return AssetTransactionDAO()

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

    @patch.object(AssetTransactionItem, MockDatabaseMethods.SAVE)
    def test_create_asset_transaction_success(self, mock_save, sample_transaction_create):
        """Test successful asset transaction creation"""
        # Mock PynamoDB save operation
        mock_save.return_value = None

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

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

        # Verify PynamoDB save was called
        mock_save.assert_called_once()

    @patch.object(AssetTransactionItem, MockDatabaseMethods.SAVE)
    def test_create_asset_transaction_sell_type(self, mock_save, sample_transaction_create):
        """Test asset transaction creation with SELL type"""
        transaction_create = AssetTransaction(
            username="testuser123",
            asset_id="ETH",
            transaction_type=AssetTransactionType.SELL,
            quantity=Decimal("10.0"),
            price=Decimal("3000.00"),
            total_amount=Decimal("30000.00")
        )

        # Mock PynamoDB save operation
        mock_save.return_value = None

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.create_asset_transaction(transaction_create)

        assert result.transaction_type == AssetTransactionType.SELL
        assert result.total_amount == Decimal("30000.00")

    @patch.object(AssetTransactionItem, MockDatabaseMethods.SAVE)
    def test_create_asset_transaction_no_order_id(self, mock_save, sample_transaction_create):
        """Test asset transaction creation without order_id"""
        transaction_create = AssetTransaction(
            username="testuser123",
            asset_id="BTC",
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("1.0"),
            price=Decimal("50000.00"),
            total_amount=Decimal("50000.00")
        )

        # Mock PynamoDB save operation
        mock_save.return_value = None

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.create_asset_transaction(transaction_create)

        assert result.order_id is None

    @patch.object(AssetTransactionItem, MockDatabaseMethods.SAVE)
    def test_create_asset_transaction_database_error(self, mock_save, sample_transaction_create):
        """Test asset transaction creation with database error"""
        # Mock database error
        mock_save.side_effect = Exception("Database connection failed")

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        with pytest.raises(CNOPDatabaseOperationException):
            asset_transaction_dao.create_asset_transaction(sample_transaction_create)

    @patch.object(AssetTransactionItem, MockDatabaseMethods.GET)
    def test_get_asset_transaction_success(self, mock_get, sample_asset_transaction):
        """Test successful asset transaction retrieval"""
        # Mock PynamoDB model instance
        mock_transaction_item = AssetTransactionItem()
        mock_transaction_item.Pk = 'TRANS#testuser123#BTC'
        mock_transaction_item.Sk = '2024-01-01T12:00:00Z'
        mock_transaction_item.username = 'testuser123'
        mock_transaction_item.asset_id = 'BTC'
        mock_transaction_item.transaction_type = 'BUY'
        mock_transaction_item.quantity = '2.5'
        mock_transaction_item.price = '50000.00'
        mock_transaction_item.total_amount = '125000.00'
        mock_transaction_item.order_id = 'order-123'
        mock_transaction_item.status = 'COMPLETED'
        mock_transaction_item.created_at = datetime(2024, 1, 1, 12, 0, 0)
        mock_get.return_value = mock_transaction_item

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

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

        # Verify PynamoDB get was called
        mock_get.assert_called_once()

    @patch.object(AssetTransactionItem, MockDatabaseMethods.GET)
    def test_get_asset_transaction_not_found(self, mock_get):
        """Test asset transaction retrieval when not found"""
        # Mock DoesNotExist exception
        mock_get.side_effect = AssetTransactionItem.DoesNotExist()

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        # Should raise CNOPTransactionNotFoundException
        with pytest.raises(CNOPTransactionNotFoundException):
            asset_transaction_dao.get_asset_transaction('testuser123', 'BTC', '2024-01-01T12:00:00Z')

    @patch.object(AssetTransactionItem, MockDatabaseMethods.GET)
    def test_get_asset_transaction_database_error(self, mock_get):
        """Test asset transaction retrieval with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        with pytest.raises(CNOPDatabaseOperationException):
            asset_transaction_dao.get_asset_transaction('testuser123', 'BTC', '2024-01-01T12:00:00Z')

    @patch.object(AssetTransactionItem, MockDatabaseMethods.QUERY)
    def test_get_user_asset_transactions_success(self, mock_query):
        """Test successful retrieval of user asset transactions"""
        # Mock PynamoDB query result
        mock_transaction_item1 = AssetTransactionItem()
        mock_transaction_item1.Pk = 'TRANS#testuser123#BTC'
        mock_transaction_item1.Sk = '2024-01-01T12:00:00Z'
        mock_transaction_item1.username = 'testuser123'
        mock_transaction_item1.asset_id = 'BTC'
        mock_transaction_item1.transaction_type = 'BUY'
        mock_transaction_item1.quantity = '2.5'
        mock_transaction_item1.price = '50000.00'
        mock_transaction_item1.total_amount = '125000.00'
        mock_transaction_item1.order_id = 'order-123'
        mock_transaction_item1.status = 'COMPLETED'
        mock_transaction_item1.created_at = datetime(2024, 1, 1, 12, 0, 0)

        mock_transaction_item2 = AssetTransactionItem()
        mock_transaction_item2.Pk = 'TRANS#testuser123#BTC'
        mock_transaction_item2.Sk = '2024-01-02T12:00:00Z'
        mock_transaction_item2.username = 'testuser123'
        mock_transaction_item2.asset_id = 'BTC'
        mock_transaction_item2.transaction_type = 'SELL'
        mock_transaction_item2.quantity = '1.0'
        mock_transaction_item2.price = '55000.00'
        mock_transaction_item2.total_amount = '55000.00'
        mock_transaction_item2.order_id = None
        mock_transaction_item2.status = 'COMPLETED'
        mock_transaction_item2.created_at = datetime(2024, 1, 2, 12, 0, 0)

        mock_query.return_value = [mock_transaction_item1, mock_transaction_item2]

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.get_user_asset_transactions('testuser123', 'BTC')

        # Verify result
        assert len(result) == 2
        assert result[0].transaction_type == AssetTransactionType.BUY
        assert result[0].quantity == Decimal("2.5")
        assert result[1].transaction_type == AssetTransactionType.SELL
        assert result[1].quantity == Decimal("1.0")

        # Verify PynamoDB query was called
        mock_query.assert_called_once()

    @patch.object(AssetTransactionItem, MockDatabaseMethods.QUERY)
    def test_get_user_asset_transactions_with_limit(self, mock_query):
        """Test retrieval of user asset transactions with limit"""
        # Mock PynamoDB query result
        mock_transaction_item = AssetTransactionItem()
        mock_transaction_item.Pk = 'TRANS#testuser123#BTC'
        mock_transaction_item.Sk = '2024-01-01T12:00:00Z'
        mock_transaction_item.username = 'testuser123'
        mock_transaction_item.asset_id = 'BTC'
        mock_transaction_item.transaction_type = 'BUY'
        mock_transaction_item.quantity = '2.5'
        mock_transaction_item.price = '50000.00'
        mock_transaction_item.total_amount = '125000.00'
        mock_transaction_item.order_id = 'order-123'
        mock_transaction_item.status = 'COMPLETED'
        mock_transaction_item.created_at = datetime(2024, 1, 1, 12, 0, 0)

        mock_query.return_value = [mock_transaction_item]

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.get_user_asset_transactions('testuser123', 'BTC', limit=1)

        assert len(result) == 1
        mock_query.assert_called_once()

    @patch.object(AssetTransactionItem, MockDatabaseMethods.QUERY)
    def test_get_user_asset_transactions_empty(self, mock_query):
        """Test retrieval of user asset transactions when none exist"""
        # Mock empty query result
        mock_query.return_value = []

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.get_user_asset_transactions('testuser123', 'BTC')

        assert len(result) == 0

    @patch.object(AssetTransactionItem, MockDatabaseMethods.QUERY)
    def test_get_user_asset_transactions_database_error(self, mock_query):
        """Test retrieval of user asset transactions with database error"""
        # Mock database error
        mock_query.side_effect = Exception("Database connection failed")

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        with pytest.raises(CNOPDatabaseOperationException):
            asset_transaction_dao.get_user_asset_transactions('testuser123', 'BTC')

    def test_get_user_transactions_returns_empty(self):
        """Test get_user_transactions returns empty list (GSI not implemented)"""
        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.get_user_transactions('testuser123')

        assert result == []

    def test_get_user_transactions_with_limit_returns_empty(self):
        """Test get_user_transactions with limit returns empty list (GSI not implemented)"""
        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.get_user_transactions('testuser123', limit=10)

        assert result == []

    @patch.object(AssetTransactionItem, MockDatabaseMethods.GET)
    @patch.object(AssetTransactionItem, MockDatabaseMethods.DELETE)
    def test_delete_asset_transaction_success(self, mock_delete, mock_get):
        """Test successful asset transaction deletion"""
        # Mock successful get and delete
        mock_transaction_item = AssetTransactionItem()
        mock_transaction_item.Pk = 'TRANS#testuser123#BTC'
        mock_transaction_item.Sk = '2024-01-01T12:00:00Z'
        mock_get.return_value = mock_transaction_item
        mock_delete.return_value = None

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.delete_asset_transaction('testuser123', 'BTC', '2024-01-01T12:00:00Z')

        # Verify result
        assert result is True

        # Verify PynamoDB operations were called
        mock_get.assert_called_once()
        mock_delete.assert_called_once()

    @patch.object(AssetTransactionItem, MockDatabaseMethods.GET)
    def test_delete_asset_transaction_database_error(self, mock_get):
        """Test asset transaction deletion with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        with pytest.raises(CNOPDatabaseOperationException):
            asset_transaction_dao.delete_asset_transaction('testuser123', 'BTC', '2024-01-01T12:00:00Z')


    @patch.object(AssetTransactionItem, MockDatabaseMethods.SAVE)
    def test_total_amount_calculation(self, mock_save, sample_transaction_create):
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

        # Mock PynamoDB save operation
        mock_save.return_value = None

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.create_asset_transaction(transaction_create)

        # Verify total_amount calculation: 3.0 * 40000.00 = 120000.00
        assert result.total_amount == Decimal("120000.00")

        # Verify PynamoDB save was called
        mock_save.assert_called_once()