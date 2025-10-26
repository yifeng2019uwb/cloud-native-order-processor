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
from tests.utils.dependency_constants import (
    MODEL_SAVE, MODEL_GET, MODEL_QUERY, MODEL_DELETE, DOES_NOT_EXIST,
    ASSET_TRANSACTION_DAO_CREATE_ASSET_TRANSACTION, ASSET_TRANSACTION_DAO_GET_ASSET_TRANSACTION,
    ASSET_TRANSACTION_DAO_GET_USER_ASSET_TRANSACTIONS, ASSET_TRANSACTION_DAO_GET_USER_TRANSACTIONS,
    ASSET_TRANSACTION_DAO_DELETE_ASSET_TRANSACTION, ASSET_TRANSACTION_ITEM_FROM_ASSET_TRANSACTION
)


# =============================================================================
# LOCAL TEST VARIABLES - Avoid hardcoded values in tests
# =============================================================================

# Test user data
TEST_USERNAME = "testuser123"
TEST_EMAIL = "test@example.com"

# Test asset data
TEST_ASSET_ID_BTC = "BTC"
TEST_ASSET_ID_ETH = "ETH"

# Test financial data
TEST_BTC_PRICE_50000 = Decimal("50000.00")
TEST_BTC_QUANTITY_2_5 = Decimal("2.5")
TEST_TRANSACTION_AMOUNT_125000 = Decimal("125000.00")  # 2.5 * 50000
TEST_TRANSACTION_AMOUNT_30000 = Decimal("30000.00")  # 10.0 * 3000
TEST_DEPOSIT_AMOUNT_50 = Decimal("50.00")
TEST_BALANCE_AMOUNT_100 = Decimal("100.00")

# Test order data
TEST_ORDER_ID = "order-123"
TEST_REFERENCE_ID = "test_ref_123"

# Test transaction status and type
TEST_TRANSACTION_TYPE_BUY = "BUY"
TEST_TRANSACTION_TYPE_SELL = "SELL"
TEST_TRANSACTION_STATUS_COMPLETED = "COMPLETED"
TEST_TRANSACTION_STATUS_PENDING = "PENDING"

# Test string values for mock objects
TEST_QUANTITY_STRING_2_5 = "2.5"
TEST_QUANTITY_STRING_1_0 = "1.0"
TEST_PRICE_STRING_50000 = "50000.00"
TEST_PRICE_STRING_55000 = "55000.00"
TEST_AMOUNT_STRING_125000 = "125000.00"
TEST_AMOUNT_STRING_55000 = "55000.00"

TEST_CURRENT_TIMESTAMP = datetime.now(timezone.utc)
TEST_FIXED_TIMESTAMP_1 = datetime(2024, 1, 1, 12, 0, 0)
TEST_FIXED_TIMESTAMP_2 = datetime(2024, 1, 2, 12, 0, 0)

# Test primary keys - use entity methods directly in tests when needed
# Example: AssetTransaction.build_pk(TEST_USERNAME, TEST_ASSET_ID_BTC)


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
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            transaction_type=AssetTransactionType.BUY,
            quantity=TEST_BTC_QUANTITY_2_5,
            price=TEST_BTC_PRICE_50000,
            total_amount=TEST_TRANSACTION_AMOUNT_125000,
            order_id=TEST_ORDER_ID
        )

    @pytest.fixture
    def sample_asset_transaction(self):
        """Sample asset transaction for testing"""
        return AssetTransaction(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            transaction_type=AssetTransactionType.BUY,
            quantity=TEST_BTC_QUANTITY_2_5,
            price=TEST_BTC_PRICE_50000,
            total_amount=TEST_TRANSACTION_AMOUNT_125000,
            order_id=TEST_ORDER_ID,
            status=AssetTransactionStatus.COMPLETED,
            created_at=datetime.now(timezone.utc)
        )

    @patch.object(AssetTransactionItem, MODEL_SAVE)
    @patch.object(AssetTransactionItem, ASSET_TRANSACTION_ITEM_FROM_ASSET_TRANSACTION)
    def test_create_asset_transaction_success(self, mock_from_asset_transaction, mock_save, sample_transaction_create):
        """Test successful asset transaction creation"""
        # Mock PynamoDB save operation
        mock_save.return_value = None

        # Mock the from_asset_transaction method to return an item with datetime created_at
        mock_item = AssetTransactionItem(
            Pk=AssetTransaction.build_pk(TEST_USERNAME, TEST_ASSET_ID_BTC),
            Sk=datetime.now(timezone.utc).isoformat(),
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            transaction_type=TEST_TRANSACTION_TYPE_BUY,
            quantity=TEST_QUANTITY_STRING_2_5,
            price=TEST_PRICE_STRING_50000,
            total_amount=str(TEST_TRANSACTION_AMOUNT_125000),
            order_id=TEST_ORDER_ID,
            status=TEST_TRANSACTION_STATUS_COMPLETED,
            created_at=datetime.now(timezone.utc)  # Datetime object as expected by source code
        )
        mock_from_asset_transaction.return_value = mock_item

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.create_asset_transaction(sample_transaction_create)

        # Verify result
        assert result is not None
        assert result.username == TEST_USERNAME
        assert result.asset_id == TEST_ASSET_ID_BTC
        assert result.transaction_type == AssetTransactionType.BUY
        assert result.quantity == TEST_BTC_QUANTITY_2_5
        assert result.price == TEST_BTC_PRICE_50000
        assert result.total_amount == TEST_TRANSACTION_AMOUNT_125000
        assert result.order_id == TEST_ORDER_ID
        assert result.status == AssetTransactionStatus.COMPLETED

        # Verify PynamoDB save was called
        mock_save.assert_called_once()

    @patch.object(AssetTransactionItem, MODEL_SAVE)
    @patch.object(AssetTransactionItem, ASSET_TRANSACTION_ITEM_FROM_ASSET_TRANSACTION)
    def test_create_asset_transaction_sell_type(self, mock_from_asset_transaction, mock_save, sample_transaction_create):
        """Test asset transaction creation with SELL type"""
        # Local test variables for this specific test
        test_username = TEST_USERNAME
        test_asset_id = TEST_ASSET_ID_ETH
        test_quantity = Decimal("10.0")
        test_price = Decimal("3000.00")
        test_total_amount = Decimal("30000.00")

        transaction_create = AssetTransaction(
            username=test_username,
            asset_id=test_asset_id,
            transaction_type=AssetTransactionType.SELL,
            quantity=test_quantity,
            price=test_price,
            total_amount=test_total_amount
        )

        # Mock PynamoDB save operation
        mock_save.return_value = None

        # Mock the from_asset_transaction method to return an item with datetime created_at
        mock_item = AssetTransactionItem(
            Pk=AssetTransaction.build_pk(TEST_USERNAME, TEST_ASSET_ID_ETH),
            Sk=datetime.now(timezone.utc).isoformat(),
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_ETH,
            transaction_type=TEST_TRANSACTION_TYPE_SELL,
            quantity=TEST_QUANTITY_STRING_1_0,
            price=TEST_PRICE_STRING_50000,
            total_amount=str(TEST_TRANSACTION_AMOUNT_30000),
            order_id=None,
            status=TEST_TRANSACTION_STATUS_COMPLETED,
            created_at=datetime.now(timezone.utc)  # Datetime object as expected by source code
        )
        mock_from_asset_transaction.return_value = mock_item

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.create_asset_transaction(transaction_create)

        assert result.transaction_type == AssetTransactionType.SELL
        assert result.total_amount == test_total_amount

    @patch.object(AssetTransactionItem, MODEL_SAVE)
    @patch.object(AssetTransactionItem, ASSET_TRANSACTION_ITEM_FROM_ASSET_TRANSACTION)
    def test_create_asset_transaction_no_order_id(self, mock_from_asset_transaction, mock_save, sample_transaction_create):
        """Test asset transaction creation without order_id"""
        # Local test variables for this specific test
        test_username = TEST_USERNAME
        test_asset_id = TEST_ASSET_ID_BTC
        test_quantity = Decimal("1.0")
        test_price = TEST_BTC_PRICE_50000
        test_total_amount = Decimal("50000.00")

        transaction_create = AssetTransaction(
            username=test_username,
            asset_id=test_asset_id,
            transaction_type=AssetTransactionType.BUY,
            quantity=test_quantity,
            price=test_price,
            total_amount=test_total_amount
        )

        # Mock PynamoDB save operation
        mock_save.return_value = None

        # Mock the from_asset_transaction method to return an item with datetime created_at
        mock_item = AssetTransactionItem(
            Pk=AssetTransaction.build_pk(TEST_USERNAME, TEST_ASSET_ID_BTC),
            Sk=datetime.now(timezone.utc).isoformat(),
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            transaction_type=TEST_TRANSACTION_TYPE_BUY,
            quantity=TEST_QUANTITY_STRING_1_0,
            price=TEST_PRICE_STRING_50000,
            total_amount=str(Decimal("50000.00")),
            order_id=None,  # No order_id as expected
            status=TEST_TRANSACTION_STATUS_COMPLETED,
            created_at=datetime.now(timezone.utc)  # Datetime object as expected by source code
        )
        mock_from_asset_transaction.return_value = mock_item

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.create_asset_transaction(transaction_create)

        assert result.order_id is None

    @patch.object(AssetTransactionItem, MODEL_SAVE)
    def test_create_asset_transaction_database_error(self, mock_save, sample_transaction_create):
        """Test asset transaction creation with database error"""
        # Mock database error
        mock_save.side_effect = Exception("Database connection failed")

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        with pytest.raises(CNOPDatabaseOperationException):
            asset_transaction_dao.create_asset_transaction(sample_transaction_create)

    @patch.object(AssetTransactionItem, MODEL_GET)
    def test_get_asset_transaction_success(self, mock_get, sample_asset_transaction):
        """Test successful asset transaction retrieval"""
        # Local test variables for this specific test
        test_username = TEST_USERNAME
        test_asset_id = TEST_ASSET_ID_BTC
        test_timestamp = TEST_CURRENT_TIMESTAMP
        test_quantity = TEST_BTC_QUANTITY_2_5
        test_price = TEST_BTC_PRICE_50000
        test_total_amount = TEST_TRANSACTION_AMOUNT_125000
        test_order_id = TEST_ORDER_ID
        test_transaction_type = AssetTransactionType.BUY
        test_status = AssetTransactionStatus.COMPLETED
        test_created_at = TEST_FIXED_TIMESTAMP_1

        # Expected values for assertions
        expected_username = test_username
        expected_asset_id = test_asset_id
        expected_quantity = test_quantity
        expected_price = test_price
        expected_total_amount = test_total_amount
        expected_order_id = test_order_id
        expected_transaction_type = test_transaction_type
        expected_status = test_status

        # Mock PynamoDB model instance
        mock_transaction_item = AssetTransactionItem()
        mock_transaction_item.Pk = AssetTransaction.build_pk(test_username, test_asset_id)
        mock_transaction_item.Sk = test_timestamp
        mock_transaction_item.username = test_username
        mock_transaction_item.asset_id = test_asset_id
        mock_transaction_item.transaction_type = test_transaction_type.value
        mock_transaction_item.quantity = str(test_quantity)
        mock_transaction_item.price = str(test_price)
        mock_transaction_item.total_amount = str(test_total_amount)
        mock_transaction_item.order_id = test_order_id
        mock_transaction_item.status = test_status.value
        mock_transaction_item.created_at = test_created_at
        mock_get.return_value = mock_transaction_item

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.get_asset_transaction(test_username, test_asset_id, test_timestamp)

        # Verify result using expected variables
        assert result is not None
        assert result.username == expected_username
        assert result.asset_id == expected_asset_id
        assert result.transaction_type == expected_transaction_type
        assert result.quantity == expected_quantity
        assert result.price == expected_price
        assert result.total_amount == expected_total_amount
        assert result.order_id == expected_order_id
        assert result.status == expected_status

        # Verify PynamoDB get was called
        mock_get.assert_called_once()

    @patch.object(AssetTransactionItem, MODEL_GET)
    def test_get_asset_transaction_not_found(self, mock_get):
        """Test asset transaction retrieval when not found"""
        # Mock DoesNotExist exception
        mock_get.side_effect = AssetTransactionItem.DoesNotExist()

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        # Should raise CNOPTransactionNotFoundException
        with pytest.raises(CNOPTransactionNotFoundException):
            asset_transaction_dao.get_asset_transaction(TEST_USERNAME, TEST_ASSET_ID_BTC, '2024-01-01T12:00:00Z')

    @patch.object(AssetTransactionItem, MODEL_GET)
    def test_get_asset_transaction_database_error(self, mock_get):
        """Test asset transaction retrieval with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        with pytest.raises(CNOPDatabaseOperationException):
            asset_transaction_dao.get_asset_transaction(TEST_USERNAME, TEST_ASSET_ID_BTC, '2024-01-01T12:00:00Z')

    @patch.object(AssetTransactionItem, MODEL_QUERY)
    def test_get_user_asset_transactions_success(self, mock_query):
        """Test successful retrieval of user asset transactions"""
        # Mock PynamoDB query result
        mock_transaction_item1 = AssetTransactionItem()
        mock_transaction_item1.Pk = AssetTransaction.build_pk(TEST_USERNAME, TEST_ASSET_ID_BTC)
        mock_transaction_item1.Sk = TEST_CURRENT_TIMESTAMP
        mock_transaction_item1.username = TEST_USERNAME
        mock_transaction_item1.asset_id = TEST_ASSET_ID_BTC
        mock_transaction_item1.transaction_type = TEST_TRANSACTION_TYPE_BUY
        mock_transaction_item1.quantity = TEST_QUANTITY_STRING_2_5
        mock_transaction_item1.price = TEST_PRICE_STRING_50000
        mock_transaction_item1.total_amount = TEST_AMOUNT_STRING_125000
        mock_transaction_item1.order_id = TEST_ORDER_ID
        mock_transaction_item1.status = TEST_TRANSACTION_STATUS_COMPLETED
        mock_transaction_item1.created_at = TEST_FIXED_TIMESTAMP_1

        mock_transaction_item2 = AssetTransactionItem()
        mock_transaction_item2.Pk = AssetTransaction.build_pk(TEST_USERNAME, TEST_ASSET_ID_BTC)
        mock_transaction_item2.Sk = TEST_CURRENT_TIMESTAMP
        mock_transaction_item2.username = TEST_USERNAME
        mock_transaction_item2.asset_id = TEST_ASSET_ID_BTC
        mock_transaction_item2.transaction_type = TEST_TRANSACTION_TYPE_SELL
        mock_transaction_item2.quantity = TEST_QUANTITY_STRING_1_0
        mock_transaction_item2.price = TEST_PRICE_STRING_55000
        mock_transaction_item2.total_amount = TEST_AMOUNT_STRING_55000
        mock_transaction_item2.order_id = None
        mock_transaction_item2.status = TEST_TRANSACTION_STATUS_COMPLETED
        mock_transaction_item2.created_at = TEST_FIXED_TIMESTAMP_2

        mock_query.return_value = [mock_transaction_item1, mock_transaction_item2]

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.get_user_asset_transactions(TEST_USERNAME, TEST_ASSET_ID_BTC)

        # Verify result
        assert len(result) == 2
        assert result[0].transaction_type == AssetTransactionType.BUY
        assert result[0].quantity == Decimal("2.5")
        assert result[1].transaction_type == AssetTransactionType.SELL
        assert result[1].quantity == Decimal("1.0")

        # Verify PynamoDB query was called
        mock_query.assert_called_once()

    @patch.object(AssetTransactionItem, MODEL_QUERY)
    def test_get_user_asset_transactions_with_limit(self, mock_query):
        """Test retrieval of user asset transactions with limit"""
        # Mock PynamoDB query result
        mock_transaction_item = AssetTransactionItem()
        mock_transaction_item.Pk = AssetTransaction.build_pk(TEST_USERNAME, TEST_ASSET_ID_BTC)
        mock_transaction_item.Sk = TEST_CURRENT_TIMESTAMP
        mock_transaction_item.username = TEST_USERNAME
        mock_transaction_item.asset_id = TEST_ASSET_ID_BTC
        mock_transaction_item.transaction_type = TEST_TRANSACTION_TYPE_BUY
        mock_transaction_item.quantity = TEST_QUANTITY_STRING_2_5
        mock_transaction_item.price = TEST_PRICE_STRING_50000
        mock_transaction_item.total_amount = TEST_AMOUNT_STRING_125000
        mock_transaction_item.order_id = TEST_ORDER_ID
        mock_transaction_item.status = TEST_TRANSACTION_STATUS_COMPLETED
        mock_transaction_item.created_at = TEST_FIXED_TIMESTAMP_1

        mock_query.return_value = [mock_transaction_item]

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.get_user_asset_transactions(TEST_USERNAME, TEST_ASSET_ID_BTC, limit=1)

        assert len(result) == 1
        mock_query.assert_called_once()

    @patch.object(AssetTransactionItem, MODEL_QUERY)
    def test_get_user_asset_transactions_empty(self, mock_query):
        """Test retrieval of user asset transactions when none exist"""
        # Mock empty query result
        mock_query.return_value = []

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.get_user_asset_transactions(TEST_USERNAME, TEST_ASSET_ID_BTC)

        assert len(result) == 0

    @patch.object(AssetTransactionItem, MODEL_QUERY)
    def test_get_user_asset_transactions_database_error(self, mock_query):
        """Test retrieval of user asset transactions with database error"""
        # Mock database error
        mock_query.side_effect = Exception("Database connection failed")

        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        with pytest.raises(CNOPDatabaseOperationException):
            asset_transaction_dao.get_user_asset_transactions(TEST_USERNAME, TEST_ASSET_ID_BTC)

    def test_get_user_transactions_returns_empty(self):
        """Test get_user_transactions returns empty list (GSI not implemented)"""
        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.get_user_transactions(TEST_USERNAME)

        assert result == []

    def test_get_user_transactions_with_limit_returns_empty(self):
        """Test get_user_transactions with limit returns empty list (GSI not implemented)"""
        # Create DAO instance (PynamoDB doesn't need db_connection)
        asset_transaction_dao = AssetTransactionDAO()

        result = asset_transaction_dao.get_user_transactions(TEST_USERNAME, limit=10)

        assert result == []



    @patch.object(AssetTransactionItem, MODEL_SAVE)
    def test_total_amount_calculation(self, mock_save, sample_transaction_create):
        """Test that total_amount is calculated correctly during creation"""
        # Local test variables for this specific test
        test_username = TEST_USERNAME
        test_asset_id = TEST_ASSET_ID_BTC
        test_quantity = Decimal("3.0")
        test_price = Decimal("40000.00")
        test_total_amount = Decimal("120000.00")
        test_order_id = "order-456"

        transaction_create = AssetTransaction(
            username=test_username,
            asset_id=test_asset_id,
            transaction_type=AssetTransactionType.BUY,
            quantity=test_quantity,
            price=test_price,
            total_amount=test_total_amount,
            order_id=test_order_id
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