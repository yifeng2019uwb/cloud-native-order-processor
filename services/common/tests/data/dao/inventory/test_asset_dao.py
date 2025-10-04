import os
import sys
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

# Add the common directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data.dao.inventory.asset_dao import AssetDAO
from src.data.entities.inventory import Asset, AssetItem
from src.data.entities.entity_constants import AssetFields
from src.data.exceptions import CNOPDatabaseOperationException
from src.exceptions.shared_exceptions import CNOPAssetNotFoundException
from tests.data.dao.mock_constants import MockDatabaseMethods


class TestAssetDAO:
    """Comprehensive test suite for AssetDAO"""

    @pytest.fixture
    def asset_dao(self):
        """Create AssetDAO instance (PynamoDB doesn't need db_connection)"""
        return AssetDAO()

    @pytest.fixture
    def sample_asset_create(self):
        return Asset(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=Decimal("10.5"),
            price_usd=Decimal("45000.0"),
            symbol="BTC",
            image="https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
            market_cap_rank=1,
            high_24h=68000.0,
            low_24h=66000.0,
            circulating_supply=19400000.0,
            price_change_24h=500.0,
            ath_change_percentage=-2.5,
            market_cap=1300000000000.0
        )

    @pytest.fixture
    def sample_asset_create_zero_price(self):
        """Sample asset creation data with zero price"""
        return Asset(
            asset_id="TEST",
            name="Test Asset",
            description="Test asset with zero price",
            category="stablecoin",
            amount=Decimal("100.0"),
            price_usd=Decimal("0.0")
        )

    @pytest.fixture
    def sample_asset(self):
        """Sample asset data"""
        return Asset(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=Decimal("10.5"),
            price_usd=Decimal("45000.0"),
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )

    @pytest.fixture
    def sample_db_item(self):
        now = datetime.now(UTC).isoformat()
        return {
            'product_id': 'BTC',
            'asset_id': 'BTC',
            'name': 'Bitcoin',
            'description': 'Digital currency',
            'category': 'major',
            'amount': Decimal("10.5"),
            'price_usd': Decimal("45000.0"),
            'symbol': 'BTC',
            'image': 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png',
            'market_cap_rank': 1,
            'high_24h': 68000.0,
            'low_24h': 66000.0,
            'circulating_supply': 19400000.0,
            'price_change_24h': 500.0,
            'ath_change_percentage': -2.5,
            'market_cap': 1300000000000.0,
            'is_active': True,
            'created_at': now,
            'updated_at': now
        }

    # ==================== CREATE ASSET TESTS ====================

    @patch.object(AssetItem, MockDatabaseMethods.SAVE)
    def test_create_asset_success(self, mock_save, asset_dao, sample_asset_create):
        """Test successful asset creation"""
        # save() returns None, so just let it do nothing
        mock_save.return_value = None

        result = asset_dao.create_asset(sample_asset_create)

        assert isinstance(result, Asset)
        assert result.asset_id == "BTC"
        assert result.name == "Bitcoin"
        assert result.symbol == "BTC"
        assert result.image.startswith("https://")
        assert result.market_cap_rank == 1
        assert result.high_24h == 68000.0
        assert result.low_24h == 66000.0
        assert result.circulating_supply == 19400000.0
        assert result.price_change_24h == 500.0
        assert result.ath_change_percentage == -2.5
        assert result.market_cap == 1300000000000.0
        assert result.is_active is True
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)

        # Verify save was called
        mock_save.assert_called_once()

    @patch.object(AssetItem, MockDatabaseMethods.SAVE)
    def test_create_asset_database_error(self, mock_save, asset_dao, sample_asset_create):
        """Test create asset with database error"""
        # Mock database exception during save
        mock_save.side_effect = Exception("Database error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            asset_dao.create_asset(sample_asset_create)

        assert "Database error" in str(exc_info.value)

    # ==================== GET ASSET BY ID TESTS ====================

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    def test_get_asset_by_id_found(self, mock_get, asset_dao):
        """Test getting asset by ID when asset exists"""
        # Mock AssetItem.get to return a real AssetItem
        asset_item = AssetItem(
            product_id='BTC',
            asset_id='BTC',
            name='Bitcoin',
            description='Digital currency',
            category='major',
            amount=10.5,
            price_usd=67000.0,
            symbol='BTC',
            image='https://assets.coingecko.com/coins/images/1/large/bitcoin.png',
            market_cap_rank=1,
            high_24h=68000.0,
            low_24h=66000.0,
            circulating_supply=19400000.0,
            price_change_24h=500.0,
            ath_change_percentage=-2.5,
            market_cap=1300000000000.0,
            is_active=True
        )
        mock_get.return_value = asset_item

        result = asset_dao.get_asset_by_id('BTC')

        assert isinstance(result, Asset)
        assert result.asset_id == 'BTC'
        assert result.name == 'Bitcoin'
        assert result.symbol == 'BTC'
        assert result.image.startswith('https://')
        assert result.market_cap_rank == 1
        assert result.high_24h == 68000.0
        assert result.low_24h == 66000.0
        assert result.circulating_supply == 19400000.0
        assert result.price_change_24h == 500.0
        assert result.ath_change_percentage == -2.5
        assert result.market_cap == 1300000000000.0
        assert result.is_active is True

        # Verify get was called with correct parameters
        mock_get.assert_called_once_with('BTC')

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    def test_get_asset_by_id_not_found(self, mock_get, asset_dao):
        """Test get asset by ID when asset not found"""
        # Mock AssetItem.get to raise DoesNotExist exception
        mock_get.side_effect = AssetItem.DoesNotExist()

        # Should raise CNOPAssetNotFoundException
        with pytest.raises(CNOPAssetNotFoundException) as exc_info:
            asset_dao.get_asset_by_id('NONEXISTENT')

        assert "Asset 'NONEXISTENT' not found" in str(exc_info.value)

        # Verify get was called with correct parameters
        mock_get.assert_called_once_with('NONEXISTENT')

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    def test_get_asset_by_id_database_error(self, mock_get, asset_dao):
        """Test get asset by ID with database error"""
        # Mock database error
        mock_get.side_effect = Exception("Database error")

        # Should raise CNOPDatabaseOperationException
        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            asset_dao.get_asset_by_id('BTC')

        assert "Database error" in str(exc_info.value)

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    def test_get_asset_by_id_missing_fields(self, mock_get, asset_dao):
        """Test getting asset with missing optional fields"""
        # Mock AssetItem with minimal fields
        minimal_item = AssetItem(
            product_id='BTC',
            asset_id='BTC',
            name='Bitcoin',
            category='major',
            amount=1.0,
            price_usd=50000.0,
            is_active=True  # Default value
        )
        mock_get.return_value = minimal_item

        # Get asset
        result = asset_dao.get_asset_by_id('BTC')

        # Verify result with defaults
        assert result.description is None  # Default for missing description
        assert result.is_active is True  # Default for missing is_active

    # ==================== GET ALL ASSETS TESTS ====================

    @patch.object(AssetItem, MockDatabaseMethods.SCAN)
    def test_get_all_assets_success(self, mock_scan, asset_dao):
        """Test getting all assets successfully"""
        # Mock AssetItem.scan to return AssetItem instances
        asset_items = [
            AssetItem(
                product_id='BTC',
                asset_id='BTC',
                name='Bitcoin',
                category='major',
                amount=10.0,
                price_usd=45000.0,
                is_active=True
            ),
            AssetItem(
                product_id='ETH',
                asset_id='ETH',
                name='Ethereum',
                category='altcoin',
                amount=100.0,
                price_usd=3000.0,
                is_active=True
            ),
            AssetItem(
                product_id='OLD',
                asset_id='OLD',
                name='Old Asset',
                category='altcoin',
                amount=50.0,
                price_usd=0.0,
                is_active=False
            )
        ]
        mock_scan.return_value = asset_items

        # Get all assets
        result = asset_dao.get_all_assets()

        # Verify result
        assert len(result) == 3
        assert all(isinstance(asset, Asset) for asset in result)
        assert result[0].asset_id == 'BTC'
        assert result[1].asset_id == 'ETH'
        assert result[2].asset_id == 'OLD'

        # Verify scan was called without filter
        mock_scan.assert_called_once_with()

    @patch.object(AssetItem, MockDatabaseMethods.SCAN)
    def test_get_all_assets_active_only(self, mock_scan, asset_dao):
        """Test getting only active assets"""
        # Mock AssetItem.scan to return only active AssetItem instances
        asset_items = [
            AssetItem(
                product_id='BTC',
                asset_id='BTC',
                name='Bitcoin',
                category='major',
                amount=10.0,
                price_usd=45000.0,
                is_active=True
            )
        ]
        mock_scan.return_value = asset_items

        # Get active assets only
        result = asset_dao.get_all_assets(active_only=True)

        # Verify result
        assert len(result) == 1
        assert result[0].is_active is True

        # Verify scan was called with filter
        mock_scan.assert_called_once()

    @patch.object(AssetItem, MockDatabaseMethods.SCAN)
    def test_get_all_assets_empty_result(self, mock_scan, asset_dao):
        """Test getting all assets when none exist"""
        # Mock empty scan result
        mock_scan.return_value = []

        # Get all assets
        result = asset_dao.get_all_assets()

        # Should return empty list
        assert result == []

    @patch.object(AssetItem, MockDatabaseMethods.SCAN)
    def test_get_all_assets_filter_invalid_items(self, mock_scan, asset_dao):
        """Test getting all assets filters out items without asset fields"""
        # Mock scan to return mix of valid and invalid items
        now = datetime.now(UTC).isoformat()

        # Valid asset item
        valid_item = AssetItem(
            asset_id='BTC',
            name='Bitcoin',
            category='major',
            amount='10.0',
            price_usd='45000.0',
            is_active=True,
            created_at=now,
            updated_at=now
        )

        # Invalid item (will be filtered out by PynamoDB model validation)
        invalid_item = AssetItem(
            asset_id='INVALID',
            name='Invalid Asset',
            category='invalid',
            amount='0.0',
            price_usd='0.0',
            is_active=True,
            created_at=now,
            updated_at=now
        )

        mock_scan.return_value = [valid_item, invalid_item]

        # Get all assets
        result = asset_dao.get_all_assets()

        # Should return all asset items (both valid and invalid)
        assert len(result) == 2
        assert result[0].asset_id == 'BTC'
        assert result[1].asset_id == 'INVALID'

    @patch.object(AssetItem, MockDatabaseMethods.SCAN)
    def test_get_all_assets_database_error(self, mock_scan, asset_dao):
        """Test get all assets with database error"""
        # Mock database error
        mock_scan.side_effect = Exception("Database error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            asset_dao.get_all_assets()

        assert "Database error" in str(exc_info.value)

    # ==================== UPDATE ASSET TESTS ====================

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    @patch.object(AssetItem, MockDatabaseMethods.SAVE)
    def test_update_asset_success(self, mock_save, mock_get, asset_dao):
        now = datetime.now(UTC).isoformat()

        # Mock existing asset item
        existing_item = AssetItem(
            asset_id='BTC',
            name='Bitcoin',
            description='Original desc',
            category='major',
            amount='10.0',
            price_usd='45000.0',
            is_active=True,
            created_at=now,
            updated_at=now
        )
        mock_get.return_value = existing_item

        # Mock save to return the updated item
        mock_save.return_value = None
        asset_update = Asset(
            asset_id="BTC",
            name="Bitcoin",
            category="major",
            description="Updated desc",
            amount=Decimal("20.0"),
            price_usd=Decimal("50000.0"),
            symbol="BTC",
            image="https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
            market_cap_rank=1,
            high_24h=70000.0,
            low_24h=65000.0,
            circulating_supply=20000000.0,
            price_change_24h=1000.0,
            ath_change_percentage=-1.5,
            market_cap=1400000000000.0
        )
        result = asset_dao.update_asset(asset_update)
        # update_asset returns an Asset entity
        assert isinstance(result, Asset)
        assert result.asset_id == "BTC"
        assert result.description == "Updated desc"
        assert result.amount == Decimal("20.0")
        assert result.price_usd == Decimal("50000.0")
        assert result.symbol == "BTC"
        assert result.image.startswith("https://")
        assert result.market_cap_rank == 1
        assert result.high_24h == 70000.0
        assert result.low_24h == 65000.0
        assert result.circulating_supply == 20000000.0
        assert result.price_change_24h == 1000.0
        assert result.ath_change_percentage == -1.5
        assert result.market_cap == 1400000000000.0
        assert result.is_active is True
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    @patch.object(AssetItem, MockDatabaseMethods.SAVE)
    def test_update_asset_no_changes(self, mock_save, mock_get, asset_dao):
        """Test update asset with no changes returns current asset"""
        # Mock existing asset item
        existing_item = AssetItem(
            asset_id='BTC',
            name='Bitcoin',
            description='Digital currency',
            category='major',
            amount='1.0',
            price_usd='50000.0',
            is_active=True
        )
        mock_get.return_value = existing_item
        mock_save.return_value = None

        # Create update with required fields
        asset_update = Asset(
            asset_id="BTC",
            name="Bitcoin",
            category="major",
            amount=Decimal("1.0"),
            price_usd=Decimal("50000.0")
        )

        # Update asset
        result = asset_dao.update_asset(asset_update)

        # Should return updated asset
        assert isinstance(result, Asset)
        assert result.asset_id == "BTC"

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    @patch.object(AssetItem, MockDatabaseMethods.SAVE)
    def test_update_asset_price_zero_forces_inactive(self, mock_save, mock_get, asset_dao):
        """Test updating price to zero forces is_active to False"""
        now = datetime.now(UTC).isoformat()

        # Mock existing asset item
        existing_item = AssetItem(
            product_id='BTC',
            asset_id='BTC',
            name='Bitcoin',
            description='Original desc',
            category='major',
            amount=10.0,
            price_usd=45000.0,
            is_active=True,
            created_at=now,
            updated_at=now
        )
        mock_get.return_value = existing_item
        mock_save.return_value = None

        # Create update data with zero price
        asset_update = Asset(
            asset_id="BTC",
            name="Bitcoin",
            category="major",
            amount=Decimal("10.0"),
            price_usd=Decimal("0.0")
        )

        # Update asset
        result = asset_dao.update_asset(asset_update)

        # Verify result (update_asset returns an Asset object)
        assert result.price_usd == Decimal("0.0")
        assert result.is_active is False

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    def test_update_asset_not_found(self, mock_get, asset_dao):
        """Test update asset when asset not found"""
        # Mock that asset doesn't exist
        mock_get.side_effect = AssetItem.DoesNotExist()

        # Should raise CNOPAssetNotFoundException directly
        asset_update = Asset(
            asset_id="NONEXISTENT",
            name="Test",
            category="major",
            amount=Decimal("1.0"),
            price_usd=Decimal("100.0"),
            description='New description'
        )
        with pytest.raises(CNOPAssetNotFoundException):
            asset_dao.update_asset(asset_update)

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    @patch.object(AssetItem, MockDatabaseMethods.SAVE)
    def test_update_asset_database_error(self, mock_save, mock_get, asset_dao):
        """Test update asset with database error"""
        now = datetime.now(UTC).isoformat()

        # Mock existing asset item
        existing_item = AssetItem(
            asset_id='BTC',
            name='Bitcoin',
            description='Original desc',
            category='major',
            amount='10.0',
            price_usd='45000.0',
            is_active=True,
            created_at=now,
            updated_at=now
        )
        mock_get.return_value = existing_item

        # Mock database error on save
        mock_save.side_effect = Exception("Database error")

        # Create update data
        asset_update = Asset(
            asset_id="BTC",
            name="Bitcoin",
            category="major",
            amount=Decimal("1.0"),
            price_usd=Decimal("50000.0"),
            description="Updated description"
        )

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            asset_dao.update_asset(asset_update)

        assert "Database error" in str(exc_info.value)


    # ==================== EDGE CASE AND ERROR HANDLING TESTS ====================

    @patch.object(AssetItem, MockDatabaseMethods.SCAN)
    def test_get_all_assets_with_missing_fields(self, mock_scan, asset_dao):
        """Test get all assets handles items with missing fields gracefully"""
        now = datetime.now(UTC).isoformat()

        # Complete item
        complete_item = AssetItem(
            asset_id='BTC',
            name='Bitcoin',
            description='Digital currency',
            category='major',
            amount='10.0',
            price_usd='45000.0',
            is_active=True,
            created_at=now,
            updated_at=now
        )

        # Item with missing optional fields (PynamoDB will use defaults)
        incomplete_item = AssetItem(
            asset_id='ETH',
            name='Ethereum',
            category='altcoin',
            amount='100.0',
            price_usd='3000.0',
            is_active=True  # Default value
        )

        mock_scan.return_value = [complete_item, incomplete_item]

        # Get all assets
        result = asset_dao.get_all_assets()

        # Should handle missing fields with defaults
        assert len(result) == 2
        assert result[1].description is None  # Default for missing description
        assert result[1].is_active is True  # Default value
        assert isinstance(result[1].created_at, datetime)
        assert isinstance(result[1].updated_at, datetime)

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    @patch.object(AssetItem, MockDatabaseMethods.SAVE)
    def test_update_asset_builds_correct_expression(self, mock_save, mock_get, asset_dao):
        """Test that update asset works with multiple field updates"""
        now = datetime.now(UTC).isoformat()

        # Mock existing asset item
        existing_item = AssetItem(
            asset_id='BTC',
            name='Bitcoin',
            description='Original desc',
            category='major',
            amount='10.0',
            price_usd='45000.0',
            is_active=True,
            created_at=now,
            updated_at=now
        )
        mock_get.return_value = existing_item
        mock_save.return_value = None

        # Create update with multiple fields
        asset_update = Asset(
            asset_id="BTC",
            name="Bitcoin",
            description="Updated description",
            category="altcoin",
            amount=Decimal("15.0"),
            price_usd=Decimal("50000.0"),
            is_active=True
        )

        # Update asset
        result = asset_dao.update_asset(asset_update)

        # Verify result
        assert isinstance(result, Asset)
        assert result.asset_id == "BTC"
        assert result.description == "Updated description"
        assert result.category == "altcoin"
        assert result.amount == Decimal("15.0")
        assert result.price_usd == Decimal("50000.0")
        assert result.is_active is True

        # Verify get and save were called
        mock_get.assert_called_once_with('BTC')
        mock_save.assert_called_once()

    # ==================== COMPREHENSIVE ERROR SCENARIO TESTS ====================

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    @patch.object(AssetItem, MockDatabaseMethods.SAVE)
    def test_create_asset_with_various_exceptions(self, mock_save, mock_get, asset_dao, sample_asset_create):
        """Test create asset handles various exception types"""
        # Mock that asset doesn't exist
        mock_get.side_effect = AssetItem.DoesNotExist()

        exception_types = [
            Exception("Generic error"),
            ValueError("Value error"),
            RuntimeError("Runtime error"),
            KeyError("Key error")
        ]

        for exception in exception_types:
            # Reset mock for each iteration
            mock_save.side_effect = exception

            # Should raise CNOPDatabaseOperationException (our design wraps all DB exceptions)
            with pytest.raises(CNOPDatabaseOperationException) as exc_info:
                asset_dao.create_asset(sample_asset_create)

            # Verify the original exception message is preserved
            assert str(exception) in str(exc_info.value)
    # ==================== BOUNDARY VALUE TESTS ====================

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    @patch.object(AssetItem, MockDatabaseMethods.SAVE)
    def test_asset_with_extreme_values(self, mock_save, mock_get, asset_dao):
        """Test asset creation with boundary values"""
        # Mock that asset doesn't exist
        mock_get.side_effect = AssetItem.DoesNotExist()
        mock_save.return_value = None

        # Test with very small values
        small_asset = Asset(
            asset_id="MIN",
            name="Minimal Asset",
            description="",
            category="stablecoin",
            amount=Decimal("0.00000001"),  # Smallest possible amount
            price_usd=Decimal("0.01")  # Smallest price
        )

        result = asset_dao.create_asset(small_asset)
        assert result.amount == Decimal("0.00000001")
        assert result.price_usd == Decimal("0.01")

        # Test with very large values
        large_asset = Asset(
            asset_id="MAX",
            name="Maximum Asset",
            description="A" * 500,  # Maximum description length (500 chars)
            category="major",
            amount=Decimal("999999999.99999999"),  # Very large amount
            price_usd=Decimal("999999.99")  # Very large price
        )

        result = asset_dao.create_asset(large_asset)
        assert result.amount == Decimal("1000000000.0")  # Float conversion loses precision
        assert result.price_usd == Decimal("999999.99")
        assert len(result.description) == 500

    # ==================== BATCH GET ASSETS BY IDS TESTS ====================

    def test_get_assets_by_ids_empty_list(self, asset_dao):
        """Test get_assets_by_ids with empty list returns empty dict"""
        result = asset_dao.get_assets_by_ids([])
        assert result == {}

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    def test_get_assets_by_ids_success(self, mock_get, asset_dao):
        """Test successful batch retrieval of assets"""
        # Mock AssetItem.get to return AssetItem instances
        btc_item = AssetItem(
            product_id='BTC',
            asset_id='BTC',
            name='Bitcoin',
            description='Digital currency',
            category='major',
            amount=10.5,
            price_usd=45000.0,
            is_active=True
        )
        eth_item = AssetItem(
            product_id='ETH',
            asset_id='ETH',
            name='Ethereum',
            description='Smart contract platform',
            category='altcoin',
            amount=100.0,
            price_usd=3000.0,
            is_active=True
        )

        # Mock get to return different items based on asset_id
        def mock_get_side_effect(asset_id):
            if asset_id == 'BTC':
                return btc_item
            elif asset_id == 'ETH':
                return eth_item
            else:
                raise AssetItem.DoesNotExist()

        mock_get.side_effect = mock_get_side_effect

        # Test batch retrieval
        result = asset_dao.get_assets_by_ids(['BTC', 'ETH'])

        # Verify result
        assert len(result) == 2
        assert 'BTC' in result
        assert 'ETH' in result
        assert isinstance(result['BTC'], Asset)
        assert isinstance(result['ETH'], Asset)
        assert result['BTC'].name == 'Bitcoin'
        assert result['ETH'].name == 'Ethereum'

        # Verify get was called for each asset
        assert mock_get.call_count == 2
        mock_get.assert_any_call('BTC')
        mock_get.assert_any_call('ETH')

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    def test_get_assets_by_ids_with_unprocessed_keys(self, mock_get, asset_dao):
        """Test batch retrieval with some assets not found (simulating unprocessed keys)"""
        # Mock AssetItem.get to return some assets and raise DoesNotExist for others
        btc_item = AssetItem(
            product_id='BTC',
            asset_id='BTC',
            name='Bitcoin',
            description='Digital currency',
            category='major',
            amount=10.5,
            price_usd=45000.0,
            is_active=True
        )

        # Mock get to return BTC but raise DoesNotExist for ETH
        def mock_get_side_effect(asset_id):
            if asset_id == 'BTC':
                return btc_item
            else:
                raise AssetItem.DoesNotExist()

        mock_get.side_effect = mock_get_side_effect

        # Test batch retrieval
        result = asset_dao.get_assets_by_ids(['BTC', 'ETH'])

        # Verify result - only BTC should be returned, ETH should be skipped
        assert len(result) == 1
        assert 'BTC' in result
        assert 'ETH' not in result
        assert isinstance(result['BTC'], Asset)
        assert result['BTC'].name == 'Bitcoin'

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    def test_get_assets_by_ids_missing_assets(self, mock_get, asset_dao):
        """Test batch retrieval when some assets are missing"""
        # Mock AssetItem.get to return some assets and raise DoesNotExist for others
        btc_item = AssetItem(
            product_id='BTC',
            asset_id='BTC',
            name='Bitcoin',
            description='Digital currency',
            category='major',
            amount=10.5,
            price_usd=45000.0,
            is_active=True
        )

        # Mock get to return BTC but raise DoesNotExist for ETH
        def mock_get_side_effect(asset_id):
            if asset_id == 'BTC':
                return btc_item
            else:
                raise AssetItem.DoesNotExist()

        mock_get.side_effect = mock_get_side_effect

        # Test batch retrieval
        result = asset_dao.get_assets_by_ids(['BTC', 'MISSING'])

        # Verify result - only found assets are returned
        assert len(result) == 1
        assert 'BTC' in result
        assert 'MISSING' not in result
        assert isinstance(result['BTC'], Asset)
        assert result['BTC'].name == 'Bitcoin'

    @patch.object(AssetItem, MockDatabaseMethods.GET)
    def test_get_assets_by_ids_database_error(self, mock_get, asset_dao):
        """Test batch retrieval with database error"""
        # Mock database error on get
        mock_get.side_effect = Exception("Database error")

        # Should raise CNOPDatabaseOperationException
        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            asset_dao.get_assets_by_ids(['BTC', 'ETH'])

        assert "Database error" in str(exc_info.value)
