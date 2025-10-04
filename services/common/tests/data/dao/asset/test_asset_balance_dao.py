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
            username="testuser123",
            asset_id="BTC",
            quantity=Decimal('10.5'),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    # ==================== UPSERT ASSET BALANCE TESTS ====================

    @patch.object(AssetBalanceItem, 'get')
    @patch.object(AssetBalanceItem, 'save')
    def test_upsert_asset_balance_update_existing(self, mock_save, mock_get, asset_balance_dao, sample_asset_balance):
        """Test successful asset balance update (existing item)"""
        # Mock existing balance item
        existing_balance_item = AssetBalanceItem(
            username='testuser123',
            asset_id='BTC',
            quantity='5.0',
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.created_at
        )
        mock_get.return_value = existing_balance_item
        mock_save.return_value = None

        result = asset_balance_dao.upsert_asset_balance('testuser123', 'BTC', Decimal('5.5'))

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.asset_id == "BTC"
        assert result.quantity == Decimal('10.5')  # 5.0 + 5.5

        # Verify get was called with correct parameters
        mock_get.assert_called_once_with('testuser123', f"{AssetBalanceFields.SK_PREFIX}BTC")
        # Verify save was called
        assert mock_save.called

    @patch.object(AssetBalanceItem, 'get')
    @patch.object(AssetBalanceItem, 'save')
    def test_upsert_asset_balance_create_new(self, mock_save, mock_get, asset_balance_dao):
        """Test successful asset balance creation (new item)"""
        # Mock get to raise DoesNotExist (no existing balance)
        mock_get.side_effect = AssetBalanceItem.DoesNotExist()
        mock_save.return_value = None

        result = asset_balance_dao.upsert_asset_balance('testuser123', 'ETH', Decimal('2.0'))

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.asset_id == "ETH"
        assert result.quantity == Decimal('2.0')

        # Verify get was called with correct parameters
        mock_get.assert_called_once_with('testuser123', f"{AssetBalanceFields.SK_PREFIX}ETH")
        # Verify save was called
        assert mock_save.called

    @patch.object(AssetBalanceItem, 'get')
    @patch.object(AssetBalanceItem, 'save')
    def test_upsert_asset_balance_zero_quantity(self, mock_save, mock_get, asset_balance_dao, sample_asset_balance):
        """Test asset balance upsert with zero quantity"""
        # Mock existing balance item
        existing_balance_item = AssetBalanceItem(
            username='testuser123',
            asset_id='BTC',
            quantity='10.5',
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.created_at
        )
        mock_get.return_value = existing_balance_item
        mock_save.return_value = None

        result = asset_balance_dao.upsert_asset_balance('testuser123', 'BTC', Decimal('0.0'))

        # Verify result (should remain the same)
        assert result is not None
        assert result.username == "testuser123"
        assert result.asset_id == "BTC"
        assert result.quantity == Decimal('10.5')  # 10.5 + 0.0

        # Verify get was called
        mock_get.assert_called_once_with('testuser123', f"{AssetBalanceFields.SK_PREFIX}BTC")
        # Verify save was called
        assert mock_save.called

    @patch.object(AssetBalanceItem, 'get')
    @patch.object(AssetBalanceItem, 'save')
    def test_upsert_asset_balance_negative_quantity(self, mock_save, mock_get, asset_balance_dao, sample_asset_balance):
        """Test asset balance upsert with negative quantity"""
        # Mock existing balance item
        existing_balance_item = AssetBalanceItem(
            username='testuser123',
            asset_id='BTC',
            quantity='10.5',
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.created_at
        )
        mock_get.return_value = existing_balance_item
        mock_save.return_value = None

        result = asset_balance_dao.upsert_asset_balance('testuser123', 'BTC', Decimal('-2.0'))

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.asset_id == "BTC"
        assert result.quantity == Decimal('8.5')  # 10.5 + (-2.0)

        # Verify get was called
        mock_get.assert_called_once_with('testuser123', f"{AssetBalanceFields.SK_PREFIX}BTC")
        # Verify save was called
        assert mock_save.called

    # ==================== GET ASSET BALANCE TESTS ====================

    @patch.object(AssetBalanceItem, 'get')
    def test_get_asset_balance_success(self, mock_get, asset_balance_dao, sample_asset_balance):
        """Test successful asset balance retrieval"""
        # Mock AssetBalanceItem.get to return a real AssetBalanceItem
        balance_item = AssetBalanceItem(
            username='testuser123',
            asset_id='BTC',
            quantity='10.5',
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.updated_at
        )
        mock_get.return_value = balance_item

        result = asset_balance_dao.get_asset_balance('testuser123', 'BTC')

        # Verify result
        assert result is not None
        assert result.username == "testuser123"
        assert result.asset_id == "BTC"
        assert result.quantity == Decimal('10.5')

        # Verify get was called with correct parameters
        mock_get.assert_called_once_with('testuser123', f"{AssetBalanceFields.SK_PREFIX}BTC")

    @patch.object(AssetBalanceItem, 'get')
    def test_get_asset_balance_not_found(self, mock_get, asset_balance_dao):
        """Test asset balance retrieval when not found"""
        # Mock AssetBalanceItem.get to raise DoesNotExist exception
        mock_get.side_effect = AssetBalanceItem.DoesNotExist()

        with pytest.raises(CNOPAssetBalanceNotFoundException) as exc_info:
            asset_balance_dao.get_asset_balance('testuser123', 'BTC')

        assert "Asset balance not found for user 'testuser123' and asset 'BTC'" in str(exc_info.value)
        mock_get.assert_called_once_with('testuser123', f"{AssetBalanceFields.SK_PREFIX}BTC")

    # ==================== GET ALL ASSET BALANCES TESTS ====================

    @patch.object(AssetBalanceItem, 'query')
    def test_get_all_asset_balances_success(self, mock_query, asset_balance_dao, sample_asset_balance):
        """Test successful retrieval of all asset balances"""
        # Mock query result with multiple asset balances
        balance_item1 = AssetBalanceItem(
            username='testuser123',
            asset_id='BTC',
            quantity='10.5',
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.updated_at
        )
        balance_item2 = AssetBalanceItem(
            username='testuser123',
            asset_id='ETH',
            quantity='25.0',
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.updated_at
        )
        mock_query.return_value = [balance_item1, balance_item2]

        result = asset_balance_dao.get_all_asset_balances('testuser123')

        # Verify result
        assert len(result) == 2
        assert result[0].username == "testuser123"
        assert result[0].asset_id == "BTC"
        assert result[0].quantity == Decimal('10.5')
        assert result[1].username == "testuser123"
        assert result[1].asset_id == "ETH"
        assert result[1].quantity == Decimal('25.0')

        # Verify query was called
        mock_query.assert_called_once()

    @patch.object(AssetBalanceItem, 'query')
    def test_get_all_asset_balances_empty(self, mock_query, asset_balance_dao):
        """Test retrieval of all asset balances when user has none"""
        # Mock empty query result
        mock_query.return_value = []

        result = asset_balance_dao.get_all_asset_balances('testuser123')

        # Verify result
        assert result == []
        mock_query.assert_called_once()

    # ==================== DELETE ASSET BALANCE TESTS ====================

    @patch.object(AssetBalanceItem, 'get')
    @patch.object(AssetBalanceItem, 'delete')
    def test_delete_asset_balance_success(self, mock_delete, mock_get, asset_balance_dao, sample_asset_balance):
        """Test successful asset balance deletion"""
        # Mock AssetBalanceItem.get to return a real AssetBalanceItem
        balance_item = AssetBalanceItem(
            username='testuser123',
            asset_id='BTC',
            quantity='10.5',
            created_at=sample_asset_balance.created_at,
            updated_at=sample_asset_balance.updated_at
        )
        mock_get.return_value = balance_item
        mock_delete.return_value = None

        result = asset_balance_dao.delete_asset_balance('testuser123', 'BTC')

        # Verify result
        assert result is True

        # Verify get and delete were called
        mock_get.assert_called_once_with('testuser123', f"{AssetBalanceFields.SK_PREFIX}BTC")
        mock_delete.assert_called_once()

    @patch.object(AssetBalanceItem, 'get')
    def test_delete_asset_balance_not_found(self, mock_get, asset_balance_dao):
        """Test asset balance deletion when not found"""
        # Mock AssetBalanceItem.get to raise DoesNotExist exception
        mock_get.side_effect = AssetBalanceItem.DoesNotExist()

        result = asset_balance_dao.delete_asset_balance('testuser123', 'BTC')

        # Verify result
        assert result is False
        mock_get.assert_called_once_with('testuser123', f"{AssetBalanceFields.SK_PREFIX}BTC")

    # ==================== ERROR HANDLING TESTS ====================

    @patch.object(AssetBalanceItem, 'get')
    def test_upsert_asset_balance_database_error(self, mock_get, asset_balance_dao):
        """Test upsert asset balance with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            asset_balance_dao.upsert_asset_balance('testuser123', 'BTC', Decimal('5.0'))

        assert "Database operation failed while upserting asset balance" in str(exc_info.value)

    @patch.object(AssetBalanceItem, 'get')
    def test_get_asset_balance_database_error(self, mock_get, asset_balance_dao):
        """Test get asset balance with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            asset_balance_dao.get_asset_balance('testuser123', 'BTC')

        assert "Database operation failed while getting asset balance" in str(exc_info.value)

    @patch.object(AssetBalanceItem, 'query')
    def test_get_all_asset_balances_database_error(self, mock_query, asset_balance_dao):
        """Test get all asset balances with database error"""
        # Mock database error
        mock_query.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            asset_balance_dao.get_all_asset_balances('testuser123')

        assert "Database operation failed while getting asset balances" in str(exc_info.value)

    @patch.object(AssetBalanceItem, 'get')
    def test_delete_asset_balance_database_error(self, mock_get, asset_balance_dao):
        """Test delete asset balance with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            asset_balance_dao.delete_asset_balance('testuser123', 'BTC')

        assert "Database operation failed while deleting asset balance" in str(exc_info.value)