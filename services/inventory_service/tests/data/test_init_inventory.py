"""
Unit tests for init_inventory module
Path: services/inventory-service/tests/data/test_init_inventory.py
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from decimal import Decimal

from common.exceptions import CNOPEntityNotFoundException, CNOPAssetNotFoundException
from common.data.entities.inventory import Asset

from data.init_inventory import (
    get_category,
    coin_to_asset,
    upsert_coins_to_inventory,
    initialize_inventory_data,
    startup_inventory_initialization
)
from services.fetch_coins import CoinData
from constants import DEFAULT_ASSET_CATEGORY, DEFAULT_ASSET_AMOUNT

# Patch paths - only for external dependencies
PATH_GET_DYNAMODB_MANAGER = 'data.init_inventory.get_dynamodb_manager'
PATH_FETCH_COINS = 'services.fetch_coins.fetch_coins'  # Patch at the source, not the import


def create_test_coin(symbol="BTC", name="Bitcoin", price=45000.0):
    """Helper to create test CoinData objects"""
    return CoinData(
        symbol=symbol,
        name=name,
        current_price=price,
        price_usd=price,
        image=f"https://example.com/{symbol.lower()}.png",
        market_cap_rank=1,
        high_24h=price * 1.02,
        low_24h=price * 0.98,
        circulating_supply=Decimal("19000000"),
        total_supply=Decimal("21000000"),
        max_supply=Decimal("21000000"),
        price_change_24h=Decimal("500"),
        price_change_percentage_24h=Decimal("1.1"),
        price_change_percentage_7d=Decimal("5.2"),
        price_change_percentage_30d=Decimal("8.5"),
        market_cap=Decimal("850000000000"),
        market_cap_change_24h=Decimal("10000000000"),
        market_cap_change_percentage_24h=Decimal("1.2"),
        total_volume_24h=Decimal("25000000000"),
        volume_change_24h=Decimal("5000000000"),
        ath=Decimal("69000"),
        ath_change_percentage=Decimal("-34.8"),
        ath_date="2021-11-10T14:24:11.849Z",
        atl=Decimal("67.81"),
        atl_change_percentage=Decimal("66263.0"),
        atl_date="2013-07-06T00:00:00.000Z",
        last_updated="2025-08-30T21:49:33.955Z",
        sparkline_7d={"prices": [44000, 45000, 46000]}
    )


class TestGetCategory:
    """Test the get_category function"""

    def test_get_category_returns_default(self):
        """Test that get_category always returns the default category"""
        # Any coin dict should return the default category
        assert get_category({"id": "bitcoin"}) == DEFAULT_ASSET_CATEGORY
        assert get_category({"id": "ethereum"}) == DEFAULT_ASSET_CATEGORY
        assert get_category({"id": "unknown"}) == DEFAULT_ASSET_CATEGORY
        assert get_category({"name": "Some Coin"}) == DEFAULT_ASSET_CATEGORY
        assert get_category({}) == DEFAULT_ASSET_CATEGORY


class TestCoinToAsset:
    """Test the coin_to_asset conversion function"""

    def test_coin_to_asset_basic_conversion(self):
        """Test basic coin to asset conversion"""
        coin = create_test_coin("BTC", "Bitcoin", 45000.0)

        asset = coin_to_asset(coin)

        # Verify Asset object is created correctly
        assert isinstance(asset, Asset)
        assert asset.asset_id == "BTC"
        assert asset.name == "Bitcoin"
        assert asset.description == "Digital asset: Bitcoin"
        assert asset.category == DEFAULT_ASSET_CATEGORY
        assert asset.amount == Decimal(str(DEFAULT_ASSET_AMOUNT))
        assert asset.price_usd == Decimal("45000.0")
        assert asset.is_active is True
        assert asset.symbol == "BTC"

    def test_coin_to_asset_all_fields_mapped(self):
        """Test that all coin fields are properly mapped to asset"""
        coin = create_test_coin("ETH", "Ethereum", 3000.0)

        asset = coin_to_asset(coin)

        # Verify all comprehensive fields are mapped
        # Note: Asset entity may store some values as float, not Decimal
        assert asset.image == coin.image
        assert asset.market_cap_rank == coin.market_cap_rank
        assert float(asset.current_price) == float(coin.current_price)
        assert float(asset.high_24h) == float(coin.high_24h)
        assert float(asset.low_24h) == float(coin.low_24h)
        assert float(asset.circulating_supply) == float(coin.circulating_supply)
        assert float(asset.total_supply) == float(coin.total_supply)
        assert float(asset.max_supply) == float(coin.max_supply)
        assert float(asset.price_change_24h) == float(coin.price_change_24h)
        assert float(asset.price_change_percentage_24h) == float(coin.price_change_percentage_24h)
        assert float(asset.price_change_percentage_7d) == float(coin.price_change_percentage_7d)
        assert float(asset.price_change_percentage_30d) == float(coin.price_change_percentage_30d)
        assert float(asset.market_cap) == float(coin.market_cap)
        assert float(asset.total_volume_24h) == float(coin.total_volume_24h)
        assert float(asset.ath) == float(coin.ath)
        assert float(asset.atl) == float(coin.atl)
        assert asset.last_updated == coin.last_updated

    def test_coin_to_asset_with_none_values(self):
        """Test coin_to_asset handles None values properly for optional fields"""
        coin = CoinData(
            symbol="DOGE",
            name="Dogecoin",
            current_price=0.08,  # Provide a valid price
            price_usd=0.08,  # Asset requires price_usd to not be None
            max_supply=None  # Some coins don't have max supply
        )

        asset = coin_to_asset(coin)

        assert asset.asset_id == "DOGE"
        assert asset.max_supply is None
        assert asset.price_usd == Decimal("0.08")

    def test_coin_to_asset_with_optional_none_fields(self):
        """Test coin_to_asset with various None optional fields"""
        coin = CoinData(
            symbol="XRP",
            name="Ripple",
            current_price=0.5,
            price_usd=0.5,
            image=None,
            market_cap_rank=None,
            high_24h=None,
            low_24h=None,
            ath=None,
            atl=None
        )

        asset = coin_to_asset(coin)

        assert asset.asset_id == "XRP"
        assert asset.name == "Ripple"
        assert asset.price_usd == Decimal("0.5")
        # Optional fields should be None
        assert asset.image is None
        assert asset.ath is None
        assert asset.atl is None


class TestUpsertCoinsToInventory:
    """Test the upsert_coins_to_inventory function"""

    @pytest.mark.asyncio
    async def test_upsert_creates_new_asset_when_not_found_entity_exception(self):
        """Test creating new asset when CNOPEntityNotFoundException is raised"""
        mock_coins = [create_test_coin("BTC", "Bitcoin", 45000.0)]

        # Mock only the external dependency: get_dynamodb_manager
        with patch(PATH_GET_DYNAMODB_MANAGER) as mock_get_manager:
            mock_connection = MagicMock()
            mock_dao = MagicMock()

            # Setup the manager to return connection
            mock_manager = MagicMock()
            mock_manager.get_connection.return_value = mock_connection
            mock_get_manager.return_value = mock_manager

            # Mock DAO behavior: asset doesn't exist, so create it
            mock_dao.get_asset_by_id.side_effect = CNOPEntityNotFoundException("Not found")
            mock_dao.create_asset.return_value = None

            # Patch AssetDAO constructor to return our mock
            with patch('data.init_inventory.AssetDAO', return_value=mock_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                assert result == 1
                mock_dao.get_asset_by_id.assert_called_once()
                mock_dao.create_asset.assert_called_once()

                # Verify the asset passed to create_asset has correct data
                created_asset = mock_dao.create_asset.call_args[0][0]
                assert created_asset.asset_id == "BTC"
                assert created_asset.name == "Bitcoin"

    @pytest.mark.asyncio
    async def test_upsert_creates_new_asset_when_not_found_asset_exception(self):
        """Test creating new asset when CNOPAssetNotFoundException is raised"""
        mock_coins = [create_test_coin("ETH", "Ethereum", 3000.0)]

        with patch(PATH_GET_DYNAMODB_MANAGER) as mock_get_manager:
            mock_connection = MagicMock()
            mock_dao = MagicMock()

            mock_manager = MagicMock()
            mock_manager.get_connection.return_value = mock_connection
            mock_get_manager.return_value = mock_manager

            # Mock DAO behavior: asset doesn't exist
            mock_dao.get_asset_by_id.side_effect = CNOPAssetNotFoundException("Not found")
            mock_dao.create_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                assert result == 1
                mock_dao.create_asset.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_updates_existing_asset(self):
        """Test updating existing asset"""
        mock_coins = [create_test_coin("BTC", "Bitcoin", 46000.0)]

        with patch(PATH_GET_DYNAMODB_MANAGER) as mock_get_manager:
            mock_connection = MagicMock()
            mock_dao = MagicMock()

            mock_manager = MagicMock()
            mock_manager.get_connection.return_value = mock_connection
            mock_get_manager.return_value = mock_manager

            # Mock DAO behavior: asset exists, so update it
            existing_asset = MagicMock()
            mock_dao.get_asset_by_id.return_value = existing_asset
            mock_dao.update_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                assert result == 1
                mock_dao.get_asset_by_id.assert_called_once()
                mock_dao.update_asset.assert_called_once()

                # Verify updated asset has new price
                updated_asset = mock_dao.update_asset.call_args[0][0]
                assert updated_asset.asset_id == "BTC"
                assert updated_asset.price_usd == Decimal("46000.0")

    @pytest.mark.asyncio
    async def test_upsert_handles_multiple_coins(self):
        """Test upserting multiple coins in a single batch"""
        mock_coins = [
            create_test_coin("BTC", "Bitcoin", 45000.0),
            create_test_coin("ETH", "Ethereum", 3000.0),
            create_test_coin("ADA", "Cardano", 0.5)
        ]

        with patch(PATH_GET_DYNAMODB_MANAGER) as mock_get_manager:
            mock_connection = MagicMock()
            mock_dao = MagicMock()

            mock_manager = MagicMock()
            mock_manager.get_connection.return_value = mock_connection
            mock_get_manager.return_value = mock_manager

            # Mock: all assets exist and will be updated
            mock_dao.get_asset_by_id.return_value = MagicMock()
            mock_dao.update_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                assert result == 3
                assert mock_dao.get_asset_by_id.call_count == 3
                assert mock_dao.update_asset.call_count == 3

    @pytest.mark.asyncio
    async def test_upsert_handles_database_error_gracefully(self):
        """Test that database errors are handled and other coins continue processing"""
        mock_coins = [
            create_test_coin("BTC", "Bitcoin", 45000.0),
            create_test_coin("ETH", "Ethereum", 3000.0),
        ]

        with patch(PATH_GET_DYNAMODB_MANAGER) as mock_get_manager:
            mock_connection = MagicMock()
            mock_dao = MagicMock()

            mock_manager = MagicMock()
            mock_manager.get_connection.return_value = mock_connection
            mock_get_manager.return_value = mock_manager

            # First coin: database error, second coin: success
            mock_dao.get_asset_by_id.side_effect = [
                Exception("Database error"),
                MagicMock()  # Second call succeeds
            ]
            mock_dao.update_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                # Only second coin should be processed successfully
                assert result == 1
                assert mock_dao.get_asset_by_id.call_count == 2
                assert mock_dao.update_asset.call_count == 1

    @pytest.mark.asyncio
    async def test_upsert_handles_coin_conversion_error(self):
        """Test handling of errors during coin-to-asset conversion"""
        # Create a coin that might cause conversion issues
        mock_coins = [create_test_coin("BTC", "Bitcoin", 45000.0)]

        with patch(PATH_GET_DYNAMODB_MANAGER) as mock_get_manager:
            mock_connection = MagicMock()
            mock_manager = MagicMock()
            mock_manager.get_connection.return_value = mock_connection
            mock_get_manager.return_value = mock_manager

            # Mock coin_to_asset to raise an exception
            with patch('data.init_inventory.coin_to_asset', side_effect=Exception("Conversion error")):
                result = await upsert_coins_to_inventory(mock_coins)

                # Should handle error gracefully and return 0
                assert result == 0

    @pytest.mark.asyncio
    async def test_upsert_mixed_create_and_update(self):
        """Test mixed scenario with some new and some existing assets"""
        mock_coins = [
            create_test_coin("BTC", "Bitcoin", 45000.0),
            create_test_coin("ETH", "Ethereum", 3000.0),
        ]

        with patch(PATH_GET_DYNAMODB_MANAGER) as mock_get_manager:
            mock_connection = MagicMock()
            mock_dao = MagicMock()

            mock_manager = MagicMock()
            mock_manager.get_connection.return_value = mock_connection
            mock_get_manager.return_value = mock_manager

            # First coin doesn't exist (create), second exists (update)
            mock_dao.get_asset_by_id.side_effect = [
                CNOPAssetNotFoundException("Not found"),
                MagicMock()  # Exists
            ]
            mock_dao.create_asset.return_value = None
            mock_dao.update_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                assert result == 2
                assert mock_dao.create_asset.call_count == 1
                assert mock_dao.update_asset.call_count == 1


class TestInitializeInventoryData:
    """Test the initialize_inventory_data function"""

    @pytest.mark.asyncio
    async def test_initialize_inventory_data_success(self):
        """Test successful initialization"""
        mock_coins = [
            create_test_coin("BTC", "Bitcoin", 45000.0),
            create_test_coin("ETH", "Ethereum", 3000.0)
        ]

        # Mock only external dependencies
        with patch(PATH_FETCH_COINS, return_value=mock_coins) as mock_fetch:
            with patch(PATH_GET_DYNAMODB_MANAGER) as mock_get_manager:
                mock_connection = MagicMock()
                mock_dao = MagicMock()

                mock_manager = MagicMock()
                mock_manager.get_connection.return_value = mock_connection
                mock_get_manager.return_value = mock_manager

                # All coins exist and will be updated
                mock_dao.get_asset_by_id.return_value = MagicMock()
                mock_dao.update_asset.return_value = None

                with patch('data.init_inventory.AssetDAO', return_value=mock_dao):
                    await initialize_inventory_data()

                    mock_fetch.assert_called_once()
                    assert mock_dao.update_asset.call_count == 2

    @pytest.mark.asyncio
    async def test_initialize_inventory_data_fetch_error(self):
        """Test handling of fetch errors"""
        with patch(PATH_FETCH_COINS, side_effect=Exception("API Error")):
            # Should not raise exception, just log error
            await initialize_inventory_data()

    @pytest.mark.asyncio
    async def test_initialize_inventory_data_empty_coins(self):
        """Test handling when no coins are fetched"""
        with patch(PATH_FETCH_COINS, return_value=[]):
            # Should return early without attempting to upsert
            await initialize_inventory_data()

    @pytest.mark.asyncio
    async def test_initialize_inventory_data_upsert_error(self):
        """Test handling of errors during upsert"""
        mock_coins = [create_test_coin("BTC", "Bitcoin", 45000.0)]

        with patch(PATH_FETCH_COINS, return_value=mock_coins):
            with patch(PATH_GET_DYNAMODB_MANAGER) as mock_get_manager:
                mock_connection = MagicMock()
                mock_dao = MagicMock()

                mock_manager = MagicMock()
                mock_manager.get_connection.return_value = mock_connection
                mock_get_manager.return_value = mock_manager

                # Simulate database error
                mock_dao.get_asset_by_id.side_effect = Exception("Database error")

                with patch('data.init_inventory.AssetDAO', return_value=mock_dao):
                    # Should not raise exception
                    await initialize_inventory_data()


class TestStartupInventoryInitialization:
    """Test the startup_inventory_initialization function"""

    @pytest.mark.asyncio
    async def test_startup_calls_initialize(self):
        """Test that startup function calls initialize_inventory_data"""
        with patch('data.init_inventory.initialize_inventory_data') as mock_init:
            await startup_inventory_initialization()

            mock_init.assert_called_once_with()


class TestIntegrationScenarios:
    """Test integration scenarios with real function interactions"""

    @pytest.mark.asyncio
    async def test_full_initialization_flow(self):
        """Test the complete flow from fetch to database upsert"""
        mock_coins = [
            create_test_coin("BTC", "Bitcoin", 45000.0),
            create_test_coin("ETH", "Ethereum", 3000.0)
        ]

        with patch(PATH_FETCH_COINS, return_value=mock_coins):
            with patch(PATH_GET_DYNAMODB_MANAGER) as mock_get_manager:
                mock_connection = MagicMock()
                mock_dao = MagicMock()

                mock_manager = MagicMock()
                mock_manager.get_connection.return_value = mock_connection
                mock_get_manager.return_value = mock_manager

                # Mix of new and existing assets
                mock_dao.get_asset_by_id.side_effect = [
                    CNOPAssetNotFoundException("Not found"),  # BTC is new
                    MagicMock()  # ETH exists
                ]
                mock_dao.create_asset.return_value = None
                mock_dao.update_asset.return_value = None

                with patch('data.init_inventory.AssetDAO', return_value=mock_dao):
                    await initialize_inventory_data()

                    # Verify both operations occurred
                    assert mock_dao.create_asset.call_count == 1
                    assert mock_dao.update_asset.call_count == 1

    def test_coin_to_asset_preserves_all_data(self):
        """Test that coin_to_asset preserves all important data fields"""
        coin = create_test_coin("SOL", "Solana", 100.0)

        asset = coin_to_asset(coin)

        # Verify critical fields are preserved (comparing as floats for compatibility)
        assert asset.asset_id == coin.symbol
        assert asset.name == coin.name
        assert asset.price_usd == coin.price_usd
        assert float(asset.market_cap) == float(coin.market_cap)
        assert float(asset.circulating_supply) == float(coin.circulating_supply)
        assert float(asset.ath) == float(coin.ath)
        assert float(asset.atl) == float(coin.atl)