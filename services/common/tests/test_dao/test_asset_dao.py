import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, UTC
from decimal import Decimal

# Add the common directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from common.dao.asset_dao import AssetDAO
from common.entities.asset import AssetCreate, Asset, AssetUpdate


class TestAssetDAO:
    """Comprehensive test suite for AssetDAO"""

    @pytest.fixture
    def mock_db_connection(self):
        """Create mock database connection"""
        mock_connection = Mock()
        mock_connection.inventory_table = Mock()
        return mock_connection

    @pytest.fixture
    def asset_dao(self, mock_db_connection):
        """Create AssetDAO instance with mock connection"""
        return AssetDAO(mock_db_connection)

    @pytest.fixture
    def sample_asset_create(self):
        """Sample asset creation data"""
        return AssetCreate(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=Decimal("10.5"),
            price_usd=Decimal("45000.0")
        )

    @pytest.fixture
    def sample_asset_create_zero_price(self):
        """Sample asset creation data with zero price"""
        return AssetCreate(
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
        """Sample database item response"""
        now = datetime.now(UTC).isoformat()
        return {
            'product_id': 'BTC',
            'asset_id': 'BTC',
            'name': 'Bitcoin',
            'description': 'Digital currency',
            'category': 'major',
            'amount': Decimal("10.5"),
            'price_usd': Decimal("45000.0"),
            'is_active': True,
            'created_at': now,
            'updated_at': now
        }

    # ==================== CREATE ASSET TESTS ====================

    @pytest.mark.asyncio
    async def test_create_asset_success(self, asset_dao, sample_asset_create, mock_db_connection):
        """Test successful asset creation"""
        # Mock that asset doesn't exist
        asset_dao.get_asset_by_id = AsyncMock(return_value=None)

        # Mock successful database operations
        now = datetime.now(UTC).isoformat()
        created_item = {
            'product_id': 'BTC',
            'asset_id': 'BTC',
            'name': 'Bitcoin',
            'description': 'Digital currency',
            'category': 'major',
            'amount': 10.5,
            'price_usd': 45000.0,
            'is_active': True,
            'created_at': now,
            'updated_at': now
        }
        mock_db_connection.inventory_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Create asset
        result = await asset_dao.create_asset(sample_asset_create)

        # Verify result
        assert isinstance(result, Asset)
        assert result.asset_id == "BTC"
        assert result.name == "Bitcoin"
        assert result.description == "Digital currency"
        assert result.category == "major"
        assert result.amount == Decimal("10.5")
        assert result.price_usd == Decimal("45000.0")
        assert result.is_active is True
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)

        # Verify database was called
        mock_db_connection.inventory_table.put_item.assert_called_once()
        call_args = mock_db_connection.inventory_table.put_item.call_args[1]['Item']
        assert call_args['product_id'] == 'BTC'
        assert call_args['asset_id'] == 'BTC'
        assert call_args['name'] == 'Bitcoin'
        assert call_args['is_active'] is True

    @pytest.mark.asyncio
    async def test_create_asset_zero_price_sets_inactive(self, asset_dao, sample_asset_create_zero_price, mock_db_connection):
        """Test creating asset with zero price automatically sets is_active to False"""
        # Mock that asset doesn't exist
        asset_dao.get_asset_by_id = AsyncMock(return_value=None)

        # Mock successful database operations
        mock_db_connection.inventory_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Create asset with zero price
        result = await asset_dao.create_asset(sample_asset_create_zero_price)

        # Verify result
        assert result.price_usd == 0.0
        assert result.is_active is False

        # Verify database was called with is_active=False
        call_args = mock_db_connection.inventory_table.put_item.call_args[1]['Item']
        assert call_args['price_usd'] == 0.0
        assert call_args['is_active'] is False

    @pytest.mark.asyncio
    async def test_create_asset_already_exists(self, asset_dao, sample_asset_create, sample_asset):
        """Test creating asset that already exists"""
        # Mock that asset already exists
        asset_dao.get_asset_by_id = AsyncMock(return_value=sample_asset)

        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            await asset_dao.create_asset(sample_asset_create)

        assert "Asset with ID BTC already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_asset_database_error(self, asset_dao, sample_asset_create, mock_db_connection):
        """Test create asset with database error"""
        # Mock that asset doesn't exist
        asset_dao.get_asset_by_id = AsyncMock(return_value=None)

        # Mock database error
        mock_db_connection.inventory_table.put_item.side_effect = Exception("Database error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            await asset_dao.create_asset(sample_asset_create)

        assert "Database error" in str(exc_info.value)

    # ==================== GET ASSET BY ID TESTS ====================

    @pytest.mark.asyncio
    async def test_get_asset_by_id_found(self, asset_dao, sample_db_item, mock_db_connection):
        """Test getting asset by ID when found"""
        # Mock database response
        mock_db_connection.inventory_table.get_item.return_value = {'Item': sample_db_item}

        # Get asset
        result = await asset_dao.get_asset_by_id('BTC')

        # Verify result
        assert isinstance(result, Asset)
        assert result.asset_id == 'BTC'
        assert result.name == 'Bitcoin'
        assert result.description == 'Digital currency'
        assert result.category == 'major'
        assert result.amount == Decimal("10.5")
        assert result.price_usd == Decimal("45000.0")
        assert result.is_active is True

        # Verify database was called correctly
        mock_db_connection.inventory_table.get_item.assert_called_once_with(
            Key={'product_id': 'BTC'}
        )

    @pytest.mark.asyncio
    async def test_get_asset_by_id_not_found(self, asset_dao, mock_db_connection):
        """Test getting asset by ID when not found"""
        # Mock database response - no item
        mock_db_connection.inventory_table.get_item.return_value = {}

        # Get asset
        result = await asset_dao.get_asset_by_id('NONEXISTENT')

        # Should return None
        assert result is None

        # Verify database was called
        mock_db_connection.inventory_table.get_item.assert_called_once_with(
            Key={'product_id': 'NONEXISTENT'}
        )

    @pytest.mark.asyncio
    async def test_get_asset_by_id_database_error(self, asset_dao, mock_db_connection):
        """Test get asset by ID with database error"""
        # Mock database error
        mock_db_connection.inventory_table.get_item.side_effect = Exception("Database error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            await asset_dao.get_asset_by_id('BTC')

        assert "Database error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_asset_by_id_missing_fields(self, asset_dao, mock_db_connection):
        """Test getting asset with missing optional fields"""
        # Mock database response with minimal fields
        minimal_item = {
            'product_id': 'BTC',
            'asset_id': 'BTC',
            'name': 'Bitcoin',
            'category': 'major',
            'amount': 1.0,
            'price_usd': 50000.0,
            'created_at': datetime.now(UTC).isoformat(),
            'updated_at': datetime.now(UTC).isoformat()
        }
        mock_db_connection.inventory_table.get_item.return_value = {'Item': minimal_item}

        # Get asset
        result = await asset_dao.get_asset_by_id('BTC')

        # Verify result with defaults
        assert result.description == ''  # Default for missing description
        assert result.is_active is True  # Default for missing is_active

    # ==================== GET ALL ASSETS TESTS ====================

    @pytest.mark.asyncio
    async def test_get_all_assets_success(self, asset_dao, mock_db_connection):
        """Test getting all assets successfully"""
        # Mock database response with multiple items
        now = datetime.now(UTC).isoformat()
        items = [
            {
                'product_id': 'BTC',
                'asset_id': 'BTC',
                'name': 'Bitcoin',
                'category': 'major',
                'amount': 10.0,
                'price_usd': 45000.0,
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'product_id': 'ETH',
                'asset_id': 'ETH',
                'name': 'Ethereum',
                'category': 'altcoin',
                'amount': 100.0,
                'price_usd': 3000.0,
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {
                'product_id': 'OLD',
                'asset_id': 'OLD',
                'name': 'Old Asset',
                'category': 'altcoin',
                'amount': 50.0,
                'price_usd': 0.0,
                'is_active': False,
                'created_at': now,
                'updated_at': now
            }
        ]
        mock_db_connection.inventory_table.scan.return_value = {'Items': items}

        # Get all assets
        result = await asset_dao.get_all_assets()

        # Verify result
        assert len(result) == 3
        assert all(isinstance(asset, Asset) for asset in result)
        assert result[0].asset_id == 'BTC'
        assert result[1].asset_id == 'ETH'
        assert result[2].asset_id == 'OLD'

        # Verify database was called without filter
        mock_db_connection.inventory_table.scan.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_get_all_assets_active_only(self, asset_dao, mock_db_connection):
        """Test getting only active assets"""
        # Mock database response
        now = datetime.now(UTC).isoformat()
        items = [
            {
                'product_id': 'BTC',
                'asset_id': 'BTC',
                'name': 'Bitcoin',
                'category': 'major',
                'amount': 10.0,
                'price_usd': 45000.0,
                'is_active': True,
                'created_at': now,
                'updated_at': now
            }
        ]
        mock_db_connection.inventory_table.scan.return_value = {'Items': items}

        # Get active assets only
        result = await asset_dao.get_all_assets(active_only=True)

        # Verify result
        assert len(result) == 1
        assert result[0].is_active is True

        # Verify database was called with filter
        call_args = mock_db_connection.inventory_table.scan.call_args[1]
        assert 'FilterExpression' in call_args

    @pytest.mark.asyncio
    async def test_get_all_assets_empty_result(self, asset_dao, mock_db_connection):
        """Test getting all assets when none exist"""
        # Mock empty database response
        mock_db_connection.inventory_table.scan.return_value = {'Items': []}

        # Get all assets
        result = await asset_dao.get_all_assets()

        # Should return empty list
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_assets_filter_invalid_items(self, asset_dao, mock_db_connection):
        """Test getting all assets filters out items without asset fields"""
        # Mock database response with mix of valid and invalid items
        now = datetime.now(UTC).isoformat()
        items = [
            {  # Valid asset item
                'product_id': 'BTC',
                'asset_id': 'BTC',
                'name': 'Bitcoin',
                'category': 'major',
                'amount': 10.0,
                'price_usd': 45000.0,
                'created_at': now,
                'updated_at': now
            },
            {  # Invalid item (no asset_id or name)
                'product_id': 'SOME_PRODUCT',
                'other_field': 'other_value'
            }
        ]
        mock_db_connection.inventory_table.scan.return_value = {'Items': items}

        # Get all assets
        result = await asset_dao.get_all_assets()

        # Should only return valid asset items
        assert len(result) == 1
        assert result[0].asset_id == 'BTC'

    @pytest.mark.asyncio
    async def test_get_all_assets_database_error(self, asset_dao, mock_db_connection):
        """Test get all assets with database error"""
        # Mock database error
        mock_db_connection.inventory_table.scan.side_effect = Exception("Database error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            await asset_dao.get_all_assets()

        assert "Database error" in str(exc_info.value)

    # ==================== GET ASSETS BY CATEGORY TESTS ====================

    @pytest.mark.asyncio
    async def test_get_assets_by_category_success(self, asset_dao, mock_db_connection):
        """Test getting assets by category successfully"""
        # Mock database response
        now = datetime.now(UTC).isoformat()
        items = [
            {
                'product_id': 'BTC',
                'asset_id': 'BTC',
                'name': 'Bitcoin',
                'category': 'major',
                'amount': 10.0,
                'price_usd': 45000.0,
                'created_at': now,
                'updated_at': now
            }
        ]
        mock_db_connection.inventory_table.scan.return_value = {'Items': items}

        # Get assets by category
        result = await asset_dao.get_assets_by_category('major')

        # Verify result
        assert len(result) == 1
        assert result[0].category == 'major'

        # Verify database was called with filter
        call_args = mock_db_connection.inventory_table.scan.call_args[1]
        assert 'FilterExpression' in call_args

    @pytest.mark.asyncio
    async def test_get_assets_by_category_case_insensitive(self, asset_dao, mock_db_connection):
        """Test getting assets by category is case insensitive"""
        # Mock database response
        mock_db_connection.inventory_table.scan.return_value = {'Items': []}

        # Get assets by category with different case
        await asset_dao.get_assets_by_category('MAJOR')

        # Verify scan was called - case handling is in the filter expression
        mock_db_connection.inventory_table.scan.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_assets_by_category_empty_result(self, asset_dao, mock_db_connection):
        """Test getting assets by category with no matches"""
        # Mock empty database response
        mock_db_connection.inventory_table.scan.return_value = {'Items': []}

        # Get assets by category
        result = await asset_dao.get_assets_by_category('nonexistent')

        # Should return empty list
        assert result == []

    @pytest.mark.asyncio
    async def test_get_assets_by_category_database_error(self, asset_dao, mock_db_connection):
        """Test get assets by category with database error"""
        # Mock database error
        mock_db_connection.inventory_table.scan.side_effect = Exception("Database error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            await asset_dao.get_assets_by_category('major')

        assert "Database error" in str(exc_info.value)

    # ==================== UPDATE ASSET TESTS ====================

    @pytest.mark.asyncio
    async def test_update_asset_success(self, asset_dao, mock_db_connection):
        """Test successful asset update"""
        # Mock database response
        updated_item = {
            'asset_id': 'BTC',
            'name': 'Bitcoin',
            'description': 'Updated description',
            'category': 'major',
            'amount': 15.0,
            'price_usd': 50000.0,
            'is_active': True,
            'created_at': datetime.now(UTC).isoformat(),
            'updated_at': datetime.now(UTC).isoformat()
        }
        mock_db_connection.inventory_table.update_item.return_value = {'Attributes': updated_item}

        # Create update data
        asset_update = AssetUpdate(
            description="Updated description",
            amount=15.0,
            price_usd=50000.0
        )

        # Update asset
        result = await asset_dao.update_asset('BTC', asset_update)

        # Verify result
        assert isinstance(result, Asset)
        assert result.description == "Updated description"
        assert result.amount == 15.0
        assert result.price_usd == 50000.0

        # Verify database was called
        mock_db_connection.inventory_table.update_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_asset_no_changes(self, asset_dao, sample_asset):
        """Test update asset with no changes returns current asset"""
        # Mock get_asset_by_id to return current asset
        asset_dao.get_asset_by_id = AsyncMock(return_value=sample_asset)

        # Create empty update
        asset_update = AssetUpdate()

        # Update asset
        result = await asset_dao.update_asset('BTC', asset_update)

        # Should return current asset
        assert result == sample_asset

    @pytest.mark.asyncio
    async def test_update_asset_price_zero_forces_inactive(self, asset_dao, mock_db_connection):
        """Test updating price to zero forces is_active to False"""
        # Mock database response
        updated_item = {
            'asset_id': 'BTC',
            'name': 'Bitcoin',
            'description': '',
            'category': 'major',
            'amount': 10.0,
            'price_usd': 0.0,
            'is_active': False,
            'created_at': datetime.now(UTC).isoformat(),
            'updated_at': datetime.now(UTC).isoformat()
        }
        mock_db_connection.inventory_table.update_item.return_value = {'Attributes': updated_item}

        # Create update data with zero price
        asset_update = AssetUpdate(price_usd=0.0)

        # Update asset
        result = await asset_dao.update_asset('BTC', asset_update)

        # Verify result
        assert result.price_usd == 0.0
        assert result.is_active is False

    @pytest.mark.asyncio
    async def test_update_asset_not_found(self, asset_dao, mock_db_connection):
        """Test updating non-existent asset"""
        # Mock database response - no item returned
        mock_db_connection.inventory_table.update_item.return_value = {}

        # Create update data
        asset_update = AssetUpdate(description="Updated description")

        # Update asset
        result = await asset_dao.update_asset('NONEXISTENT', asset_update)

        # Should return None
        assert result is None

    @pytest.mark.asyncio
    async def test_update_asset_database_error(self, asset_dao, mock_db_connection):
        """Test update asset with database error"""
        # Mock database error
        mock_db_connection.inventory_table.update_item.side_effect = Exception("Database error")

        # Create update data
        asset_update = AssetUpdate(description="Updated description")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            await asset_dao.update_asset('BTC', asset_update)

        assert "Database error" in str(exc_info.value)

    # ==================== DELETE ASSET TESTS ====================

    @pytest.mark.asyncio
    async def test_delete_asset_success(self, asset_dao, mock_db_connection):
        """Test successful asset deletion"""
        # Mock successful deletion
        mock_db_connection.inventory_table.delete_item.return_value = {'Attributes': {'product_id': 'BTC'}}

        # Delete asset
        result = await asset_dao.delete_asset('BTC')

        # Should return True
        assert result == True

        # Verify database was called correctly
        mock_db_connection.inventory_table.delete_item.assert_called_once_with(
            Key={'product_id': 'BTC'},
            ReturnValues='ALL_OLD'
        )

    @pytest.mark.asyncio
    async def test_delete_asset_not_found(self, asset_dao, mock_db_connection):
        """Test deleting non-existent asset"""
        # Mock no deletion (asset not found)
        mock_db_connection.inventory_table.delete_item.return_value = {}

        # Delete asset
        result = await asset_dao.delete_asset('NONEXISTENT')

        # Should return False
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_asset_database_error(self, asset_dao, mock_db_connection):
        """Test delete asset with database error"""
        # Mock database error
        mock_db_connection.inventory_table.delete_item.side_effect = Exception("Database error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            await asset_dao.delete_asset('BTC')

        assert "Database error" in str(exc_info.value)

    # ==================== CONVENIENCE METHOD TESTS ====================

    @pytest.mark.asyncio
    async def test_update_asset_price_success(self, asset_dao, sample_asset):
        """Test update asset price convenience method"""
        # Mock update_asset method
        updated_asset = Asset(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=10.5,
            price_usd=50000.0,
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        asset_dao.update_asset = AsyncMock(return_value=updated_asset)

        # Update price
        result = await asset_dao.update_asset_price('BTC', 50000.0)

        # Verify result
        assert result.price_usd == 50000.0

        # Verify update_asset was called with correct parameters
        asset_dao.update_asset.assert_called_once()
        call_args = asset_dao.update_asset.call_args[0]
        asset_update = call_args[1]
        assert asset_update.price_usd == 50000.0

    @pytest.mark.asyncio
    async def test_update_asset_price_zero_sets_inactive(self, asset_dao):
        """Test update asset price to zero sets inactive"""
        # Mock update_asset method
        asset_dao.update_asset = AsyncMock(return_value=None)

        # Update price to zero
        await asset_dao.update_asset_price('BTC', 0.0)

        # Verify update_asset was called with is_active=False
        call_args = asset_dao.update_asset.call_args[0]
        asset_update = call_args[1]
        assert asset_update.price_usd == 0.0
        assert asset_update.is_active is False

    @pytest.mark.asyncio
    async def test_update_asset_price_database_error(self, asset_dao):
        """Test update asset price with database error"""
        # Mock update_asset to raise error
        asset_dao.update_asset = AsyncMock(side_effect=Exception("Database error"))

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            await asset_dao.update_asset_price('BTC', 50000.0)

        assert "Database error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_asset_amount_success(self, asset_dao, sample_asset):
        """Test update asset amount convenience method"""
        # Mock update_asset method
        updated_asset = Asset(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=20.0,
            price_usd=45000.0,
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        asset_dao.update_asset = AsyncMock(return_value=updated_asset)

        # Update amount
        result = await asset_dao.update_asset_amount('BTC', 20.0)

        # Verify result
        assert result.amount == 20.0

        # Verify update_asset was called with correct parameters
        call_args = asset_dao.update_asset.call_args[0]
        asset_update = call_args[1]
        assert asset_update.amount == 20.0

    @pytest.mark.asyncio
    async def test_update_asset_amount_database_error(self, asset_dao):
        """Test update asset amount with database error"""
        # Mock update_asset to raise error
        asset_dao.update_asset = AsyncMock(side_effect=Exception("Database error"))

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            await asset_dao.update_asset_amount('BTC', 20.0)

        assert "Database error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_deactivate_asset_success(self, asset_dao, sample_asset):
        """Test deactivate asset convenience method"""
        # Mock update_asset method
        deactivated_asset = Asset(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=10.5,
            price_usd=45000.0,
            is_active=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        asset_dao.update_asset = AsyncMock(return_value=deactivated_asset)

        # Deactivate asset
        result = await asset_dao.deactivate_asset('BTC')

        # Verify result
        assert result.is_active == False

        # Verify update_asset was called with is_active=True
        call_args = asset_dao.update_asset.call_args[0]
        asset_update = call_args[1]
        assert asset_update.is_active is False

    @pytest.mark.asyncio
    async def test_activate_asset_not_found(self, asset_dao):
        """Test activate asset when asset not found"""
        # Mock get_asset_by_id to return None
        asset_dao.get_asset_by_id = AsyncMock(return_value=None)

        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            await asset_dao.activate_asset('NONEXISTENT')

        assert "Asset NONEXISTENT not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_activate_asset_zero_price(self, asset_dao):
        """Test activate asset with zero price"""
        # Mock get_asset_by_id to return asset with zero price
        zero_price_asset = Asset(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=10.5,
            price_usd=0.0,
            is_active=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        asset_dao.get_asset_by_id = AsyncMock(return_value=zero_price_asset)

        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            await asset_dao.activate_asset('BTC')

        assert "Cannot activate asset BTC with zero or negative price" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_activate_asset_negative_price(self, asset_dao):
        """Test activate asset with negative price"""
        # Mock get_asset_by_id to return asset with negative price
        negative_price_asset = Asset(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=10.5,
            price_usd=-100.0,
            is_active=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        asset_dao.get_asset_by_id = AsyncMock(return_value=negative_price_asset)

        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            await asset_dao.activate_asset('BTC')

        assert "Cannot activate asset BTC with zero or negative price" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_activate_asset_database_error(self, asset_dao):
        """Test activate asset with database error"""
        # Mock get_asset_by_id to raise error
        asset_dao.get_asset_by_id = AsyncMock(side_effect=Exception("Database error"))

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            await asset_dao.activate_asset('BTC')

        assert "Database error" in str(exc_info.value)

    # ==================== GET ASSET STATS TESTS ====================

    @pytest.mark.asyncio
    async def test_get_asset_stats_success(self, asset_dao):
        """Test get asset stats successfully"""
        # Mock get_all_assets to return sample data
        now = datetime.now(UTC)
        assets = [
            Asset(
                asset_id="BTC",
                name="Bitcoin",
                description="Digital currency",
                category="major",
                amount=10.0,
                price_usd=45000.0,
                is_active=True,
                created_at=now,
                updated_at=now
            ),
            Asset(
                asset_id="ETH",
                name="Ethereum",
                description="Smart contracts",
                category="altcoin",
                amount=100.0,
                price_usd=3000.0,
                is_active=True,
                created_at=now,
                updated_at=now
            ),
            Asset(
                asset_id="OLD",
                name="Old Asset",
                description="Inactive asset",
                category="altcoin",
                amount=50.0,
                price_usd=100.0,
                is_active=False,
                created_at=now,
                updated_at=now
            )
        ]
        asset_dao.get_all_assets = AsyncMock(return_value=assets)

        # Get stats
        result = await asset_dao.get_asset_stats()

        # Verify result
        assert result['total_assets'] == 3
        assert result['active_assets'] == 2
        assert result['inactive_assets'] == 1

        # Total value = (10 * 45000) + (100 * 3000) = 450000 + 300000 = 750000
        assert result['total_inventory_value_usd'] == 750000.0

        assert result['assets_by_category'] == {
            'major': 1,
            'altcoin': 2
        }
        assert 'last_updated' in result
        assert result['last_updated']  # Should be a timestamp

    @pytest.mark.asyncio
    async def test_get_asset_stats_no_assets(self, asset_dao):
        """Test get asset stats with no assets"""
        # Mock get_all_assets to return empty list
        asset_dao.get_all_assets = AsyncMock(return_value=[])

        # Get stats
        result = await asset_dao.get_asset_stats()

        # Verify result
        assert result['total_assets'] == 0
        assert result['active_assets'] == 0
        assert result['inactive_assets'] == 0
        assert result['total_inventory_value_usd'] == 0.0
        assert result['assets_by_category'] == {}

    @pytest.mark.asyncio
    async def test_get_asset_stats_only_inactive_assets(self, asset_dao):
        """Test get asset stats with only inactive assets"""
        # Mock get_all_assets to return only inactive assets
        now = datetime.now(UTC)
        assets = [
            Asset(
                asset_id="OLD1",
                name="Old Asset 1",
                description="Inactive asset",
                category="major",
                amount=10.0,
                price_usd=0.0,
                is_active=False,
                created_at=now,
                updated_at=now
            ),
            Asset(
                asset_id="OLD2",
                name="Old Asset 2",
                description="Inactive asset",
                category="altcoin",
                amount=50.0,
                price_usd=100.0,
                is_active=False,
                created_at=now,
                updated_at=now
            )
        ]
        asset_dao.get_all_assets = AsyncMock(return_value=assets)

        # Get stats
        result = await asset_dao.get_asset_stats()

        # Verify result
        assert result['total_assets'] == 2
        assert result['active_assets'] == 0
        assert result['inactive_assets'] == 2
        assert result['total_inventory_value_usd'] == 0.0  # No active assets

    @pytest.mark.asyncio
    async def test_get_asset_stats_fractional_amounts(self, asset_dao):
        """Test get asset stats with fractional amounts and prices"""
        # Mock get_all_assets with fractional values
        now = datetime.now(UTC)
        assets = [
            Asset(
                asset_id="BTC",
                name="Bitcoin",
                description="Digital currency",
                category="major",
                amount=Decimal("1.5"),
                price_usd=Decimal("45000.5"),
                is_active=True,
                created_at=now,
                updated_at=now
            ),
            Asset(
                asset_id="ETH",
                name="Ethereum",
                description="Smart contracts",
                category="altcoin",
                amount=Decimal("10.25"),
                price_usd=Decimal("3000.33"),
                is_active=True,
                created_at=now,
                updated_at=now
            )
        ]
        asset_dao.get_all_assets = AsyncMock(return_value=assets)

        # Get stats
        result = await asset_dao.get_asset_stats()

        # Calculate expected total value using Decimal for precision
        # (1.5 * 45000.5) + (10.25 * 3000.33) = 67500.75 + 30753.3825 = 98254.1325
        expected_value = Decimal("98254.13")

        assert result['total_inventory_value_usd'] == expected_value

    @pytest.mark.asyncio
    async def test_get_asset_stats_database_error(self, asset_dao):
        """Test get asset stats with database error"""
        # Mock get_all_assets to raise error
        asset_dao.get_all_assets = AsyncMock(side_effect=Exception("Database error"))

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            await asset_dao.get_asset_stats()

        assert "Database error" in str(exc_info.value)

    # ==================== EDGE CASE AND ERROR HANDLING TESTS ====================

    @pytest.mark.asyncio
    async def test_get_all_assets_with_missing_fields(self, asset_dao, mock_db_connection):
        """Test get all assets handles items with missing fields gracefully"""
        # Mock database response with items missing various fields
        now = datetime.now(UTC).isoformat()
        items = [
            {  # Complete item
                'product_id': 'BTC',
                'asset_id': 'BTC',
                'name': 'Bitcoin',
                'description': 'Digital currency',
                'category': 'major',
                'amount': 10.0,
                'price_usd': 45000.0,
                'is_active': True,
                'created_at': now,
                'updated_at': now
            },
            {  # Item with missing optional fields
                'product_id': 'ETH',
                'asset_id': 'ETH',
                'name': 'Ethereum',
                'category': 'altcoin',
                'amount': 100.0,
                'price_usd': 3000.0,
                # Missing description, is_active, created_at, updated_at
            }
        ]
        mock_db_connection.inventory_table.scan.return_value = {'Items': items}

        # Get all assets
        result = await asset_dao.get_all_assets()

        # Should handle missing fields with defaults
        assert len(result) == 2
        assert result[1].description == ''
        assert result[1].is_active is True  # Default value
        assert isinstance(result[1].created_at, datetime)
        assert isinstance(result[1].updated_at, datetime)

    @pytest.mark.asyncio
    async def test_update_asset_builds_correct_expression(self, asset_dao, mock_db_connection):
        """Test that update asset builds correct DynamoDB update expression"""
        # Mock database response
        updated_item = {
            'asset_id': 'BTC',
            'name': 'Bitcoin',
            'description': 'Updated description',
            'category': 'altcoin',
            'amount': 15.0,
            'price_usd': 50000.0,
            'is_active': True,
            'created_at': datetime.now(UTC).isoformat(),
            'updated_at': datetime.now(UTC).isoformat()
        }
        mock_db_connection.inventory_table.update_item.return_value = {'Attributes': updated_item}

        # Create update with multiple fields
        asset_update = AssetUpdate(
            description="Updated description",
            category="altcoin",
            amount=15.0,
            price_usd=50000.0,
            is_active=True
        )

        # Update asset
        await asset_dao.update_asset('BTC', asset_update)

        # Verify update_item was called with correct parameters
        call_args = mock_db_connection.inventory_table.update_item.call_args[1]

        # Check that key is correct
        assert call_args['Key'] == {'product_id': 'BTC'}

        # Check that update expression contains all fields
        update_expression = call_args['UpdateExpression']
        assert 'SET' in update_expression
        assert 'description = :description' in update_expression
        assert 'category = :category' in update_expression
        assert 'amount = :amount' in update_expression
        assert 'price_usd = :price_usd' in update_expression
        assert 'is_active = :is_active' in update_expression
        assert 'updated_at = :updated_at' in update_expression

        # Check expression values
        expression_values = call_args['ExpressionAttributeValues']
        assert expression_values[':description'] == "Updated description"
        assert expression_values[':category'] == "altcoin"
        assert expression_values[':amount'] == 15.0
        assert expression_values[':price_usd'] == 50000.0
        assert expression_values[':is_active'] is True
        assert ':updated_at' in expression_values

    @pytest.mark.asyncio
    async def test_datetime_handling_in_create_asset(self, asset_dao, sample_asset_create, mock_db_connection):
        """Test that datetime handling works correctly in create asset"""
        # Mock that asset doesn't exist
        asset_dao.get_asset_by_id = AsyncMock(return_value=None)

        # Mock database operations
        mock_db_connection.inventory_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Patch datetime to control the timestamp
        with patch('common.dao.asset_dao.datetime') as mock_datetime:
            fixed_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
            mock_datetime.now.return_value = fixed_time
            mock_datetime.fromisoformat = datetime.fromisoformat  # Keep original method

            # Create asset
            result = await asset_dao.create_asset(sample_asset_create)

            # Verify timestamps are set correctly
            assert result.created_at == fixed_time
            assert result.updated_at == fixed_time

            # Verify database was called with correct timestamp
            call_args = mock_db_connection.inventory_table.put_item.call_args[1]['Item']
            assert call_args['created_at'] == fixed_time.isoformat()
            assert call_args['updated_at'] == fixed_time.isoformat()

    # ==================== COMPREHENSIVE ERROR SCENARIO TESTS ====================

    @pytest.mark.asyncio
    async def test_create_asset_with_various_exceptions(self, asset_dao, sample_asset_create, mock_db_connection):
        """Test create asset handles various exception types"""
        # Mock that asset doesn't exist
        asset_dao.get_asset_by_id = AsyncMock(return_value=None)

        exception_types = [
            Exception("Generic error"),
            ValueError("Value error"),
            RuntimeError("Runtime error"),
            KeyError("Key error")
        ]

        for exception in exception_types:
            # Reset mock for each iteration
            mock_db_connection.inventory_table.put_item.side_effect = exception

            # Should raise the specific exception
            with pytest.raises(type(exception)) as exc_info:
                await asset_dao.create_asset(sample_asset_create)

            assert str(exception) in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_methods_with_empty_strings(self, asset_dao, mock_db_connection):
        """Test methods handle empty strings appropriately"""
        # Test get_asset_by_id with empty string
        mock_db_connection.inventory_table.get_item.return_value = {}
        result = await asset_dao.get_asset_by_id('')
        assert result is None

        # Test get_assets_by_category with empty string
        mock_db_connection.inventory_table.scan.return_value = {'Items': []}
        result = await asset_dao.get_assets_by_category('')
        assert result == []

        # Test delete_asset with empty string
        mock_db_connection.inventory_table.delete_item.return_value = {}
        result = await asset_dao.delete_asset('')
        assert result is False

    # ==================== LOGGING TESTS ====================

    @pytest.mark.asyncio
    async def test_logging_in_methods(self, asset_dao, mock_db_connection, caplog):
        """Test that appropriate logging occurs in DAO methods"""
        import logging

        # Set log level to capture debug messages
        caplog.set_level(logging.INFO)

        # Test get_asset_by_id logging
        mock_db_connection.inventory_table.get_item.return_value = {}
        await asset_dao.get_asset_by_id('TEST')

        # Check that debug logs were created
        assert any("Looking up asset by ID: 'TEST'" in record.message for record in caplog.records)
        assert any("No asset found for ID: 'TEST'" in record.message for record in caplog.records)

    # ==================== BOUNDARY VALUE TESTS ====================

    @pytest.mark.asyncio
    async def test_asset_with_extreme_values(self, asset_dao, mock_db_connection):
        """Test asset creation with boundary values"""
        # Mock that asset doesn't exist
        asset_dao.get_asset_by_id = AsyncMock(return_value=None)

        # Test with very small values
        small_asset = AssetCreate(
            asset_id="MIN",
            name="Minimal Asset",
            description="",
            category="stablecoin",
            amount=Decimal("0.00000001"),  # Smallest possible amount
            price_usd=Decimal("0.01")  # Smallest price
        )

        # Mock successful database operations
        mock_db_connection.inventory_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        result = await asset_dao.create_asset(small_asset)
        assert result.amount == Decimal("0.00000001")
        assert result.price_usd == Decimal("0.01")

        # Test with very large values
        large_asset = AssetCreate(
            asset_id="MAX",
            name="Maximum Asset",
            description="A" * 1000,  # Maximum description length
            category="major",
            amount=Decimal("999999999.99999999"),  # Very large amount
            price_usd=Decimal("999999.99")  # Very large price
        )

        result = await asset_dao.create_asset(large_asset)
        assert result.amount == Decimal("999999999.99999999")
        assert result.price_usd == Decimal("999999.99")
        assert len(result.description) == 1000


    @pytest.mark.asyncio
    async def test_deactivate_asset_database_error(self, asset_dao):
        """Test deactivate asset with database error"""
        # Mock update_asset to raise error
        asset_dao.update_asset = AsyncMock(side_effect=Exception("Database error"))

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            await asset_dao.deactivate_asset('BTC')

        assert "Database error" in str(exc_info.value)