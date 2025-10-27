"""
Unit tests for assets controller
Path: services/inventory-service/tests/controllers/test_assets.py
"""
import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from fastapi import Request
from decimal import Decimal
from datetime import datetime, timezone

# Add the necessary paths to sys.path before importing the controller
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # for dependency_constants
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))  # for common
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))  # for api_models

# Import dependency constants
from dependency_constants import PATCH_VALIDATE_ASSET_EXISTS, PATCH_GET_REQUEST_ID

# Import the controller functions directly
from controllers.assets import list_assets, get_asset, get_asset_request

# Import exception classes for testing
from inventory_exceptions import CNOPAssetValidationException, CNOPInventoryServerException
from common.exceptions import CNOPAssetNotFoundException
from common.data.entities.inventory import Asset
from api_models.list_assets import ListAssetsRequest, ListAssetsResponse
from api_models.get_asset import GetAssetRequest, GetAssetResponse
from api_models.shared.data_models import AssetData, AssetDetailData


def create_test_asset_btc():
    """Create a real BTC Asset object for testing"""
    return Asset(
        asset_id="BTC",
        name="Bitcoin",
        description="Bitcoin cryptocurrency",
        category="Cryptocurrency",
        amount=Decimal("1000000"),
        price_usd=Decimal("45000.0"),
        is_active=True,
        symbol="BTC",
        image="https://example.com/btc.png",
        market_cap_rank=1,
        current_price=Decimal("45000.0"),
        high_24h=Decimal("46000.0"),
        low_24h=Decimal("44000.0"),
        circulating_supply=Decimal("19500000"),
        total_supply=Decimal("21000000"),
        max_supply=Decimal("21000000"),
        price_change_24h=Decimal("500.0"),
        price_change_percentage_24h=Decimal("1.1"),
        price_change_percentage_7d=Decimal("5.2"),
        price_change_percentage_30d=Decimal("8.5"),
        market_cap=Decimal("850000000000"),
        market_cap_change_24h=Decimal("10000000000"),
        market_cap_change_percentage_24h=Decimal("1.2"),
        total_volume_24h=Decimal("25000000000"),
        volume_change_24h=Decimal("5000000000"),
        ath=Decimal("69000.0"),
        ath_change_percentage=Decimal("-34.8"),
        ath_date="2021-11-10T14:24:11.849Z",
        atl=Decimal("67.81"),
        atl_change_percentage=Decimal("66263.0"),
        atl_date="2013-07-06T00:00:00.000Z",
        last_updated="2025-08-30T21:49:33.955Z",
        sparkline_7d={"prices": [44000, 45000, 46000, 45000, 44000, 45000, 45000]},
        updated_at=datetime.now(timezone.utc)
    )


def create_test_asset_eth():
    """Create a real ETH Asset object for testing"""
    return Asset(
        asset_id="ETH",
        name="Ethereum",
        description="Ethereum cryptocurrency",
        category="Cryptocurrency",
        amount=Decimal("2000000"),
        price_usd=Decimal("3000.0"),
        is_active=True,
        symbol="ETH",
        image="https://example.com/eth.png",
        market_cap_rank=2,
        current_price=Decimal("3000.0"),
        high_24h=Decimal("3100.0"),
        low_24h=Decimal("2900.0"),
        circulating_supply=Decimal("120000000"),
        total_supply=Decimal("120000000"),
        max_supply=None,
        price_change_24h=Decimal("-50.0"),
        price_change_percentage_24h=Decimal("-1.6"),
        price_change_percentage_7d=Decimal("-2.1"),
        price_change_percentage_30d=Decimal("-5.2"),
        market_cap=Decimal("350000000000"),
        market_cap_change_24h=Decimal("-5000000000"),
        market_cap_change_percentage_24h=Decimal("-1.4"),
        total_volume_24h=Decimal("15000000000"),
        volume_change_24h=Decimal("-2000000000"),
        ath=Decimal("4878.26"),
        ath_change_percentage=Decimal("-38.5"),
        ath_date="2021-11-10T14:24:11.849Z",
        atl=Decimal("0.432979"),
        atl_change_percentage=Decimal("692866.0"),
        atl_date="2020-01-20T00:00:00.000Z",
        last_updated="2025-08-30T21:49:33.955Z",
        sparkline_7d={"prices": [3100, 3000, 2900, 3000, 3100, 3000, 3000]},
        updated_at=datetime.now(timezone.utc)
    )


def create_test_asset_inactive():
    """Create an inactive asset for testing"""
    asset = create_test_asset_btc()
    asset.is_active = False
    return asset


def create_test_request():
    """Create a real Request object for testing"""
    request = Request({"type": "http", "method": "GET", "url": "http://test"})
    request._headers = {"X-Request-ID": "test-request-id"}
    return request


TEST_ASSET_ID_BTC = "BTC"
TEST_ASSET_ID_ETH = "ETH"
TEST_ACTIVE_ONLY = True
TEST_LIMIT_1 = 1
TEST_LIMIT_10 = 10
TEST_TOTAL_COUNT_2 = 2
TEST_ACTIVE_COUNT_1 = 1


class TestListAssets:
    """Test list_assets controller"""

    def test_list_assets_success_with_limit(self):
        """Test list_assets with limit parameter"""
        request = create_test_request()
        test_assets = [create_test_asset_btc(), create_test_asset_eth()]

        with patch(PATCH_GET_REQUEST_ID, return_value="test-request-id") as mock_get_request_id:
            mock_dao = MagicMock()
            mock_dao.get_all_assets.return_value = test_assets

            filter_params = ListAssetsRequest(active_only=True, limit=TEST_LIMIT_1)
            result = list_assets(request, filter_params=filter_params, asset_dao=mock_dao)

            assert isinstance(result, ListAssetsResponse)
            assert len(result.data) == TEST_LIMIT_1
            assert result.total_count == TEST_TOTAL_COUNT_2
            assert result.active_count == TEST_ACTIVE_COUNT_1

    def test_list_assets_without_limit(self):
        """Test list_assets without limit parameter"""
        request = create_test_request()
        test_assets = [create_test_asset_btc(), create_test_asset_eth()]

        with patch(PATCH_GET_REQUEST_ID, return_value="test-request-id"):
            mock_dao = MagicMock()
            mock_dao.get_all_assets.return_value = test_assets

            filter_params = ListAssetsRequest(active_only=True, limit=None)
            result = list_assets(request, filter_params=filter_params, asset_dao=mock_dao)

            assert isinstance(result, ListAssetsResponse)
            assert len(result.data) == TEST_TOTAL_COUNT_2
            assert result.total_count == TEST_TOTAL_COUNT_2

    def test_list_assets_database_error(self):
        """Test that database errors are properly converted to internal exceptions"""
        request = create_test_request()

        with patch(PATCH_GET_REQUEST_ID, return_value="test-request-id"):
            mock_dao = MagicMock()
            mock_dao.get_all_assets.side_effect = Exception("Database connection failed")

            filter_params = ListAssetsRequest(active_only=True, limit=10)

            with pytest.raises(CNOPInventoryServerException) as exc_info:
                list_assets(request, filter_params=filter_params, asset_dao=mock_dao)

            assert "Failed to list assets" in str(exc_info.value)


class TestGetAsset:
    """Test get_asset controller"""

    def test_get_asset_success(self):
        """Test get_asset with valid asset ID"""
        request = create_test_request()
        test_asset = create_test_asset_btc()

        with patch(PATCH_GET_REQUEST_ID, return_value="test-request-id"):

            mock_dao = MagicMock()
            mock_dao.get_asset_by_id.return_value = test_asset

            asset_request = GetAssetRequest(asset_id=TEST_ASSET_ID_BTC)
            result = get_asset(request, asset_request=asset_request, asset_dao=mock_dao)

            assert isinstance(result, GetAssetResponse)
            assert result.data.asset_id == TEST_ASSET_ID_BTC
            assert result.data.name == "Bitcoin"
            assert result.data.availability_status == "available"

    def test_get_asset_not_found(self):
        """Test get_asset with non-existent asset ID"""
        request = create_test_request()

        with patch(PATCH_GET_REQUEST_ID, return_value="test-request-id"):

            mock_dao = MagicMock()
            # DAO raises CNOPAssetNotFoundException when asset not found
            mock_dao.get_asset_by_id.side_effect = CNOPAssetNotFoundException("Asset 'XYZ' not found")

            asset_request = GetAssetRequest(asset_id="XYZ")

            # Should raise CNOPAssetNotFoundException from DAO
            with pytest.raises(CNOPAssetNotFoundException):
                get_asset(request, asset_request=asset_request, asset_dao=mock_dao)

    def test_get_asset_inactive(self):
        """Test get_asset with inactive asset"""
        request = create_test_request()
        test_asset = create_test_asset_inactive()

        with patch(PATCH_GET_REQUEST_ID, return_value="test-request-id"):

            mock_dao = MagicMock()
            mock_dao.get_asset_by_id.return_value = test_asset

            asset_request = GetAssetRequest(asset_id=TEST_ASSET_ID_BTC)
            result = get_asset(request, asset_request=asset_request, asset_dao=mock_dao)

            assert result.data.availability_status == "unavailable"
            assert result.data.is_active is False


class TestGetAssetRequest:
    """Test get_asset_request dependency"""

    def test_get_asset_request_creates_model(self):
        """Test that get_asset_request creates GetAssetRequest model"""
        result = get_asset_request(TEST_ASSET_ID_BTC)

        assert isinstance(result, GetAssetRequest)
        assert result.asset_id == TEST_ASSET_ID_BTC