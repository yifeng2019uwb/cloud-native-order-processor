import pytest
import os
import sys
from unittest.mock import AsyncMock, patch, MagicMock

# Add the necessary paths to sys.path before importing the controller
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))  # for common
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))  # for api_models

# Import the controller functions directly
from controllers.assets import list_assets, get_asset_by_id

# Import exception classes for testing
from inventory_exceptions import (
    CNOPAssetValidationException,
    CNOPInventoryServerException
)
from common.exceptions import (
    CNOPDatabaseOperationException,
    CNOPAssetNotFoundException
)


def test_list_assets_success():
    """Test list_assets with mocked AssetDAO"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        # Setup mock AssetDAO
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Mock asset data with proper attributes
        mock_asset1 = MagicMock()
        mock_asset1.asset_id = "BTC"
        mock_asset1.name = "Bitcoin"
        mock_asset1.description = "Bitcoin cryptocurrency"
        mock_asset1.category = "Cryptocurrency"
        mock_asset1.price_usd = 45000.0
        mock_asset1.is_active = True
        # Add new CoinGecko fields
        mock_asset1.symbol = "BTC"
        mock_asset1.image = "https://assets.coingecko.com/coins/images/1/large/bitcoin.png"
        mock_asset1.market_cap_rank = 1
        mock_asset1.high_24h = 46000.0
        mock_asset1.low_24h = 44000.0
        mock_asset1.circulating_supply = 19500000
        mock_asset1.total_supply = 21000000
        mock_asset1.max_supply = 21000000
        mock_asset1.price_change_24h = 500.0
        mock_asset1.price_change_percentage_24h = 1.1
        mock_asset1.price_change_percentage_7d = 5.2
        mock_asset1.price_change_percentage_30d = 8.5
        mock_asset1.market_cap = 850000000000
        mock_asset1.market_cap_change_24h = 10000000000
        mock_asset1.market_cap_change_percentage_24h = 1.2
        mock_asset1.total_volume_24h = 25000000000
        mock_asset1.volume_change_24h = 5000000000
        mock_asset1.ath = 69000.0
        mock_asset1.ath_change_percentage = -34.8
        mock_asset1.ath_date = "2021-11-10T14:24:11.849Z"
        mock_asset1.atl = 67.81
        mock_asset1.atl_change_percentage = 66263.0
        mock_asset1.atl_date = "2013-07-06T00:00:00.000Z"
        mock_asset1.last_updated = "2025-08-30T21:49:33.955Z"
        mock_asset1.sparkline_7d = {"prices": [44000, 45000, 46000, 45000, 44000, 45000, 45000]}
        mock_asset1.updated_at = "2025-08-30T21:49:33.955Z"

        mock_asset2 = MagicMock()
        mock_asset2.asset_id = "ETH"
        mock_asset2.name = "Ethereum"
        mock_asset2.description = "Ethereum cryptocurrency"
        mock_asset2.category = "Cryptocurrency"
        mock_asset2.price_usd = 3000.0
        mock_asset2.is_active = True
        # Add new CoinGecko fields
        mock_asset2.symbol = "ETH"
        mock_asset2.image = "https://assets.coingecko.com/coins/images/279/large/ethereum.png"
        mock_asset2.market_cap_rank = 2
        mock_asset2.high_24h = 3100.0
        mock_asset2.low_24h = 2900.0
        mock_asset2.circulating_supply = 120000000
        mock_asset2.total_supply = 120000000
        mock_asset2.max_supply = None
        mock_asset2.price_change_24h = -50.0
        mock_asset2.price_change_percentage_24h = -1.6
        mock_asset2.price_change_percentage_7d = -2.1
        mock_asset2.price_change_percentage_30d = -5.2
        mock_asset2.market_cap = 350000000000
        mock_asset2.market_cap_change_24h = -5000000000
        mock_asset2.market_cap_change_percentage_24h = -1.4
        mock_asset2.total_volume_24h = 15000000000
        mock_asset2.volume_change_24h = -2000000000
        mock_asset2.ath = 4878.26
        mock_asset2.ath_change_percentage = -38.5
        mock_asset2.ath_date = "2021-11-10T14:24:11.849Z"
        mock_asset2.atl = 0.432979
        mock_asset2.atl_change_percentage = 692866.0
        mock_asset2.atl_date = "2020-01-20T00:00:00.000Z"
        mock_asset2.last_updated = "2025-08-30T21:49:33.955Z"
        mock_asset2.sparkline_7d = {"prices": [3100, 3000, 2900, 3000, 3100, 3000, 3000]}
        mock_asset2.updated_at = "2025-08-30T21:49:33.955Z"

        # Mock inactive asset for total count
        mock_asset3 = MagicMock()
        mock_asset3.asset_id = "INACTIVE"
        mock_asset3.name = "Inactive Asset"
        mock_asset3.description = "Inactive asset"
        mock_asset3.category = "Test"
        mock_asset3.price_usd = 100.0
        mock_asset3.is_active = False
        # Add new CoinGecko fields (can be None for inactive assets)
        mock_asset3.symbol = None
        mock_asset3.image = None
        mock_asset3.market_cap_rank = None
        mock_asset3.high_24h = None
        mock_asset3.low_24h = None
        mock_asset3.circulating_supply = None
        mock_asset3.total_supply = None
        mock_asset3.max_supply = None
        mock_asset3.price_change_24h = None
        mock_asset3.price_change_percentage_24h = None
        mock_asset3.price_change_percentage_7d = None
        mock_asset3.price_change_percentage_30d = None
        mock_asset3.market_cap = None
        mock_asset3.market_cap_change_24h = None
        mock_asset3.market_cap_change_percentage_24h = None
        mock_asset3.total_volume_24h = None
        mock_asset3.volume_change_24h = None
        mock_asset3.ath = None
        mock_asset3.ath_change_percentage = None
        mock_asset3.ath_date = None
        mock_asset3.atl = None
        mock_asset3.atl_change_percentage = None
        mock_asset3.atl_date = None
        mock_asset3.last_updated = None
        mock_asset3.sparkline_7d = None
        mock_asset3.updated_at = "2025-08-30T21:49:33.955Z"

        # Setup mock to return different results based on active_only parameter
        def mock_get_all_assets(active_only=True):
            if active_only:
                return [mock_asset1, mock_asset2]
            else:
                return [mock_asset1, mock_asset2, mock_asset3]

        mock_dao.get_all_assets.side_effect = mock_get_all_assets

        # test the function
        result = list_assets(active_only=True, limit=2, asset_dao=mock_dao)

        # Verify AssetDAO was called correctly (twice: once for active, once for total)
        assert mock_dao.get_all_assets.call_count == 2
        mock_dao.get_all_assets.assert_any_call(active_only=True)
        mock_dao.get_all_assets.assert_any_call(active_only=False)

        # Verify result structure
        assert result is not None
        assert hasattr(result, 'assets')
        assert len(result.assets) == 2

        # Verify enhanced CoinGecko attributes are present in the response
        btc_asset = result.assets[0]
        assert btc_asset.asset_id == "BTC"
        assert btc_asset.name == "Bitcoin"
        assert btc_asset.symbol == "BTC"
        assert btc_asset.image == "https://assets.coingecko.com/coins/images/1/large/bitcoin.png"
        assert btc_asset.market_cap_rank == 1
        assert btc_asset.price_usd == 45000.0  # This field exists in AssetResponse
        assert btc_asset.high_24h == 46000.0
        assert btc_asset.low_24h == 44000.0
        assert btc_asset.circulating_supply == 19500000
        assert btc_asset.market_cap == 850000000000
        assert btc_asset.price_change_percentage_24h == 1.1
        assert btc_asset.total_volume_24h == 25000000000
        assert btc_asset.last_updated is not None  # This field exists in AssetResponse

        eth_asset = result.assets[1]
        assert eth_asset.asset_id == "ETH"
        assert eth_asset.name == "Ethereum"
        assert eth_asset.symbol == "ETH"
        assert eth_asset.image == "https://assets.coingecko.com/coins/images/279/large/ethereum.png"
        assert eth_asset.market_cap_rank == 2
        assert eth_asset.price_usd == 3000.0  # This field exists in AssetResponse
        assert eth_asset.high_24h == 3100.0
        assert eth_asset.low_24h == 2900.0
        assert eth_asset.circulating_supply == 120000000
        assert eth_asset.market_cap == 350000000000
        assert eth_asset.price_change_percentage_24h == -1.6
        assert eth_asset.total_volume_24h == 15000000000
        assert eth_asset.last_updated is not None  # This field exists in AssetResponse

        # Test result with active as false
        result = list_assets(active_only=False, limit=5, asset_dao=mock_dao)
        assert result is not None
        assert hasattr(result, 'assets')
        assert len(result.assets) == 3

        # Verify inactive asset has None values for CoinGecko attributes
        inactive_asset = result.assets[2]
        assert inactive_asset.asset_id == "INACTIVE"
        assert inactive_asset.is_active is False
        assert inactive_asset.symbol is None
        assert inactive_asset.image is None
        assert inactive_asset.market_cap_rank is None
        assert inactive_asset.high_24h is None
        assert inactive_asset.low_24h is None
        assert inactive_asset.circulating_supply is None
        assert inactive_asset.market_cap is None
        assert inactive_asset.price_change_percentage_24h is None
        assert inactive_asset.total_volume_24h is None
        # last_updated will have the updated_at value from the mock, not None
        assert inactive_asset.last_updated is not None


def test_list_assets_with_limit():
    """Test list_assets with limit parameter"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Create more mock assets with proper attributes
        mock_assets = []
        for i in range(5):
            mock_asset = MagicMock()
            mock_asset.asset_id = f"ASSET{i}"
            mock_asset.name = f"Asset {i}"
            mock_asset.description = f"Description for Asset {i}"
            mock_asset.category = "Test Category"
            mock_asset.price_usd = 100.0 + i
            mock_asset.is_active = True
            # Add new CoinGecko fields
            mock_asset.symbol = f"ASSET{i}"
            mock_asset.image = f"https://example.com/asset{i}.png"
            mock_asset.market_cap_rank = 100 + i
            mock_asset.high_24h = 110.0 + i
            mock_asset.low_24h = 90.0 + i
            mock_asset.circulating_supply = 1000000 + (i * 100000)
            mock_asset.total_supply = 1000000 + (i * 100000)
            mock_asset.max_supply = 1000000 + (i * 100000)
            mock_asset.price_change_24h = 5.0 + i
            mock_asset.price_change_percentage_24h = 1.0 + (i * 0.5)
            mock_asset.price_change_percentage_7d = 2.0 + (i * 1.0)
            mock_asset.price_change_percentage_30d = 3.0 + (i * 1.5)
            mock_asset.market_cap = 100000000 + (i * 10000000)
            mock_asset.market_cap_change_24h = 1000000 + (i * 100000)
            mock_asset.market_cap_change_percentage_24h = 1.0 + (i * 0.2)
            mock_asset.total_volume_24h = 5000000 + (i * 500000)
            mock_asset.volume_change_24h = 100000 + (i * 10000)
            mock_asset.ath = 200.0 + (i * 20)
            mock_asset.ath_change_percentage = -10.0 - (i * 2)
            mock_asset.ath_date = "2021-11-10T14:24:11.849Z"
            mock_asset.atl = 50.0 + (i * 5)
            mock_asset.atl_change_percentage = 100.0 + (i * 10)
            mock_asset.atl_date = "2020-01-01T00:00:00.000Z"
            mock_asset.last_updated = "2025-08-30T21:49:33.955Z"
            mock_asset.sparkline_7d = {"prices": [100, 105, 110, 105, 100, 105, 100]}
            mock_asset.updated_at = "2025-08-30T21:49:33.955Z"
            mock_assets.append(mock_asset)

        mock_dao.get_all_assets.return_value = mock_assets

        # test with limit
        result = list_assets(active_only=True, limit=3, asset_dao=mock_dao)

        # Verify limit was applied
        assert len(result.assets) == 3
        assert result.assets[0].asset_id == "ASSET0"
        assert result.assets[1].asset_id == "ASSET1"
        assert result.assets[2].asset_id == "ASSET2"


def test_list_assets_without_limit():
    """Test list_assets without limit parameter"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Create mock assets
        mock_assets = []
        for i in range(3):
            mock_asset = MagicMock()
            mock_asset.asset_id = f"ASSET{i}"
            mock_asset.name = f"Asset {i}"
            mock_asset.description = f"Description for Asset {i}"
            mock_asset.category = "Test Category"
            mock_asset.price_usd = 100.0 + i
            mock_asset.is_active = True
            # Add new CoinGecko fields
            mock_asset.symbol = f"ASSET{i}"
            mock_asset.image = f"https://example.com/asset{i}.png"
            mock_asset.market_cap_rank = 100 + i
            mock_asset.high_24h = 110.0 + i
            mock_asset.low_24h = 90.0 + i
            mock_asset.circulating_supply = 1000000 + (i * 100000)
            mock_asset.total_supply = 1000000 + (i * 100000)
            mock_asset.max_supply = 1000000 + (i * 100000)
            mock_asset.price_change_24h = 5.0 + i
            mock_asset.price_change_percentage_24h = 1.0 + (i * 0.5)
            mock_asset.price_change_percentage_7d = 2.0 + (i * 1.0)
            mock_asset.price_change_percentage_30d = 3.0 + (i * 1.5)
            mock_asset.market_cap = 100000000 + (i * 10000000)
            mock_asset.market_cap_change_24h = 1000000 + (i * 100000)
            mock_asset.market_cap_change_percentage_24h = 1.0 + (i * 0.2)
            mock_asset.total_volume_24h = 5000000 + (i * 500000)
            mock_asset.volume_change_24h = 100000 + (i * 10000)
            mock_asset.ath = 200.0 + (i * 20)
            mock_asset.ath_change_percentage = -10.0 - (i * 2)
            mock_asset.ath_date = "2021-11-10T14:24:11.849Z"
            mock_asset.atl = 50.0 + (i * 5)
            mock_asset.atl_change_percentage = 100.0 + (i * 10)
            mock_asset.atl_date = "2020-01-01T00:00:00.000Z"
            mock_asset.last_updated = "2025-08-30T21:49:33.955Z"
            mock_asset.sparkline_7d = {"prices": [100, 105, 110, 105, 100, 105, 100]}
            mock_asset.updated_at = "2025-08-30T21:49:33.955Z"
            mock_assets.append(mock_asset)

        mock_dao.get_all_assets.return_value = mock_assets

        # test without limit
        result = list_assets(active_only=True, limit=None, asset_dao=mock_dao)

        # Verify all assets were returned
        assert len(result.assets) == 3


    def test_get_asset_by_id_success():
        """Test get_asset_by_id with valid asset ID"""
        with patch('controllers.assets.AssetDAO') as mock_dao_class:
            mock_dao = MagicMock()
            mock_dao_class.return_value = mock_dao

            # Create mock asset
            mock_asset = MagicMock()
            mock_asset.asset_id = "BTC"
            mock_asset.name = "Bitcoin"
            mock_asset.description = "Bitcoin cryptocurrency"
            mock_asset.category = "Cryptocurrency"
            mock_asset.price_usd = 45000.0
            mock_asset.is_active = True
            mock_asset.amount = 100.0  # Add amount for availability check
            # Add new CoinGecko fields
            mock_asset.symbol = "BTC"
            mock_asset.image = "https://assets.coingecko.com/coins/images/1/large/bitcoin.png"
            mock_asset.market_cap_rank = 1
            mock_asset.high_24h = 46000.0
            mock_asset.low_24h = 44000.0
            mock_asset.circulating_supply = 19500000
            mock_asset.total_supply = 21000000
            mock_asset.max_supply = 21000000
            mock_asset.price_change_24h = 500.0
            mock_asset.price_change_percentage_24h = 1.1
            mock_asset.price_change_percentage_7d = 5.2
            mock_asset.price_change_percentage_30d = 8.5
            mock_asset.market_cap = 850000000000
            mock_asset.market_cap_change_24h = 10000000000
            mock_asset.market_cap_change_percentage_24h = 1.2
            mock_asset.total_volume_24h = 25000000000
            mock_asset.volume_change_24h = 5000000000
            mock_asset.ath = 69000.0
            mock_asset.ath_change_percentage = -34.8
            mock_asset.ath_date = "2021-11-10T14:24:11.849Z"
            mock_asset.atl = 67.81
            mock_asset.atl_change_percentage = 66263.0
            mock_asset.atl_date = "2013-07-06T00:00:00.000Z"
            mock_asset.last_updated = "2025-08-30T21:49:33.955Z"
            mock_asset.sparkline_7d = {"prices": [44000, 45000, 46000, 45000, 44000, 45000, 45000]}
            mock_asset.updated_at = "2025-08-30T21:49:33.955Z"

            mock_dao.get_asset_by_id.return_value = mock_asset

            # test the function
            result = get_asset_by_id("BTC", asset_dao=mock_dao)

        # Verify AssetDAO was called with uppercase asset_id
        mock_dao.get_asset_by_id.assert_called_once_with("BTC")

        # Verify result
        assert result is not None
        assert hasattr(result, 'asset_id')
        assert result.asset_id == "BTC"


def test_get_asset_by_id_not_found():
    """Test get_asset_by_id with non-existent asset ID"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Mock DAO to return None (asset not found)
        mock_dao.get_asset_by_id.return_value = None

        # Test that the function raises the correct exception
        with pytest.raises(CNOPInventoryServerException) as exc_info:
            get_asset_by_id("INVALID", asset_dao=mock_dao)

        error = exc_info.value
        # Check that the error message contains the operation context
        assert "failed to get asset invalid" in str(error).lower()


    def test_get_asset_by_id_case_insensitive():
        """Test get_asset_by_id handles case insensitivity"""
        with patch('controllers.assets.AssetDAO') as mock_dao_class:
            mock_dao = MagicMock()
            mock_dao_class.return_value = mock_dao

            # Create mock asset
            mock_asset = MagicMock()
            mock_asset.asset_id = "BTC"
            mock_asset.name = "Bitcoin"
            mock_asset.description = "Bitcoin cryptocurrency"
            mock_asset.category = "Cryptocurrency"
            mock_asset.price_usd = 45000.0
            mock_asset.is_active = True
            mock_asset.amount = 100.0  # Add amount for availability check
            # Add new CoinGecko fields
            mock_asset.symbol = "BTC"
            mock_asset.image = "https://assets.coingecko.com/coins/images/1/large/bitcoin.png"
            mock_asset.market_cap_rank = 1
            mock_asset.high_24h = 46000.0
            mock_asset.low_24h = 44000.0
            mock_asset.circulating_supply = 19500000
            mock_asset.total_supply = 21000000
            mock_asset.max_supply = 21000000
            mock_asset.price_change_24h = 500.0
            mock_asset.price_change_percentage_24h = 1.1
            mock_asset.price_change_percentage_7d = 5.2
            mock_asset.price_change_percentage_30d = 8.5
            mock_asset.market_cap = 850000000000
            mock_asset.market_cap_change_24h = 10000000000
            mock_asset.market_cap_change_percentage_24h = 1.2
            mock_asset.total_volume_24h = 25000000000
            mock_asset.volume_change_24h = 5000000000
            mock_asset.ath = 69000.0
            mock_asset.ath_change_percentage = -34.8
            mock_asset.ath_date = "2021-11-10T14:24:11.849Z"
            mock_asset.atl = 67.81
            mock_asset.atl_change_percentage = 66263.0
            mock_asset.atl_date = "2013-07-06T00:00:00.000Z"
            mock_asset.last_updated = "2025-08-30T21:49:33.955Z"
            mock_asset.sparkline_7d = {"prices": [44000, 45000, 46000, 45000, 44000, 45000, 45000]}
            mock_asset.updated_at = "2025-08-30T21:49:33.955Z"

            mock_dao.get_asset_by_id.return_value = mock_asset

            # Test with lowercase input
            result = get_asset_by_id("btc", asset_dao=mock_dao)

        # Verify AssetDAO was called with uppercase asset_id
        mock_dao.get_asset_by_id.assert_called_once_with("BTC")

        # Verify result
        assert result is not None
        assert result.asset_id == "BTC"


# ========================================
# COMPREHENSIVE EXCEPTION HANDLING TESTS
# ========================================

class TestAssetsControllerExceptionHandling:
    """Comprehensive tests for exception handling in assets controller"""

    def test_list_assets_database_error_handling(self):
        """Test that database errors are properly converted to internal exceptions"""
        # Mock the asset DAO to raise an exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_all_assets.side_effect = Exception("Database connection failed")

        with pytest.raises(CNOPInventoryServerException) as exc_info:
            list_assets(active_only=True, limit=10, asset_dao=mock_asset_dao)

        error = exc_info.value
        # Check that the error message contains the operation context
        assert "failed to list assets" in str(error).lower()

    def test_get_asset_by_id_database_error_handling(self):
        """Test that database errors in get_asset_by_id are properly handled"""
        # Mock the asset DAO to raise an exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_asset_by_id.side_effect = Exception("Database query failed")

        with pytest.raises(CNOPInventoryServerException) as exc_info:
            get_asset_by_id("BTC", asset_dao=mock_asset_dao)

        error = exc_info.value
        # Check that the error message contains the operation context
        assert "failed to get asset btc" in str(error).lower()

    def test_list_assets_with_common_package_exception(self):
        """Test handling of common package exceptions in list_assets"""
        # Mock the asset DAO to raise a common package exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_all_assets.side_effect = CNOPDatabaseOperationException(
            "Connection failed", service="dynamodb"
        )

        with pytest.raises(CNOPInventoryServerException) as exc_info:
            list_assets(active_only=True, limit=10, asset_dao=mock_asset_dao)

        error = exc_info.value
        # Check that the error message contains the operation context
        assert "failed to list assets" in str(error).lower()

    def test_get_asset_by_id_with_common_package_exception(self):
        """Test handling of common package exceptions in get_asset_by_id"""
        # Mock the asset DAO to raise a common package exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_asset_by_id.side_effect = CNOPDatabaseOperationException(
            "Operation failed", operation="get_item"
        )

        with pytest.raises(CNOPInventoryServerException) as exc_info:
            get_asset_by_id("BTC", asset_dao=mock_asset_dao)

        error = exc_info.value
        # Check that the error message contains the operation context
        assert "failed to get asset btc" in str(error).lower()

    def test_assets_controller_error_context(self):
        """Test that assets controller provides proper error context"""
        # Mock the asset DAO to raise an exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_asset_by_id.side_effect = Exception("Test database error")

        with pytest.raises(CNOPInventoryServerException) as exc_info:
            get_asset_by_id("BTC", asset_dao=mock_asset_dao)

        error = exc_info.value
        # Check that the error has proper context
        assert "failed to get asset btc" in str(error).lower()
        assert "Test database error" in str(error)

    def test_assets_controller_exception_flow(self):
        """Test the complete exception flow in assets controller"""
        # Mock the asset DAO to raise a common package exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_all_assets.side_effect = CNOPDatabaseOperationException(
            "Connection failed", service="dynamodb", region="us-east-1"
        )

        with pytest.raises(CNOPInventoryServerException) as exc_info:
            list_assets(active_only=True, limit=5, asset_dao=mock_asset_dao)

        error = exc_info.value
        # Verify the error is properly wrapped
        assert isinstance(error, CNOPInventoryServerException)
        assert "failed to list assets" in str(error).lower()

    def test_assets_controller_with_complex_exception(self):
        """Test assets controller with complex nested exceptions"""
        # Create a complex nested exception
        class ComplexDatabaseError(Exception):
            def __init__(self, message, details):
                self.message = message
                self.details = details
                super().__init__(message)

        complex_error = ComplexDatabaseError("Complex error", {"level": "critical", "retry_count": 3})

        # Mock the asset DAO to raise the complex exception
        mock_asset_dao = MagicMock()
        mock_asset_dao.get_asset_by_id.side_effect = complex_error

        with pytest.raises(CNOPInventoryServerException) as exc_info:
            get_asset_by_id("BTC", asset_dao=mock_asset_dao)

        error = exc_info.value
        assert "failed to get asset btc" in str(error).lower()
        assert "Complex error" in str(error)

    def test_assets_controller_with_multiple_exceptions(self):
        """Test assets controller handling multiple types of exceptions"""
        # Test with different exception types
        exceptions_to_test = [
            (Exception("Generic exception"), CNOPInventoryServerException),
            (RuntimeError("Runtime error"), CNOPInventoryServerException),
            (CNOPDatabaseOperationException("Connection error", service="dynamodb"), CNOPInventoryServerException),
            (CNOPDatabaseOperationException("Operation error", operation="scan"), CNOPInventoryServerException)
        ]

        for exc, expected_exception_type in exceptions_to_test:
            mock_asset_dao = MagicMock()
            mock_asset_dao.get_asset_by_id.side_effect = exc

            with pytest.raises(expected_exception_type) as exc_info:
                get_asset_by_id("BTC", asset_dao=mock_asset_dao)

            error = exc_info.value
            assert isinstance(error, expected_exception_type)
            if expected_exception_type == CNOPInventoryServerException:
                assert "failed to get asset btc" in str(error).lower()

    def test_assets_controller_validation_error_handling(self):
        """Test assets controller handling validation errors"""
        # Test with validation errors that should be converted to AssetValidationException
        validation_errors = [
            CNOPAssetValidationException("Asset ID cannot be empty"),
            CNOPAssetValidationException("Asset ID contains potentially malicious content"),
            CNOPAssetValidationException("Asset ID must be 1-10 alphanumeric characters")
        ]

        for validation_error in validation_errors:
            mock_asset_dao = MagicMock()
            mock_asset_dao.get_asset_by_id.side_effect = validation_error

            with pytest.raises(CNOPAssetValidationException) as exc_info:
                get_asset_by_id("BTC", asset_dao=mock_asset_dao)

            error = exc_info.value
            assert isinstance(error, CNOPAssetValidationException)
            # Check that the error message contains the expected content from the validation_error
            assert str(validation_error) in str(error)


def test_list_assets_metrics_recording():
    """Test list_assets with metrics recording (lines 40-41)"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class, \
         patch('controllers.assets.METRICS_AVAILABLE', True), \
         patch('controllers.assets.record_asset_retrieval') as mock_record_retrieval, \
         patch('controllers.assets.update_asset_counts') as mock_update_counts:

        # Setup mock AssetDAO
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Mock asset data
        mock_asset1 = MagicMock()
        mock_asset1.asset_id = "BTC"
        mock_asset1.name = "Bitcoin"
        mock_asset1.description = "Bitcoin cryptocurrency"
        mock_asset1.category = "Cryptocurrency"
        mock_asset1.price_usd = 45000.0
        mock_asset1.is_active = True
        # Add new CoinGecko fields
        mock_asset1.symbol = "BTC"
        mock_asset1.image = "https://assets.coingecko.com/coins/images/1/large/bitcoin.png"
        mock_asset1.market_cap_rank = 1
        mock_asset1.high_24h = 46000.0
        mock_asset1.low_24h = 44000.0
        mock_asset1.circulating_supply = 19500000
        mock_asset1.total_supply = 21000000
        mock_asset1.max_supply = 21000000
        mock_asset1.price_change_24h = 500.0
        mock_asset1.price_change_percentage_24h = 1.1
        mock_asset1.price_change_percentage_7d = 5.2
        mock_asset1.price_change_percentage_30d = 8.5
        mock_asset1.market_cap = 850000000000
        mock_asset1.market_cap_change_24h = 10000000000
        mock_asset1.market_cap_change_percentage_24h = 1.2
        mock_asset1.total_volume_24h = 25000000000
        mock_asset1.volume_change_24h = 5000000000
        mock_asset1.ath = 69000.0
        mock_asset1.ath_change_percentage = -34.8
        mock_asset1.ath_date = "2021-11-10T14:24:11.849Z"
        mock_asset1.atl = 67.81
        mock_asset1.atl_change_percentage = 66263.0
        mock_asset1.atl_date = "2013-07-06T00:00:00.000Z"
        mock_asset1.last_updated = "2025-08-30T21:49:33.955Z"
        mock_asset1.sparkline_7d = {"prices": [44000, 45000, 46000, 45000, 44000, 45000, 45000]}
        mock_asset1.updated_at = "2025-08-30T21:49:33.955Z"

        mock_asset2 = MagicMock()
        mock_asset2.asset_id = "ETH"
        mock_asset2.name = "Ethereum"
        mock_asset2.description = "Ethereum cryptocurrency"
        mock_asset2.category = "Cryptocurrency"
        mock_asset2.price_usd = 3000.0
        mock_asset2.is_active = True
        # Add new CoinGecko fields
        mock_asset2.symbol = "ETH"
        mock_asset2.image = "https://assets.coingecko.com/coins/images/279/large/ethereum.png"
        mock_asset2.market_cap_rank = 2
        mock_asset2.high_24h = 3100.0
        mock_asset2.low_24h = 2900.0
        mock_asset2.circulating_supply = 120000000
        mock_asset2.total_supply = 120000000
        mock_asset2.max_supply = None
        mock_asset2.price_change_24h = -50.0
        mock_asset2.price_change_percentage_24h = -1.6
        mock_asset2.price_change_percentage_7d = -2.1
        mock_asset2.price_change_percentage_30d = -5.2
        mock_asset2.market_cap = 350000000000
        mock_asset2.market_cap_change_24h = -5000000000
        mock_asset2.market_cap_change_percentage_24h = -1.4
        mock_asset2.total_volume_24h = 15000000000
        mock_asset2.volume_change_24h = -2000000000
        mock_asset2.ath = 4878.26
        mock_asset2.ath_change_percentage = -38.5
        mock_asset2.ath_date = "2021-11-10T14:24:11.849Z"
        mock_asset2.atl = 0.432979
        mock_asset2.atl_change_percentage = 692866.0
        mock_asset2.atl_date = "2020-01-20T00:00:00.000Z"
        mock_asset2.last_updated = "2025-08-30T21:49:33.955Z"
        mock_asset2.sparkline_7d = {"prices": [3100, 3000, 2900, 3000, 3100, 3000, 3000]}
        mock_asset2.updated_at = "2025-08-30T21:49:33.955Z"

        # Mock inactive asset for total count
        mock_asset3 = MagicMock()
        mock_asset3.asset_id = "INACTIVE"
        mock_asset3.name = "Inactive Asset"
        mock_asset3.description = "Inactive asset"
        mock_asset3.category = "Test"
        mock_asset3.price_usd = 100.0
        mock_asset3.is_active = False
        # Add new CoinGecko fields (can be None for inactive assets)
        mock_asset3.symbol = None
        mock_asset3.image = None
        mock_asset3.market_cap_rank = None
        mock_asset3.high_24h = None
        mock_asset3.low_24h = None
        mock_asset3.circulating_supply = None
        mock_asset3.total_supply = None
        mock_asset3.max_supply = None
        mock_asset3.price_change_24h = None
        mock_asset3.price_change_percentage_24h = None
        mock_asset3.price_change_percentage_7d = None
        mock_asset3.price_change_percentage_30d = None
        mock_asset3.market_cap = None
        mock_asset3.market_cap_change_24h = None
        mock_asset3.market_cap_change_percentage_24h = None
        mock_asset3.total_volume_24h = None
        mock_asset3.volume_change_24h = None
        mock_asset3.ath = None
        mock_asset3.ath_change_percentage = None
        mock_asset3.ath_date = None
        mock_asset3.atl = None
        mock_asset3.atl_change_percentage = None
        mock_asset3.atl_date = None
        mock_asset3.last_updated = None
        mock_asset3.sparkline_7d = None
        mock_asset3.updated_at = "2025-08-30T21:49:33.955Z"

        # Setup mock to return different results based on active_only parameter
        def mock_get_all_assets(active_only=True):
            if active_only:
                return [mock_asset1, mock_asset2]
            else:
                return [mock_asset1, mock_asset2, mock_asset3]

        mock_dao.get_all_assets.side_effect = mock_get_all_assets

        # test the function
        result = list_assets(active_only=True, limit=2, asset_dao=mock_dao)

        # Verify metrics were recorded
        mock_record_retrieval.assert_called_once_with(category="all", active_only=True)
        mock_update_counts.assert_called_once_with(total=3, active=2)

        # Verify result structure
        assert result is not None
        assert hasattr(result, 'assets')
        assert len(result.assets) == 2


def test_get_asset_by_id_validation_error_handling():
    """Test get_asset_by_id with AssetValidationException handling (lines 172-176)"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class, \
         patch('controllers.assets.validate_asset_exists') as mock_validate, \
         patch('controllers.assets.METRICS_AVAILABLE', True), \
         patch('controllers.assets.record_asset_detail_view') as mock_record_view:

        # Setup mock AssetDAO
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Mock asset data with all required attributes
        mock_asset = MagicMock()
        mock_asset.asset_id = "BTC"
        mock_asset.name = "Bitcoin"
        mock_asset.description = "Bitcoin cryptocurrency"
        mock_asset.category = "Cryptocurrency"
        mock_asset.price_usd = 45000.0
        mock_asset.is_active = True
        mock_asset.amount = 100.0  # Add amount attribute
        mock_asset.market_cap = 850000000000
        mock_asset.volume_24h = 25000000000
        mock_asset.created_at = "2024-01-01T00:00:00Z"
        mock_asset.updated_at = "2024-01-01T00:00:00Z"
        # Add new CoinGecko fields
        mock_asset.symbol = "BTC"
        mock_asset.image = "https://assets.coingecko.com/coins/images/1/large/bitcoin.png"
        mock_asset.market_cap_rank = 1
        mock_asset.high_24h = 46000.0
        mock_asset.low_24h = 44000.0
        mock_asset.circulating_supply = 19500000
        mock_asset.total_supply = 21000000
        mock_asset.max_supply = 21000000
        mock_asset.price_change_24h = 500.0
        mock_asset.price_change_percentage_24h = 1.1
        mock_asset.price_change_percentage_7d = 5.2
        mock_asset.price_change_percentage_30d = 8.5
        mock_asset.market_cap_change_24h = 10000000000
        mock_asset.market_cap_change_percentage_24h = 1.2
        mock_asset.total_volume_24h = 25000000000
        mock_asset.volume_change_24h = 5000000000
        mock_asset.ath = 69000.0
        mock_asset.ath_change_percentage = -34.8
        mock_asset.ath_date = "2021-11-10T14:24:11.849Z"
        mock_asset.atl = 67.81
        mock_asset.atl_change_percentage = 66263.0
        mock_asset.atl_date = "2013-07-06T00:00:00.000Z"
        mock_asset.last_updated = "2025-08-30T21:49:33.955Z"
        mock_asset.sparkline_7d = {"prices": [44000, 45000, 46000, 45000, 44000, 45000, 45000]}

        # Setup mocks
        mock_dao.get_asset_by_id.return_value = mock_asset
        mock_validate.return_value = None  # No validation error

        # Test successful case first
        result = get_asset_by_id("BTC", asset_dao=mock_dao)

        # Verify validation was called
        mock_validate.assert_called_once_with("BTC", mock_dao)

        # Verify metrics were recorded
        mock_record_view.assert_called_once_with(asset_id="BTC")

        # Now test with AssetValidationException
        mock_validate.side_effect = CNOPAssetValidationException("Asset ID cannot be empty")

        with pytest.raises(CNOPAssetValidationException) as exc_info:
            get_asset_by_id("INVALID", asset_dao=mock_dao)

        # Verify the exception message is properly formatted
        # The actual format is: "CNOPAssetValidationException: Asset ID cannot be empty"
        assert "Asset ID cannot be empty" in str(exc_info.value)


def test_get_asset_by_id_metrics_recording():
    """Test get_asset_by_id with metrics recording when METRICS_AVAILABLE is True"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class, \
         patch('controllers.assets.validate_asset_exists') as mock_validate, \
         patch('controllers.assets.METRICS_AVAILABLE', True), \
         patch('controllers.assets.record_asset_detail_view') as mock_record_view:

        # Setup mock AssetDAO
        mock_dao = MagicMock()
        mock_dao_class.return_value = mock_dao

        # Mock asset data with all required attributes
        mock_asset = MagicMock()
        mock_asset.asset_id = "ETH"
        mock_asset.name = "Ethereum"
        mock_asset.description = "Ethereum cryptocurrency"
        mock_asset.category = "Cryptocurrency"
        mock_asset.price_usd = 3000.0
        mock_asset.is_active = True
        mock_asset.amount = 5000.0  # Add amount attribute
        mock_asset.market_cap = 350000000000
        mock_asset.volume_24h = 15000000000
        mock_asset.created_at = "2024-01-01T00:00:00Z"
        mock_asset.updated_at = "2024-01-01T00:00:00Z"
        # Add new CoinGecko fields
        mock_asset.symbol = "ETH"
        mock_asset.image = "https://assets.coingecko.com/coins/images/279/large/ethereum.png"
        mock_asset.market_cap_rank = 2
        mock_asset.high_24h = 3100.0
        mock_asset.low_24h = 2900.0
        mock_asset.circulating_supply = 120000000
        mock_asset.total_supply = 120000000
        mock_asset.max_supply = None
        mock_asset.price_change_24h = -50.0
        mock_asset.price_change_percentage_24h = -1.6
        mock_asset.price_change_percentage_7d = -2.1
        mock_asset.price_change_percentage_30d = -5.2
        mock_asset.market_cap_change_24h = -5000000000
        mock_asset.market_cap_change_percentage_24h = -1.4
        mock_asset.total_volume_24h = 15000000000
        mock_asset.volume_change_24h = -2000000000
        mock_asset.ath = 4878.26
        mock_asset.ath_change_percentage = -38.5
        mock_asset.ath_date = "2021-11-10T14:24:11.849Z"
        mock_asset.atl = 0.432979
        mock_asset.atl_change_percentage = 692866.0
        mock_asset.atl_date = "2020-01-20T00:00:00.000Z"
        mock_asset.last_updated = "2025-08-30T21:49:33.955Z"
        mock_asset.sparkline_7d = {"prices": [3100, 3000, 2900, 3000, 3100, 3000, 3000]}

        # Setup mocks
        mock_dao.get_asset_by_id.return_value = mock_asset
        mock_validate.return_value = None  # No validation error

        # Test the function
        result = get_asset_by_id("ETH", asset_dao=mock_dao)

        # Verify metrics were recorded
        mock_record_view.assert_called_once_with(asset_id="ETH")

        # Verify result structure
        assert result is not None


class TestMetricsImportFailure:
    """Test scenarios when metrics module is not available"""

    @patch('controllers.assets.METRICS_AVAILABLE', False)
    def test_list_assets_without_metrics(self):
        """Test list_assets when metrics module is not available"""
        with patch('controllers.assets.AssetDAO') as mock_dao_class:
            # Setup mock AssetDAO
            mock_dao = MagicMock()
            mock_dao_class.return_value = mock_dao

            # Mock asset data
            mock_asset = MagicMock()
            mock_asset.asset_id = "BTC"
            mock_asset.name = "Bitcoin"
            mock_asset.description = "Bitcoin cryptocurrency"
            mock_asset.category = "Cryptocurrency"
            mock_asset.price_usd = 45000.0
            mock_asset.is_active = True
            mock_asset.symbol = "BTC"
            mock_asset.image = "https://example.com/btc.png"
            mock_asset.market_cap_rank = 1
            mock_asset.market_cap = 1000000000
            mock_asset.total_volume_24h = 50000
            mock_asset.price_change_percentage_24h = 5.0
            mock_asset.high_24h = 46000.0
            mock_asset.low_24h = 44000.0
            mock_asset.circulating_supply = 19500000
            mock_asset.updated_at = None

            # Mock DAO methods
            mock_dao.get_all_assets.return_value = [mock_asset]

            # Test the function
            result = list_assets(active_only=True, limit=1, asset_dao=mock_dao)

            # Should work without metrics
            assert result.total_count == 1
            assert result.filtered_count == 1
            assert result.active_count == 1
            assert len(result.assets) == 1

    @patch('controllers.assets.METRICS_AVAILABLE', False)
    def test_get_asset_by_id_without_metrics(self):
        """Test get_asset_by_id when metrics module is not available"""
        with patch('controllers.assets.AssetDAO') as mock_dao_class:
            # Setup mock AssetDAO
            mock_dao = MagicMock()
            mock_dao_class.return_value = mock_dao

            # Mock asset data
            mock_asset = MagicMock()
            mock_asset.asset_id = "BTC"
            mock_asset.name = "Bitcoin"
            mock_asset.description = "Bitcoin cryptocurrency"
            mock_asset.category = "Cryptocurrency"
            mock_asset.price_usd = 45000.0
            mock_asset.is_active = True
            mock_asset.amount = 100
            mock_asset.symbol = "BTC"
            mock_asset.image = "https://example.com/btc.png"
            mock_asset.market_cap_rank = 1
            mock_asset.market_cap = 1000000000
            mock_asset.price_change_24h = 500.0
            mock_asset.price_change_percentage_24h = 5.0
            mock_asset.price_change_percentage_7d = 5.2
            mock_asset.price_change_percentage_30d = 8.5
            mock_asset.high_24h = 46000.0
            mock_asset.low_24h = 44000.0
            mock_asset.total_volume_24h = 50000
            mock_asset.circulating_supply = 19500000
            mock_asset.total_supply = 21000000
            mock_asset.max_supply = 21000000
            mock_asset.ath = 69000.0
            mock_asset.ath_change_percentage = -34.8
            mock_asset.ath_date = "2021-11-10T14:24:11.849Z"
            mock_asset.atl = 67.81
            mock_asset.atl_change_percentage = 66263.0
            mock_asset.atl_date = "2013-07-06T00:00:00.000Z"
            mock_asset.updated_at = "2025-08-30T21:49:33.955Z"

            # Mock DAO methods
            mock_dao.get_asset_by_id.return_value = mock_asset

            # Test the function
            result = get_asset_by_id("BTC", asset_dao=mock_dao)

            # Should work without metrics
            assert result.asset_id == "BTC"
            assert result.name == "Bitcoin"


class TestValidationErrorHandling:
    """Test validation error handling scenarios"""

    def test_get_asset_by_id_validation_error_asset_id(self):
        """Test validation error when asset_id is invalid"""
        with patch('controllers.assets.AssetDAO') as mock_dao_class:
            # Setup mock AssetDAO
            mock_dao = MagicMock()
            mock_dao_class.return_value = mock_dao

            # Mock validation to fail
            with patch('controllers.assets.AssetIdRequest') as mock_request_class:
                mock_request = MagicMock()
                mock_request_class.side_effect = ValueError("Invalid asset_id format")
                mock_request_class.return_value = mock_request

                # Test that validation error is converted to internal server exception
                with pytest.raises(CNOPInventoryServerException, match="Failed to get asset invalid-asset-id"):
                    get_asset_by_id("invalid-asset-id", asset_dao=mock_dao)

    def test_get_asset_by_id_validation_error_asset_id_logging(self):
        """Test validation error logging when asset_id is invalid"""
        with patch('controllers.assets.AssetDAO') as mock_dao_class:
            # Setup mock AssetDAO
            mock_dao = MagicMock()
            mock_dao_class.return_value = mock_dao

            # Mock validation to fail
            with patch('controllers.assets.AssetIdRequest') as mock_request_class:
                mock_request = MagicMock()
                mock_request_class.side_effect = ValueError("Invalid asset_id format")
                mock_request_class.return_value = mock_request

                # Mock logger to capture warning and error
                with patch('controllers.assets.logger') as mock_logger:
                    with pytest.raises(CNOPInventoryServerException):
                        get_asset_by_id("invalid-asset-id", asset_dao=mock_dao)

                    # Check that warning was logged for validation error
                    mock_logger.warning.assert_called_once()
                    # Check that error was logged for the final exception
                    mock_logger.error.assert_called_once()

    def test_get_asset_by_id_cnop_validation_exception(self):
        """Test that CNOPAssetValidationException is properly caught and re-raised"""
        with patch('controllers.assets.AssetDAO') as mock_dao_class:
            # Setup mock AssetDAO
            mock_dao = MagicMock()
            mock_dao_class.return_value = mock_dao

            # Mock validation to succeed
            with patch('controllers.assets.AssetIdRequest') as mock_request_class:
                mock_request = MagicMock()
                mock_request.asset_id = "BTC"
                mock_request_class.return_value = mock_request

                # Mock business validation to raise CNOPAssetValidationException
                with patch('controllers.assets.validate_asset_exists') as mock_validate:
                    mock_validate.side_effect = CNOPAssetValidationException("Asset ID cannot be empty")

                    # Test that CNOPAssetValidationException is re-raised as-is
                    with pytest.raises(CNOPAssetValidationException, match="Asset ID cannot be empty"):
                        get_asset_by_id("BTC", asset_dao=mock_dao)


class TestExceptionHandling:
    """Test exception handling scenarios"""

    def test_get_asset_by_id_database_exception(self):
        """Test handling of database exceptions"""
        with patch('controllers.assets.AssetDAO') as mock_dao_class:
            # Setup mock AssetDAO
            mock_dao = MagicMock()
            mock_dao_class.return_value = mock_dao

            # Mock validation to succeed
            with patch('controllers.assets.AssetIdRequest') as mock_request_class:
                mock_request = MagicMock()
                mock_request.asset_id = "BTC"
                mock_request_class.return_value = mock_request

                # Mock business validation to succeed
                with patch('controllers.assets.validate_asset_exists'):
                    # Mock DAO to raise database exception
                    mock_dao.get_asset_by_id.side_effect = CNOPDatabaseOperationException("Database connection failed")

                    # Test that database exception is converted to internal server exception
                    with pytest.raises(CNOPInventoryServerException, match="Failed to get asset BTC"):
                        get_asset_by_id("BTC", asset_dao=mock_dao)

    def test_get_asset_by_id_unexpected_exception(self):
        """Test handling of unexpected exceptions"""
        with patch('controllers.assets.AssetDAO') as mock_dao_class:
            # Setup mock AssetDAO
            mock_dao = MagicMock()
            mock_dao_class.return_value = mock_dao

            # Mock validation to succeed
            with patch('controllers.assets.AssetIdRequest') as mock_request_class:
                mock_request = MagicMock()
                mock_request.asset_id = "BTC"
                mock_request_class.return_value = mock_request

                # Mock business validation to succeed
                with patch('controllers.assets.validate_asset_exists'):
                    # Mock DAO to raise unexpected exception
                    mock_dao.get_asset_by_id.side_effect = RuntimeError("Unexpected runtime error")

                    # Test that unexpected exception is converted to internal server exception
                    with pytest.raises(CNOPInventoryServerException, match="Failed to get asset BTC"):
                        get_asset_by_id("BTC", asset_dao=mock_dao)
