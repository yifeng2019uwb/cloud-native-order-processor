import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from decimal import Decimal
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from common.exceptions import CNOPEntityNotFoundException

# Import the module to test
from data.init_inventory import (
    get_category,
    upsert_coins_to_inventory,
    initialize_inventory_data,
    startup_inventory_initialization
)


class TestGetCategory:
    """Test the get_category function"""

    def test_get_category_returns_default(self):
        """Test that get_category always returns the default category"""
        from constants import DEFAULT_ASSET_CATEGORY

        # Any coin should return the default category
        bitcoin_coin = {"id": "bitcoin"}
        ethereum_coin = {"id": "ethereum"}
        unknown_coin = {"id": "some-unknown-coin"}
        coin_without_id = {"name": "Some Coin"}
        empty_coin = {}

        assert get_category(bitcoin_coin) == DEFAULT_ASSET_CATEGORY
        assert get_category(ethereum_coin) == DEFAULT_ASSET_CATEGORY
        assert get_category(unknown_coin) == DEFAULT_ASSET_CATEGORY
        assert get_category(coin_without_id) == DEFAULT_ASSET_CATEGORY
        assert get_category(empty_coin) == DEFAULT_ASSET_CATEGORY


class TestUpsertCoinsToInventory:
    """Test the upsert_coins_to_inventory function"""

    @pytest.mark.asyncio
    async def test_upsert_coins_creates_new_assets(self):
        """Test creating new assets"""
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
            mock_asset_dao.update_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_asset_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                assert result == 2
                assert mock_asset_dao.update_asset.call_count == 2
                # update_asset is inherently an upsert - creates if not exists, updates if exists

    @pytest.mark.asyncio
    async def test_upsert_coins_updates_existing_assets(self):
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
            mock_asset_dao.update_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_asset_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                assert result == 1
                assert mock_asset_dao.update_asset.call_count == 1
                # update_asset is inherently an upsert - creates if not exists, updates if exists

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
            mock_asset_dao.update_asset.return_value = None

            with patch('data.init_inventory.AssetDAO', return_value=mock_asset_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                assert result == 2
                assert mock_asset_dao.update_asset.call_count == 2
                # update_asset is inherently an upsert - creates if not exists, updates if exists

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
            # First call succeeds, second call fails
            mock_asset_dao.update_asset.side_effect = [None, Exception("Database error")]

            with patch('data.init_inventory.AssetDAO', return_value=mock_asset_dao):
                result = await upsert_coins_to_inventory(mock_coins)

                # Should still return 1 for the successful upsert
                assert result == 1
                assert mock_asset_dao.update_asset.call_count == 2

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

        with patch('services.fetch_coins.fetch_coins', return_value=mock_coins) as mock_fetch, \
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
        with patch('services.fetch_coins.fetch_coins', side_effect=Exception("API Error")):
            result = await initialize_inventory_data()

            assert result["status"] == "error"
            assert result["error"] == "API Error"
            assert "Failed to initialize inventory data" in result["message"]

    @pytest.mark.asyncio
    async def test_initialize_inventory_data_upsert_error(self):
        """Test handling of upsert errors"""
        mock_coins = [{"symbol": "BTC", "name": "Bitcoin", "current_price": 45000.0}]

        with patch('services.fetch_coins.fetch_coins', return_value=mock_coins), \
             patch('data.init_inventory.upsert_coins_to_inventory', side_effect=Exception("Database Error")):

            result = await initialize_inventory_data()

            assert result["status"] == "error"
            assert result["error"] == "Database Error"
            assert "Failed to initialize inventory data" in result["message"]

    @pytest.mark.asyncio
    async def test_initialize_inventory_data_empty_coins(self):
        """Test handling of empty coin list"""
        with patch('services.fetch_coins.fetch_coins', return_value=[]), \
             patch('data.init_inventory.upsert_coins_to_inventory', return_value=0):

            result = await initialize_inventory_data()

            assert result["status"] == "error"
            assert result["error"] == "No coins received"
            assert "Failed to fetch coins from data providers" in result["message"]


class TestStartupInventoryInitialization:
    """Test the startup_inventory_initialization function"""

    @pytest.mark.asyncio
    async def test_startup_inventory_initialization(self):
        """Test the convenience function calls initialize_inventory_data correctly"""
        expected_result = {
            "status": "success",
            "assets_upserted": 1,
            "message": "Successfully upserted 1 assets from data providers"
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

        with patch('services.fetch_coins.fetch_coins', return_value=mock_coins), \
             patch('data.init_inventory.upsert_coins_to_inventory', return_value=2):

            result = await initialize_inventory_data()

            assert result["status"] == "success"
            assert result["assets_upserted"] == 2