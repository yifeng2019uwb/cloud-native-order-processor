"""
Tests for Asset Balance DAO
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from src.data.dao.asset.asset_balance_dao import AssetBalanceDAO
from src.data.entities.asset.asset_balance import AssetBalance, AssetBalanceItem
from src.data.entities.entity_constants import AssetBalanceFields
from src.data.exceptions import CNOPDatabaseOperationException
from src.exceptions.shared_exceptions import CNOPAssetBalanceNotFoundException
from tests.utils.dependency_constants import (
    MODEL_SAVE, MODEL_GET, MODEL_QUERY, MODEL_DELETE, DOES_NOT_EXIST,
    ASSET_BALANCE_DAO_UPSERT_ASSET_BALANCE, ASSET_BALANCE_DAO_GET_ASSET_BALANCE,
    ASSET_BALANCE_DAO_GET_ALL_ASSET_BALANCES, ASSET_BALANCE_DAO_DELETE_ASSET_BALANCE
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
TEST_BALANCE_AMOUNT_100 = Decimal("100.00")
TEST_QUANTITY_1_0 = Decimal("1.0")
TEST_QUANTITY_2_5 = Decimal("2.5")
TEST_QUANTITY_5_0 = Decimal("5.0")
TEST_QUANTITY_5_5 = Decimal("5.5")
TEST_QUANTITY_10_5 = Decimal("10.5")
TEST_QUANTITY_8_5 = Decimal("8.5")
TEST_QUANTITY_2_0 = Decimal("2.0")
TEST_QUANTITY_25_0 = Decimal("25.0")
TEST_QUANTITY_0_0 = Decimal("0.0")
TEST_QUANTITY_NEGATIVE_2_0 = Decimal("-2.0")

# Test timestamps
TEST_CURRENT_TIMESTAMP = datetime.now(timezone.utc)
TEST_FIXED_TIMESTAMP = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

# Test primary keys - use entity methods directly in tests when needed
# Example: AssetBalance.build_pk(TEST_USERNAME, TEST_ASSET_ID_BTC)


class TestAssetBalanceDAO:
    """Test AssetBalanceDAO class"""

    @pytest.fixture
    def asset_balance_dao(self):
        """Create AssetBalanceDAO instance (PynamoDB doesn't need db_connection)"""
        return AssetBalanceDAO()

    @pytest.fixture
    def sample_asset_balance(self):
        """Sample asset balance for testing"""
        return AssetBalance(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_QUANTITY_1_0,
            created_at=TEST_CURRENT_TIMESTAMP,
            updated_at=TEST_CURRENT_TIMESTAMP
        )

    # ==================== UPSERT ASSET BALANCE TESTS ====================

    @patch.object(AssetBalanceItem, MODEL_GET)
    @patch.object(AssetBalanceItem, MODEL_SAVE)
    def test_upsert_asset_balance_update_existing(self, mock_save, mock_get, asset_balance_dao, sample_asset_balance):
        """Test successful asset balance update (existing item)"""
        # Mock existing balance item
        existing_balance_item = AssetBalanceItem(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_QUANTITY_5_0,
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.created_at
        )
        mock_get.return_value = existing_balance_item
        mock_save.return_value = None

        result = asset_balance_dao.upsert_asset_balance(TEST_USERNAME, TEST_ASSET_ID_BTC, TEST_QUANTITY_5_5)

        # Verify result
        assert result is not None
        assert result.username == TEST_USERNAME
        assert result.asset_id == TEST_ASSET_ID_BTC
        assert result.quantity == TEST_QUANTITY_10_5  # 5.0 + 5.5

        # Verify get was called with correct parameters
        mock_get.assert_called_once_with(TEST_USERNAME, f"{AssetBalanceFields.SK_PREFIX}{TEST_ASSET_ID_BTC}")
        # Verify save was called
        assert mock_save.called

    @patch.object(AssetBalanceItem, MODEL_GET)
    @patch.object(AssetBalanceItem, MODEL_SAVE)
    def test_upsert_asset_balance_create_new(self, mock_save, mock_get, asset_balance_dao):
        """Test successful asset balance creation (new item)"""
        # Mock get to raise DoesNotExist (no existing balance)
        mock_get.side_effect = getattr(AssetBalanceItem, DOES_NOT_EXIST)()
        mock_save.return_value = None

        result = asset_balance_dao.upsert_asset_balance(TEST_USERNAME, TEST_ASSET_ID_ETH, TEST_QUANTITY_2_0)

        # Verify result
        assert result is not None
        assert result.username == TEST_USERNAME
        assert result.asset_id == TEST_ASSET_ID_ETH
        assert result.quantity == TEST_QUANTITY_2_0

        # Verify get was called with correct parameters
        mock_get.assert_called_once_with(TEST_USERNAME, f"{AssetBalanceFields.SK_PREFIX}{TEST_ASSET_ID_ETH}")
        # Verify save was called
        assert mock_save.called

    @patch.object(AssetBalanceItem, MODEL_GET)
    @patch.object(AssetBalanceItem, MODEL_SAVE)
    def test_upsert_asset_balance_zero_quantity(self, mock_save, mock_get, asset_balance_dao, sample_asset_balance):
        """Test asset balance upsert with zero quantity"""
        # Mock existing balance item
        existing_balance_item = AssetBalanceItem(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_QUANTITY_10_5,
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.created_at
        )
        mock_get.return_value = existing_balance_item
        mock_save.return_value = None

        result = asset_balance_dao.upsert_asset_balance(TEST_USERNAME, TEST_ASSET_ID_BTC, TEST_QUANTITY_0_0)

        # Verify result (should remain the same)
        assert result is not None
        assert result.username == TEST_USERNAME
        assert result.asset_id == TEST_ASSET_ID_BTC
        assert result.quantity == TEST_QUANTITY_10_5  # 10.5 + 0.0

        # Verify get was called
        mock_get.assert_called_once_with(TEST_USERNAME, f"{AssetBalanceFields.SK_PREFIX}{TEST_ASSET_ID_BTC}")
        # Verify save was called
        assert mock_save.called

    @patch.object(AssetBalanceItem, MODEL_GET)
    @patch.object(AssetBalanceItem, MODEL_SAVE)
    def test_upsert_asset_balance_negative_quantity(self, mock_save, mock_get, asset_balance_dao, sample_asset_balance):
        """Test asset balance upsert with negative quantity"""
        # Mock existing balance item
        existing_balance_item = AssetBalanceItem(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_QUANTITY_10_5,
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.created_at
        )
        mock_get.return_value = existing_balance_item
        mock_save.return_value = None

        result = asset_balance_dao.upsert_asset_balance(TEST_USERNAME, TEST_ASSET_ID_BTC, TEST_QUANTITY_NEGATIVE_2_0)

        # Verify result
        assert result is not None
        assert result.username == TEST_USERNAME
        assert result.asset_id == TEST_ASSET_ID_BTC
        assert result.quantity == TEST_QUANTITY_8_5  # 10.5 + (-2.0)

        # Verify get was called
        mock_get.assert_called_once_with(TEST_USERNAME, f"{AssetBalanceFields.SK_PREFIX}{TEST_ASSET_ID_BTC}")
        # Verify save was called
        assert mock_save.called

    # ==================== GET ASSET BALANCE TESTS ====================

    @patch.object(AssetBalanceItem, MODEL_GET)
    def test_get_asset_balance_success(self, mock_get, asset_balance_dao, sample_asset_balance):
        """Test successful asset balance retrieval"""
        # Mock AssetBalanceItem.get to return a real AssetBalanceItem
        balance_item = AssetBalanceItem(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_QUANTITY_10_5,
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.updated_at
        )
        mock_get.return_value = balance_item

        result = asset_balance_dao.get_asset_balance(TEST_USERNAME, TEST_ASSET_ID_BTC)

        # Verify result
        assert result is not None
        assert result.username == TEST_USERNAME
        assert result.asset_id == TEST_ASSET_ID_BTC
        assert result.quantity == TEST_QUANTITY_10_5

        # Verify get was called with correct parameters
        mock_get.assert_called_once_with(TEST_USERNAME, f"{AssetBalanceFields.SK_PREFIX}{TEST_ASSET_ID_BTC}")

    @patch.object(AssetBalanceItem, MODEL_GET)
    def test_get_asset_balance_not_found(self, mock_get, asset_balance_dao):
        """Test asset balance retrieval when not found"""
        # Mock AssetBalanceItem.get to raise DoesNotExist exception
        mock_get.side_effect = getattr(AssetBalanceItem, DOES_NOT_EXIST)()

        with pytest.raises(CNOPAssetBalanceNotFoundException) as exc_info:
            asset_balance_dao.get_asset_balance(TEST_USERNAME, TEST_ASSET_ID_BTC)

        assert f"Asset balance not found for user '{TEST_USERNAME}' and asset '{TEST_ASSET_ID_BTC}'" in str(exc_info.value)
        mock_get.assert_called_once_with(TEST_USERNAME, f"{AssetBalanceFields.SK_PREFIX}{TEST_ASSET_ID_BTC}")

    # ==================== GET ALL ASSET BALANCES TESTS ====================

    @patch.object(AssetBalanceItem, MODEL_QUERY)
    def test_get_all_asset_balances_success(self, mock_query, asset_balance_dao, sample_asset_balance):
        """Test successful retrieval of all asset balances"""
        # Mock query result with multiple asset balances
        balance_item1 = AssetBalanceItem(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_QUANTITY_10_5,
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.updated_at
        )
        balance_item2 = AssetBalanceItem(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_ETH,
            quantity='25.0',
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.updated_at
        )
        mock_query.return_value = [balance_item1, balance_item2]

        result = asset_balance_dao.get_all_asset_balances(TEST_USERNAME)

        # Verify result
        assert len(result) == 2
        assert result[0].username == TEST_USERNAME
        assert result[0].asset_id == TEST_ASSET_ID_BTC
        assert result[0].quantity == TEST_QUANTITY_10_5
        assert result[1].username == TEST_USERNAME
        assert result[1].asset_id == TEST_ASSET_ID_ETH
        assert result[1].quantity == TEST_QUANTITY_25_0

        # Verify query was called
        mock_query.assert_called_once()

    @patch.object(AssetBalanceItem, MODEL_QUERY)
    def test_get_all_asset_balances_empty(self, mock_query, asset_balance_dao):
        """Test retrieval of all asset balances when user has none"""
        # Mock empty query result
        mock_query.return_value = []

        result = asset_balance_dao.get_all_asset_balances(TEST_USERNAME)

        # Verify result
        assert result == []
        mock_query.assert_called_once()

    # ==================== DELETE ASSET BALANCE TESTS ====================

    @patch.object(AssetBalanceItem, MODEL_GET)
    @patch.object(AssetBalanceItem, MODEL_DELETE)
    def test_delete_asset_balance_success(self, mock_delete, mock_get, asset_balance_dao, sample_asset_balance):
        """Test successful asset balance deletion"""
        # Mock AssetBalanceItem.get to return a real AssetBalanceItem
        balance_item = AssetBalanceItem(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_QUANTITY_10_5,
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.updated_at
        )
        mock_get.return_value = balance_item
        mock_delete.return_value = None

        result = asset_balance_dao.delete_asset_balance(TEST_USERNAME, TEST_ASSET_ID_BTC)

        # Verify result
        assert result is True

        # Verify get and delete were called
        mock_get.assert_called_once_with(TEST_USERNAME, f"{AssetBalanceFields.SK_PREFIX}BTC")
        mock_delete.assert_called_once()

    @patch.object(AssetBalanceItem, MODEL_GET)
    def test_delete_asset_balance_not_found(self, mock_get, asset_balance_dao):
        """Test asset balance deletion when not found"""
        # Mock AssetBalanceItem.get to raise DoesNotExist exception
        mock_get.side_effect = getattr(AssetBalanceItem, DOES_NOT_EXIST)()

        result = asset_balance_dao.delete_asset_balance(TEST_USERNAME, TEST_ASSET_ID_BTC)

        # Verify result
        assert result is False
        mock_get.assert_called_once_with(TEST_USERNAME, f"{AssetBalanceFields.SK_PREFIX}BTC")

    # ==================== ERROR HANDLING TESTS ====================

    @patch.object(AssetBalanceItem, MODEL_GET)
    def test_upsert_asset_balance_database_error(self, mock_get, asset_balance_dao):
        """Test upsert asset balance with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            asset_balance_dao.upsert_asset_balance(TEST_USERNAME, TEST_ASSET_ID_BTC, Decimal('5.0'))

        assert "Database operation failed while upserting asset balance" in str(exc_info.value)

    @patch.object(AssetBalanceItem, MODEL_GET)
    def test_get_asset_balance_database_error(self, mock_get, asset_balance_dao):
        """Test get asset balance with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            asset_balance_dao.get_asset_balance(TEST_USERNAME, TEST_ASSET_ID_BTC)

        assert "Database operation failed while getting asset balance" in str(exc_info.value)

    @patch.object(AssetBalanceItem, MODEL_QUERY)
    def test_get_all_asset_balances_database_error(self, mock_query, asset_balance_dao):
        """Test get all asset balances with database error"""
        # Mock database error
        mock_query.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            asset_balance_dao.get_all_asset_balances(TEST_USERNAME)

        assert "Database operation failed while getting asset balances" in str(exc_info.value)

    @patch.object(AssetBalanceItem, MODEL_GET)
    def test_delete_asset_balance_database_error(self, mock_get, asset_balance_dao):
        """Test delete asset balance with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            asset_balance_dao.delete_asset_balance(TEST_USERNAME, TEST_ASSET_ID_BTC)

        assert "Database operation failed while deleting asset balance" in str(exc_info.value)