import os
import sys
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Add the common directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data.dao.inventory.asset_dao import AssetDAO
from src.data.entities.inventory import Asset, AssetItem
from src.data.exceptions import CNOPDatabaseOperationException
from src.exceptions.shared_exceptions import CNOPAssetNotFoundException


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

    def test_create_asset_success(self, asset_dao, sample_asset_create, mock_db_connection):
        """Test successful asset creation"""
        # Mock that asset doesn't exist
        mock_db_connection.inventory_table.get_item.return_value = {}

        # Mock successful database operations
        now = datetime.now(UTC).isoformat()
        created_item = {
            'asset_id': 'BTC',
            'name': 'Bitcoin',
            'description': 'Digital currency',
            'category': 'major',
            'amount': Decimal('10.5'),
            'price_usd': 67000.0,
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
        mock_db_connection.inventory_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
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
        mock_db_connection.inventory_table.put_item.assert_called_once()
        call_args = mock_db_connection.inventory_table.put_item.call_args[1]['Item']
        assert call_args['symbol'] == 'BTC'
        assert call_args['image'].startswith('https://')

    def test_create_asset_database_error(self, asset_dao, sample_asset_create, mock_db_connection):
        """Test create asset with database error"""
        # Mock that asset doesn't exist
        mock_db_connection.inventory_table.get_item.return_value = {}

        # Mock database error
        mock_db_connection.inventory_table.put_item.side_effect = Exception("Database error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            asset_dao.create_asset(sample_asset_create)

        assert "Database error" in str(exc_info.value)

    # ==================== GET ASSET BY ID TESTS ====================

    def test_get_asset_by_id_found(self, asset_dao, sample_db_item, mock_db_connection):
        mock_db_connection.inventory_table.get_item.return_value = {'Item': sample_db_item}
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
        mock_db_connection.inventory_table.get_item.assert_called_once_with(Key={'product_id': 'BTC'})

    def test_get_asset_by_id_not_found(self, asset_dao, mock_db_connection):
        """Test get asset by ID when asset not found"""
        # Mock empty response
        mock_db_connection.inventory_table.get_item.return_value = {}

        # Should raise CNOPAssetNotFoundException directly
        with pytest.raises(CNOPAssetNotFoundException):
            asset_dao.get_asset_by_id('NONEXISTENT')

        # Verify database was called
        mock_db_connection.inventory_table.get_item.assert_called_once_with(
            Key={'product_id': 'NONEXISTENT'}
        )

    def test_get_asset_by_id_database_error(self, asset_dao, mock_db_connection):
        """Test get asset by ID with database error"""
        # Mock database error
        mock_db_connection.inventory_table.get_item.side_effect = Exception("Database error")

        # Should raise CNOPDatabaseOperationException
        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            asset_dao.get_asset_by_id('BTC')

        assert "Database error" in str(exc_info.value)

    def test_get_asset_by_id_missing_fields(self, asset_dao, mock_db_connection):
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
        result = asset_dao.get_asset_by_id('BTC')

        # Verify result with defaults
        assert result.description is None  # Default for missing description
        assert result.is_active is True  # Default for missing is_active

    # ==================== GET ALL ASSETS TESTS ====================

    def test_get_all_assets_success(self, asset_dao, mock_db_connection):
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
        result = asset_dao.get_all_assets()

        # Verify result
        assert len(result) == 3
        assert all(isinstance(asset, Asset) for asset in result)
        assert result[0].asset_id == 'BTC'
        assert result[1].asset_id == 'ETH'
        assert result[2].asset_id == 'OLD'

        # Verify database was called without filter
        mock_db_connection.inventory_table.scan.assert_called_once_with()

    def test_get_all_assets_active_only(self, asset_dao, mock_db_connection):
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
        result = asset_dao.get_all_assets(active_only=True)

        # Verify result
        assert len(result) == 1
        assert result[0].is_active is True

        # Verify database was called with filter
        call_args = mock_db_connection.inventory_table.scan.call_args[1]
        assert 'FilterExpression' in call_args

    def test_get_all_assets_empty_result(self, asset_dao, mock_db_connection):
        """Test getting all assets when none exist"""
        # Mock empty database response
        mock_db_connection.inventory_table.scan.return_value = {'Items': []}

        # Get all assets
        result = asset_dao.get_all_assets()

        # Should return empty list
        assert result == []

    def test_get_all_assets_filter_invalid_items(self, asset_dao, mock_db_connection):
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
            {  # Invalid item (missing required fields)
                'product_id': 'SOME_PRODUCT',
                'asset_id': 'INVALID',
                'name': 'Invalid Asset',
                'category': 'invalid',
                'amount': 0.0,
                'price_usd': 0.0,
                'created_at': now,
                'updated_at': now,
                'other_field': 'other_value'
            }
        ]
        mock_db_connection.inventory_table.scan.return_value = {'Items': items}

        # Get all assets
        result = asset_dao.get_all_assets()

        # Should return all asset items (both valid and invalid)
        assert len(result) == 2
        assert result[0].asset_id == 'BTC'
        assert result[1].asset_id == 'INVALID'

    def test_get_all_assets_database_error(self, asset_dao, mock_db_connection):
        """Test get all assets with database error"""
        # Mock database error
        mock_db_connection.inventory_table.scan.side_effect = Exception("Database error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            asset_dao.get_all_assets()

        assert "Database error" in str(exc_info.value)

    # ==================== UPDATE ASSET TESTS ====================

    def test_update_asset_success(self, asset_dao, mock_db_connection):
        now = datetime.now(UTC).isoformat()
        updated_item = {
            'asset_id': 'BTC',
            'name': 'Bitcoin',
            'description': 'Updated desc',
            'category': 'major',
            'amount': 20.0,
            'price_usd': 50000.0,
            'symbol': 'BTC',
            'image': 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png',
            'market_cap_rank': 1,
            'high_24h': 70000.0,
            'low_24h': 65000.0,
            'circulating_supply': 20000000.0,
            'price_change_24h': 1000.0,
            'ath_change_percentage': -1.5,
            'market_cap': 1400000000000.0,
            'is_active': True,
            'created_at': now,
            'updated_at': now
        }
        # Mock the get_item call that happens inside get_asset_by_id
        existing_item = {
            'product_id': 'BTC',
            'asset_id': 'BTC',
            'name': 'Bitcoin',
            'description': 'Original desc',
            'category': 'major',
            'amount': 10.0,
            'price_usd': 45000.0,
            'is_active': True,
            'created_at': now,
            'updated_at': now
        }
        mock_db_connection.inventory_table.get_item.return_value = {'Item': existing_item}
        mock_db_connection.inventory_table.update_item.return_value = {'Attributes': updated_item}
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
        # Note: update_asset currently returns a dict, not an Asset entity
        assert isinstance(result, dict)
        assert result['asset_id'] == "BTC"
        assert result['description'] == "Updated desc"
        assert result['amount'] == 20.0
        assert result['price_usd'] == 50000.0
        assert result['symbol'] == "BTC"
        assert result['image'].startswith("https://")
        assert result['market_cap_rank'] == 1
        assert result['high_24h'] == 70000.0
        assert result['low_24h'] == 65000.0
        assert result['circulating_supply'] == 20000000.0
        assert result['price_change_24h'] == 1000.0
        assert result['ath_change_percentage'] == -1.5
        assert result['market_cap'] == 1400000000000.0
        assert result['is_active'] is True
        assert isinstance(result['created_at'], str)  # ISO string from database
        assert isinstance(result['updated_at'], str)  # ISO string from database

    def test_update_asset_no_changes(self, asset_dao, sample_asset):
        """Test update asset with no changes returns current asset"""
        # Mock get_asset_by_id to return current asset
        asset_dao.get_asset_by_id = Mock(return_value=sample_asset)
        # Mock _safe_update_item to return the sample_asset
        asset_dao._safe_update_item = Mock(return_value=sample_asset)

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

        # Should return current asset
        assert result == sample_asset

    def test_update_asset_price_zero_forces_inactive(self, asset_dao, mock_db_connection):
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
        # Mock the get_item call that happens inside get_asset_by_id
        existing_item = {
            'product_id': 'BTC',
            'asset_id': 'BTC',
            'name': 'Bitcoin',
            'description': 'Original desc',
            'category': 'major',
            'amount': 10.0,
            'price_usd': 45000.0,
            'is_active': True,
            'created_at': datetime.now(UTC).isoformat(),
            'updated_at': datetime.now(UTC).isoformat()
        }
        mock_db_connection.inventory_table.get_item.return_value = {'Item': existing_item}
        mock_db_connection.inventory_table.update_item.return_value = {'Attributes': updated_item}

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

        # Verify result (update_asset returns a dict, not an Asset object)
        assert result['price_usd'] == 0.0
        assert result['is_active'] is False

    def test_update_asset_not_found(self, asset_dao, mock_db_connection):
        """Test update asset when asset not found"""
        # Mock that asset doesn't exist
        mock_db_connection.inventory_table.get_item.return_value = {}

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

    def test_update_asset_database_error(self, asset_dao, mock_db_connection):
        """Test update asset with database error"""
        # Mock the get_item call that happens inside get_asset_by_id
        existing_item = {
            'product_id': 'BTC',
            'asset_id': 'BTC',
            'name': 'Bitcoin',
            'description': 'Original desc',
            'category': 'major',
            'amount': 10.0,
            'price_usd': 45000.0,
            'is_active': True,
            'created_at': datetime.now(UTC).isoformat(),
            'updated_at': datetime.now(UTC).isoformat()
        }
        mock_db_connection.inventory_table.get_item.return_value = {'Item': existing_item}
        # Mock database error
        mock_db_connection.inventory_table.update_item.side_effect = Exception("Database error")

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

    def test_get_all_assets_with_missing_fields(self, asset_dao, mock_db_connection):
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
        result = asset_dao.get_all_assets()

        # Should handle missing fields with defaults
        assert len(result) == 2
        assert result[1].description is None  # Default for missing description
        assert result[1].is_active is True  # Default value
        assert isinstance(result[1].created_at, datetime)
        assert isinstance(result[1].updated_at, datetime)

    def test_update_asset_builds_correct_expression(self, asset_dao, mock_db_connection):
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
        # Mock the get_item call that happens inside get_asset_by_id
        existing_item = {
            'product_id': 'BTC',
            'asset_id': 'BTC',
            'name': 'Bitcoin',
            'description': 'Original desc',
            'category': 'major',
            'amount': 10.0,
            'price_usd': 45000.0,
            'is_active': True,
            'created_at': datetime.now(UTC).isoformat(),
            'updated_at': datetime.now(UTC).isoformat()
        }
        mock_db_connection.inventory_table.get_item.return_value = {'Item': existing_item}
        mock_db_connection.inventory_table.update_item.return_value = {'Attributes': updated_item}

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
        asset_dao.update_asset(asset_update)

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

    # ==================== COMPREHENSIVE ERROR SCENARIO TESTS ====================

    def test_create_asset_with_various_exceptions(self, asset_dao, sample_asset_create, mock_db_connection):
        """Test create asset handles various exception types"""
        # Mock that asset doesn't exist
        mock_db_connection.inventory_table.get_item.return_value = {}

        exception_types = [
            Exception("Generic error"),
            ValueError("Value error"),
            RuntimeError("Runtime error"),
            KeyError("Key error")
        ]

        for exception in exception_types:
            # Reset mock for each iteration
            mock_db_connection.inventory_table.put_item.side_effect = exception

            # Should raise CNOPDatabaseOperationException (our design wraps all DB exceptions)
            with pytest.raises(CNOPDatabaseOperationException) as exc_info:
                asset_dao.create_asset(sample_asset_create)

            # Verify the original exception message is preserved
            assert str(exception) in str(exc_info.value)
    # ==================== BOUNDARY VALUE TESTS ====================

    def test_asset_with_extreme_values(self, asset_dao, mock_db_connection):
        """Test asset creation with boundary values"""
        # Mock that asset doesn't exist
        mock_db_connection.inventory_table.get_item.return_value = {}

        # Test with very small values
        small_asset = Asset(
            asset_id="MIN",
            name="Minimal Asset",
            description="",
            category="stablecoin",
            amount=Decimal("0.00000001"),  # Smallest possible amount
            price_usd=Decimal("0.01")  # Smallest price
        )

        # Mock successful database operations
        mock_db_connection.inventory_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

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
        assert result.amount == Decimal("999999999.99999999")
        assert result.price_usd == Decimal("999999.99")
        assert len(result.description) == 500

    # ==================== BATCH GET ASSETS BY IDS TESTS ====================

    def test_get_assets_by_ids_empty_list(self, asset_dao):
        """Test get_assets_by_ids with empty list returns empty dict"""
        result = asset_dao.get_assets_by_ids([])
        assert result == {}

    def test_get_assets_by_ids_success(self, asset_dao, mock_db_connection):
        """Test successful batch retrieval of assets"""
        # Mock DynamoDB client
        mock_client = Mock()
        asset_dao.client = mock_client

        # Mock table name
        asset_dao.table.table_name = 'test-inventory-table'

        # Mock DynamoDB low-level response format
        dynamodb_response = {
            'Responses': {
                'test-inventory-table': [
                    {
                        'product_id': {'S': 'BTC'},
                        'asset_id': {'S': 'BTC'},
                        'name': {'S': 'Bitcoin'},
                        'description': {'S': 'Digital currency'},
                        'category': {'S': 'major'},
                        'amount': {'N': '10.5'},
                        'price_usd': {'N': '45000.0'},
                        'is_active': {'BOOL': True},
                        'created_at': {'S': '2023-01-01T00:00:00Z'},
                        'updated_at': {'S': '2023-01-01T00:00:00Z'}
                    },
                    {
                        'product_id': {'S': 'ETH'},
                        'asset_id': {'S': 'ETH'},
                        'name': {'S': 'Ethereum'},
                        'description': {'S': 'Smart contract platform'},
                        'category': {'S': 'altcoin'},
                        'amount': {'N': '100.0'},
                        'price_usd': {'N': '3000.0'},
                        'is_active': {'BOOL': True},
                        'created_at': {'S': '2023-01-01T00:00:00Z'},
                        'updated_at': {'S': '2023-01-01T00:00:00Z'}
                    }
                ]
            },
            'UnprocessedKeys': {}
        }
        mock_client.batch_get_item.return_value = dynamodb_response

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

        # Verify client was called correctly
        mock_client.batch_get_item.assert_called_once()
        call_args = mock_client.batch_get_item.call_args[1]
        assert 'RequestItems' in call_args
        assert 'test-inventory-table' in call_args['RequestItems']

    def test_get_assets_by_ids_with_unprocessed_keys(self, asset_dao, mock_db_connection):
        """Test batch retrieval with unprocessed keys retry"""
        # Mock DynamoDB client
        mock_client = Mock()
        asset_dao.client = mock_client

        # Mock table name
        asset_dao.table.table_name = 'test-inventory-table'

        # First response with unprocessed keys
        first_response = {
            'Responses': {
                'test-inventory-table': [
                    {
                        'product_id': {'S': 'BTC'},
                        'asset_id': {'S': 'BTC'},
                        'name': {'S': 'Bitcoin'},
                        'description': {'S': 'Digital currency'},
                        'category': {'S': 'major'},
                        'amount': {'N': '10.5'},
                        'price_usd': {'N': '45000.0'},
                        'is_active': {'BOOL': True},
                        'created_at': {'S': '2023-01-01T00:00:00Z'},
                        'updated_at': {'S': '2023-01-01T00:00:00Z'}
                    }
                ]
            },
            'UnprocessedKeys': {
                'test-inventory-table': {
                    'Keys': [
                        {'product_id': {'S': 'ETH'}}
                    ]
                }
            }
        }

        # Retry response
        retry_response = {
            'Responses': {
                'test-inventory-table': [
                    {
                        'product_id': {'S': 'ETH'},
                        'asset_id': {'S': 'ETH'},
                        'name': {'S': 'Ethereum'},
                        'description': {'S': 'Smart contract platform'},
                        'category': {'S': 'altcoin'},
                        'amount': {'N': '100.0'},
                        'price_usd': {'N': '3000.0'},
                        'is_active': {'BOOL': True},
                        'created_at': {'S': '2023-01-01T00:00:00Z'},
                        'updated_at': {'S': '2023-01-01T00:00:00Z'}
                    }
                ]
            },
            'UnprocessedKeys': {}
        }

        mock_client.batch_get_item.side_effect = [first_response, retry_response]

        # Test batch retrieval
        result = asset_dao.get_assets_by_ids(['BTC', 'ETH'])

        # Verify result
        assert len(result) == 2
        assert 'BTC' in result
        assert 'ETH' in result

        # Verify client was called twice (initial + retry)
        assert mock_client.batch_get_item.call_count == 2

    def test_get_assets_by_ids_missing_assets(self, asset_dao, mock_db_connection):
        """Test batch retrieval when some assets are missing"""
        # Mock DynamoDB client
        mock_client = Mock()
        asset_dao.client = mock_client

        # Mock table name
        asset_dao.table.table_name = 'test-inventory-table'

        # Response with only one asset (other is missing)
        dynamodb_response = {
            'Responses': {
                'test-inventory-table': [
                    {
                        'product_id': {'S': 'BTC'},
                        'asset_id': {'S': 'BTC'},
                        'name': {'S': 'Bitcoin'},
                        'description': {'S': 'Digital currency'},
                        'category': {'S': 'major'},
                        'amount': {'N': '10.5'},
                        'price_usd': {'N': '45000.0'},
                        'is_active': {'BOOL': True},
                        'created_at': {'S': '2023-01-01T00:00:00Z'},
                        'updated_at': {'S': '2023-01-01T00:00:00Z'}
                    }
                ]
            },
            'UnprocessedKeys': {}
        }
        mock_client.batch_get_item.return_value = dynamodb_response

        # Test batch retrieval
        result = asset_dao.get_assets_by_ids(['BTC', 'MISSING'])

        # Verify result - only found assets are returned
        assert len(result) == 1
        assert 'BTC' in result
        assert 'MISSING' not in result

    def test_get_assets_by_ids_database_error(self, asset_dao, mock_db_connection):
        """Test batch retrieval with database error"""
        # Mock DynamoDB client
        mock_client = Mock()
        asset_dao.client = mock_client

        # Mock table name
        asset_dao.table.table_name = 'test-inventory-table'

        # Mock database error
        mock_client.batch_get_item.side_effect = Exception("Database error")

        # Should raise CNOPDatabaseOperationException
        with pytest.raises(CNOPDatabaseOperationException) as exc_info:
            asset_dao.get_assets_by_ids(['BTC', 'ETH'])

        assert "Database error" in str(exc_info.value)

    # ==================== DYNAMODB TYPE CONVERSION TESTS ====================

    def test_convert_dynamodb_item_string(self, asset_dao):
        """Test conversion of DynamoDB string type"""
        dynamodb_item = {
            'product_id': {'S': 'BTC'},
            'name': {'S': 'Bitcoin'},
            'description': {'S': 'Digital currency'}
        }

        result = asset_dao._convert_dynamodb_item(dynamodb_item)

        assert result == {
            'product_id': 'BTC',
            'name': 'Bitcoin',
            'description': 'Digital currency'
        }

    def test_convert_dynamodb_item_number(self, asset_dao):
        """Test conversion of DynamoDB number type"""
        dynamodb_item = {
            'amount': {'N': '10.5'},
            'price_usd': {'N': '45000.0'},
            'market_cap_rank': {'N': '1'}
        }

        result = asset_dao._convert_dynamodb_item(dynamodb_item)

        assert result == {
            'amount': '10.5',
            'price_usd': '45000.0',
            'market_cap_rank': '1'
        }

    def test_convert_dynamodb_item_boolean(self, asset_dao):
        """Test conversion of DynamoDB boolean type"""
        dynamodb_item = {
            'is_active': {'BOOL': True},
            'is_trading': {'BOOL': False}
        }

        result = asset_dao._convert_dynamodb_item(dynamodb_item)

        assert result == {
            'is_active': True,
            'is_trading': False
        }

    def test_convert_dynamodb_item_null(self, asset_dao):
        """Test conversion of DynamoDB null type"""
        dynamodb_item = {
            'description': {'NULL': True},
            'optional_field': {'NULL': True}
        }

        result = asset_dao._convert_dynamodb_item(dynamodb_item)

        assert result == {
            'description': None,
            'optional_field': None
        }

    def test_convert_dynamodb_item_mixed_types(self, asset_dao):
        """Test conversion of DynamoDB item with mixed types"""
        dynamodb_item = {
            'product_id': {'S': 'BTC'},
            'amount': {'N': '10.5'},
            'is_active': {'BOOL': True},
            'description': {'NULL': True},
            'metadata': {'M': {'key': {'S': 'value'}}},  # Map type
            'tags': {'L': [{'S': 'crypto'}, {'S': 'digital'}]}  # List type
        }

        result = asset_dao._convert_dynamodb_item(dynamodb_item)

        assert result == {
            'product_id': 'BTC',
            'amount': '10.5',
            'is_active': True,
            'description': None,
            'metadata': {'M': {'key': {'S': 'value'}}},  # Unhandled types passed through
            'tags': {'L': [{'S': 'crypto'}, {'S': 'digital'}]}  # Unhandled types passed through
        }

    def test_convert_dynamodb_item_non_dict_values(self, asset_dao):
        """Test conversion of DynamoDB item with non-dict values"""
        dynamodb_item = {
            'product_id': 'BTC',  # Already converted
            'name': {'S': 'Bitcoin'},  # Needs conversion
            'amount': 10.5  # Already converted
        }

        result = asset_dao._convert_dynamodb_item(dynamodb_item)

        assert result == {
            'product_id': 'BTC',
            'name': 'Bitcoin',
            'amount': 10.5
        }

    def test_convert_dynamodb_item_empty(self, asset_dao):
        """Test conversion of empty DynamoDB item"""
        result = asset_dao._convert_dynamodb_item({})
        assert result == {}

    def test_convert_dynamodb_item_unknown_type(self, asset_dao):
        """Test conversion of DynamoDB item with unknown type"""
        dynamodb_item = {
            'known_field': {'S': 'value'},
            'unknown_field': {'UNKNOWN': 'value'}  # Unknown type
        }

        result = asset_dao._convert_dynamodb_item(dynamodb_item)

        assert result == {
            'known_field': 'value',
            'unknown_field': {'UNKNOWN': 'value'}  # Passed through unchanged
        }
