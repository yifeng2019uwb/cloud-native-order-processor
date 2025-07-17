import pytest
import os
import sys
from unittest.mock import AsyncMock, patch, MagicMock

# Add the necessary paths to sys.path before importing the controller
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))  # for common
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))  # for api_models

# Import the controller functions directly
from controllers.assets import list_assets, get_asset_by_id


@pytest.mark.asyncio
async def test_list_assets_success():
    """Test list_assets with mocked AssetDAO"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        # Setup mock AssetDAO
        mock_dao = AsyncMock()
        mock_dao_class.return_value = mock_dao

        # Mock asset data with proper attributes
        mock_asset1 = MagicMock()
        mock_asset1.asset_id = "BTC"
        mock_asset1.name = "Bitcoin"
        mock_asset1.description = "Bitcoin cryptocurrency"
        mock_asset1.category = "Cryptocurrency"
        mock_asset1.price_usd = 45000.0
        mock_asset1.is_active = True

        mock_asset2 = MagicMock()
        mock_asset2.asset_id = "ETH"
        mock_asset2.name = "Ethereum"
        mock_asset2.description = "Ethereum cryptocurrency"
        mock_asset2.category = "Cryptocurrency"
        mock_asset2.price_usd = 3000.0
        mock_asset2.is_active = True

        # Mock inactive asset for total count
        mock_asset3 = MagicMock()
        mock_asset3.asset_id = "INACTIVE"
        mock_asset3.name = "Inactive Asset"
        mock_asset3.description = "Inactive asset"
        mock_asset3.category = "Test"
        mock_asset3.price_usd = 100.0
        mock_asset3.is_active = False

        # Setup mock to return different results based on active_only parameter
        def mock_get_all_assets(active_only=True):
            if active_only:
                return [mock_asset1, mock_asset2]
            else:
                return [mock_asset1, mock_asset2, mock_asset3]

        mock_dao.get_all_assets.side_effect = mock_get_all_assets

        # test the function
        result = await list_assets(active_only=True, limit=2, asset_dao=mock_dao)

        # Verify AssetDAO was called correctly (twice: once for active, once for total)
        assert mock_dao.get_all_assets.call_count == 2
        mock_dao.get_all_assets.assert_any_call(active_only=True)
        mock_dao.get_all_assets.assert_any_call(active_only=False)

        # Verify result structure
        assert result is not None
        assert hasattr(result, 'assets')
        assert len(result.assets) == 2

        # Test result with active as false
        result = await list_assets(active_only=False, limit=5, asset_dao=mock_dao)
        assert result is not None
        assert hasattr(result, 'assets')
        assert len(result.assets) == 3


@pytest.mark.asyncio
async def test_list_assets_with_limit():
    """Test list_assets with limit parameter"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        mock_dao = AsyncMock()
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
            mock_assets.append(mock_asset)

        mock_dao.get_all_assets.return_value = mock_assets

        # test with limit
        result = await list_assets(active_only=True, limit=3, asset_dao=mock_dao)

        # Verify limit was applied
        assert len(result.assets) == 3


@pytest.mark.asyncio
async def test_list_assets_without_limit():
    """Test list_assets without limit parameter"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        mock_dao = AsyncMock()
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
            mock_assets.append(mock_asset)

        mock_dao.get_all_assets.return_value = mock_assets

        # test without limit
        result = await list_assets(active_only=True, limit=None, asset_dao=mock_dao)

        # Verify all assets returned
        assert len(result.assets) == 3


@pytest.mark.asyncio
async def test_get_asset_by_id_success():
    """Test get_asset_by_id when asset exists"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        mock_dao = AsyncMock()
        mock_dao_class.return_value = mock_dao

        # Mock found asset with proper attributes
        mock_asset = MagicMock()
        mock_asset.asset_id = "BTC"
        mock_asset.name = "Bitcoin"
        mock_asset.description = "Bitcoin cryptocurrency"
        mock_asset.category = "Cryptocurrency"
        mock_asset.price_usd = 45000.0
        mock_asset.is_active = True
        mock_asset.amount = 100.0  # Add amount for availability check

        mock_dao.get_asset_by_id.return_value = mock_asset

        # test the function
        result = await get_asset_by_id("BTC", asset_dao=mock_dao)

        # Verify AssetDAO was called correctly
        mock_dao.get_asset_by_id.assert_called_once_with("BTC")

        # Verify result
        assert result is not None


@pytest.mark.asyncio
async def test_get_asset_by_id_not_found():
    """Test get_asset_by_id when asset doesn't exist"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        mock_dao = AsyncMock()
        mock_dao_class.return_value = mock_dao

        # Mock asset not found
        mock_dao.get_asset_by_id.return_value = None

        # test that HTTPException is raised
        with pytest.raises(Exception):  # HTTPException will be raised
            await get_asset_by_id("INVALID", asset_dao=mock_dao)

        # Verify AssetDAO was called
        mock_dao.get_asset_by_id.assert_called_once_with("INVALID")


@pytest.mark.asyncio
async def test_get_asset_by_id_case_insensitive():
    """Test get_asset_by_id handles case insensitivity"""
    with patch('controllers.assets.AssetDAO') as mock_dao_class:
        mock_dao = AsyncMock()
        mock_dao_class.return_value = mock_dao

        # Mock found asset
        mock_asset = MagicMock()
        mock_asset.asset_id = "BTC"
        mock_asset.name = "Bitcoin"
        mock_asset.description = "Bitcoin cryptocurrency"
        mock_asset.category = "Cryptocurrency"
        mock_asset.price_usd = 45000.0
        mock_asset.is_active = True
        mock_asset.amount = 100.0

        mock_dao.get_asset_by_id.return_value = mock_asset

        # test with lowercase
        result = await get_asset_by_id("btc", asset_dao=mock_dao)

        # Verify AssetDAO was called with uppercase
        mock_dao.get_asset_by_id.assert_called_once_with("BTC")

        # Verify result
        assert result is not None
