import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from decimal import Decimal
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from common.exceptions import EntityNotFoundException

# Import the module to test
from data.init_inventory import (
    Constants,
    get_category,
    fetch_top_coins,
    upsert_coins_to_inventory,
    initialize_inventory_data,
    startup_inventory_initialization
)


class TestConstants:
    """Test the Constants class"""

    def test_constants_values(self):
        """Test that constants have expected values"""
        assert Constants.COINGECKO_API == "https://api.coingecko.com/api/v3/coins/markets"
        assert Constants.TOP_N_COINS == 100
        assert Constants.PARAMS == {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1
        }
        assert "bitcoin" in Constants.CATEGORY_MAP
        assert "ethereum" in Constants.CATEGORY_MAP
        assert Constants.CATEGORY_MAP["bitcoin"] == "major"
        assert Constants.CATEGORY_MAP["tether"] == "stablecoin"


class TestGetCategory:
    """Test the get_category function"""

    def test_get_category_major_coins(self):
        """Test category mapping for major coins"""
        bitcoin_coin = {"id": "bitcoin"}
        ethereum_coin = {"id": "ethereum"}

        assert get_category(bitcoin_coin) == "major"
        assert get_category(ethereum_coin) == "major"

    def test_get_category_stablecoins(self):
        """Test category mapping for stablecoins"""
        tether_coin = {"id": "tether"}
        usdc_coin = {"id": "usd-coin"}

        assert get_category(tether_coin) == "stablecoin"
        assert get_category(usdc_coin) == "stablecoin"

    def test_get_category_unknown_coin(self):
        """Test category mapping for unknown coins (fallback to altcoin)"""
        unknown_coin = {"id": "some-unknown-coin"}

        assert get_category(unknown_coin) == "altcoin"

    def test_get_category_missing_id(self):
        """Test category mapping when id is missing"""
        coin_without_id = {"name": "Some Coin"}

        assert get_category(coin_without_id) == "altcoin"

    def test_get_category_empty_dict(self):
        """Test category mapping with empty dictionary"""
        empty_coin = {}

        assert get_category(empty_coin) == "altcoin"


class TestFetchTopCoins:
    """Test the fetch_top_coins function"""

    @pytest.mark.asyncio
    async def test_fetch_top_coins_success(self):
        """Test successful API call to CoinGecko"""
        mock_coins = [
            {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 45000.0},
            {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "current_price": 3000.0}
        ]

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.json.return_value = mock_coins
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await fetch_top_coins()

            assert result == mock_coins
            mock_client.get.assert_called_once_with(
                Constants.COINGECKO_API,
                params=Constants.PARAMS
            )

    @pytest.mark.asyncio
    async def test_fetch_top_coins_http_error(self):
        """Test handling of HTTP errors"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=MagicMock(), response=MagicMock()
            )
            mock_response.json.return_value = []
            mock_client.get.return_value = mock_response

            result = await fetch_top_coins()
            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_top_coins_network_error(self):
        """Test handling of network errors"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_client.get.side_effect = httpx.ConnectError("Connection failed")

            result = await fetch_top_coins()
            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_top_coins_empty_response(self):
        """Test handling of empty response"""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            result = await fetch_top_coins()

            assert result == []


class TestUpsertCoinsToInventory:
    """Test the upsert_coins_to_inventory function"""

    @pytest.mark.asyncio
    async def test_upsert_coins_create_new_assets(self):
        """Test creating new assets when they don't exist"""
        mock_coins = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "description": "Bitcoin cryptocurrency",
                "current_price": 45000.0
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "description": "Ethereum cryptocurrency",
                "current_price": 3000.0
            }
        ]

        with patch('data.init_inventory.dynamodb_manager') as mock_db_manager:
            mock_connection = AsyncMock()
            mock_db_manager.get_connection.return_value.__aenter__.return_value = mock_connection

            mock_asset_dao = MagicMock()
            # Mock DAO to raise EntityNotFoundException when asset doesn't exist
            mock_asset_dao.get_asset_by_id.side_effect = EntityNotFoundException("Asset not found")
            mock_asset_dao.create_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_asset_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                assert result == 2
                assert mock_asset_dao.create_asset.call_count == 2
                assert mock_asset_dao.update_asset.call_count == 0

    @pytest.mark.asyncio
    async def test_upsert_coins_update_existing_assets(self):
        """Test updating existing assets"""
        mock_coins = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "description": "Bitcoin cryptocurrency",
                "current_price": 45000.0
            }
        ]

        with patch('data.init_inventory.dynamodb_manager') as mock_db_manager:
            mock_connection = AsyncMock()
            mock_db_manager.get_connection.return_value.__aenter__.return_value = mock_connection

            mock_asset_dao = MagicMock()
            # Mock DAO to return existing asset
            mock_asset_dao.get_asset_by_id.return_value = MagicMock()  # Asset exists
            mock_asset_dao.update_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_asset_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                assert result == 1
                assert mock_asset_dao.update_asset.call_count == 1
                assert mock_asset_dao.create_asset.call_count == 0

    @pytest.mark.asyncio
    async def test_upsert_coins_mixed_create_and_update(self):
        """Test mixed scenario with some new and some existing assets"""
        mock_coins = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "description": "Bitcoin cryptocurrency",
                "current_price": 45000.0
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "description": "Ethereum cryptocurrency",
                "current_price": 3000.0
            }
        ]

        with patch('data.init_inventory.dynamodb_manager') as mock_db_manager:
            mock_connection = AsyncMock()
            mock_db_manager.get_connection.return_value.__aenter__.return_value = mock_connection

            mock_asset_dao = MagicMock()
            # First asset exists, second doesn't
            mock_asset_dao.get_asset_by_id.side_effect = [MagicMock(), EntityNotFoundException("Asset not found")]
            mock_asset_dao.update_asset.return_value = None
            mock_asset_dao.create_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_asset_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                assert result == 2
                assert mock_asset_dao.update_asset.call_count == 1
                assert mock_asset_dao.create_asset.call_count == 1

    @pytest.mark.asyncio
    async def test_upsert_coins_handles_exceptions(self):
        """Test that exceptions during upsert are handled gracefully"""
        mock_coins = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "description": "Bitcoin cryptocurrency",
                "current_price": 45000.0
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "description": "Ethereum cryptocurrency",
                "current_price": 3000.0
            }
        ]

        with patch('data.init_inventory.dynamodb_manager') as mock_db_manager:
            mock_connection = AsyncMock()
            mock_db_manager.get_connection.return_value.__aenter__.return_value = mock_connection

            mock_asset_dao = MagicMock()
            mock_asset_dao.get_asset_by_id.side_effect = [EntityNotFoundException("Asset not found"), Exception("Database error")]
            mock_asset_dao.create_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_asset_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                # Should still return 1 for the successful upsert
                assert result == 1
                assert mock_asset_dao.create_asset.call_count == 1

    @pytest.mark.asyncio
    async def test_upsert_coins_missing_description(self):
        """Test handling of coins with missing description"""
        mock_coins = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "current_price": 45000.0
                # No description field
            }
        ]

        with patch('data.init_inventory.dynamodb_manager') as mock_db_manager:
            mock_connection = AsyncMock()
            mock_db_manager.get_connection.return_value.__aenter__.return_value = mock_connection

            mock_asset_dao = MagicMock()
            mock_asset_dao.get_asset_by_id.side_effect = EntityNotFoundException("Asset not found")
            mock_asset_dao.create_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_asset_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                assert result == 1
                # Verify that create_asset was called with the correct AssetCreate object
                call_args = mock_asset_dao.create_asset.call_args[0][0]
                assert call_args.asset_id == "BTC"
                assert call_args.name == "Bitcoin"
                assert call_args.amount == Decimal("1000.0")
                assert call_args.price_usd == Decimal("45000.0")


class TestInitializeInventoryData:
    """Test the initialize_inventory_data function"""

    @pytest.mark.asyncio
    async def test_initialize_inventory_data_success(self):
        """Test successful initialization"""
        mock_coins = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "description": "Bitcoin cryptocurrency",
                "current_price": 45000.0
            }
        ]

        with patch('data.init_inventory.fetch_top_coins', return_value=mock_coins) as mock_fetch, \
             patch('data.init_inventory.upsert_coins_to_inventory', return_value=1) as mock_upsert:

            result = await initialize_inventory_data()

            assert result["status"] == "success"
            assert result["assets_upserted"] == 1
            assert "Successfully upserted 1 assets" in result["message"]

            mock_fetch.assert_called_once()
            mock_upsert.assert_called_once_with(mock_coins)

    @pytest.mark.asyncio
    async def test_initialize_inventory_data_fetch_error(self):
        """Test handling of fetch errors"""
        with patch('data.init_inventory.fetch_top_coins', side_effect=Exception("API Error")):
            result = await initialize_inventory_data()

            assert result["status"] == "error"
            assert result["error"] == "API Error"
            assert "Failed to initialize inventory data" in result["message"]

    @pytest.mark.asyncio
    async def test_initialize_inventory_data_upsert_error(self):
        """Test handling of upsert errors"""
        mock_coins = [{"symbol": "BTC", "name": "Bitcoin", "current_price": 45000.0}]

        with patch('data.init_inventory.fetch_top_coins', return_value=mock_coins), \
             patch('data.init_inventory.upsert_coins_to_inventory', side_effect=Exception("Database Error")):

            result = await initialize_inventory_data()

            assert result["status"] == "error"
            assert result["error"] == "Database Error"
            assert "Failed to initialize inventory data" in result["message"]

    @pytest.mark.asyncio
    async def test_initialize_inventory_data_empty_coins(self):
        """Test handling of empty coin list"""
        with patch('data.init_inventory.fetch_top_coins', return_value=[]), \
             patch('data.init_inventory.upsert_coins_to_inventory', return_value=0):

            result = await initialize_inventory_data()

            assert result["status"] == "success"
            assert result["assets_upserted"] == 0
            assert "Successfully upserted 0 assets" in result["message"]


class TestStartupInventoryInitialization:
    """Test the startup_inventory_initialization function"""

    @pytest.mark.asyncio
    async def test_startup_inventory_initialization(self):
        """Test the convenience function calls initialize_inventory_data correctly"""
        expected_result = {
            "status": "success",
            "assets_upserted": 1,
            "message": "Successfully upserted 1 assets from CoinGecko"
        }

        with patch('data.init_inventory.initialize_inventory_data', return_value=expected_result) as mock_init:
            result = await startup_inventory_initialization()

            assert result == expected_result
            mock_init.assert_called_once_with()


class TestIntegrationScenarios:
    """Test integration scenarios with multiple functions"""

    @pytest.mark.asyncio
    async def test_full_initialization_flow(self):
        """Test the complete flow from fetch to upsert"""
        mock_coins = [
            {
                "id": "bitcoin",
                "symbol": "BTC",
                "name": "Bitcoin",
                "description": "Bitcoin cryptocurrency",
                "current_price": 45000.0
            },
            {
                "id": "ethereum",
                "symbol": "ETH",
                "name": "Ethereum",
                "description": "Ethereum cryptocurrency",
                "current_price": 3000.0
            }
        ]

        with patch('httpx.AsyncClient') as mock_client_class, \
             patch('data.init_inventory.dynamodb_manager') as mock_db_manager:

            # Mock HTTP client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.json.return_value = mock_coins
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            # Mock database
            mock_connection = AsyncMock()
            mock_db_manager.get_connection.return_value.__aenter__.return_value = mock_connection

            mock_asset_dao = MagicMock()
            mock_asset_dao.get_asset_by_id.side_effect = EntityNotFoundException("Asset not found")
            mock_asset_dao.create_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_asset_dao):
                result = await initialize_inventory_data()

                assert result["status"] == "success"
                assert result["assets_upserted"] == 2

                # Verify category mapping
                create_calls = mock_asset_dao.create_asset.call_args_list
                assert len(create_calls) == 2

                # Check that Bitcoin was categorized as "major"
                bitcoin_call = create_calls[0][0][0]
                assert bitcoin_call.asset_id == "BTC"
                assert bitcoin_call.category == "major"

                # Check that Ethereum was categorized as "major"
                ethereum_call = create_calls[1][0][0]
                assert ethereum_call.asset_id == "ETH"
                assert ethereum_call.category == "major"