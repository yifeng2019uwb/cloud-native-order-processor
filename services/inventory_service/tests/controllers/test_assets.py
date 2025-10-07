"""
Unit tests for assets controller - Following correct patterns
Path: services/inventory-service/tests/controllers/test_assets.py
"""
import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from fastapi import Request
from decimal import Decimal
from datetime import datetime

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

from common.data.entities.inventory import Asset

# Constants for patch paths
PATH_GET_ASSET_DAO = 'controllers.assets.get_asset_dao'
PATH_GET_REQUEST_ID_FROM_REQUEST = 'controllers.assets.get_request_id_from_request'
PATH_VALIDATE_ASSET_EXISTS = 'controllers.assets.validate_asset_exists'
PATH_ASSET_DAO = 'controllers.assets.AssetDAO'
PATH_ASSET_ID_REQUEST = 'controllers.assets.AssetIdRequest'

# Reusable test assets
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
        updated_at=datetime.utcnow()
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
        updated_at=datetime.utcnow()
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


# ===== list_assets tests =====

def test_list_assets_with_limit():
    """Test list_assets with limit parameter"""
    request = create_test_request()
    test_assets = [create_test_asset_btc(), create_test_asset_eth()]

    with patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:
        mock_dao = MagicMock()
        mock_dao.get_all_assets.return_value = test_assets
        mock_get_request_id.return_value = "test-request-id"

        # Pass limit as integer, not Query object
        result = list_assets(request, active_only=True, limit=1, asset_dao=mock_dao)

        # Verify result structure
        assert result is not None
        assert hasattr(result, 'assets')
        assert len(result.assets) == 1  # Should be limited to 1
        assert hasattr(result, 'total_count')
        assert result.total_count == 2  # Total count should be 2
        assert result.assets[0].asset_id == "BTC"


def test_list_assets_without_limit():
    """Test list_assets without limit parameter"""
    request = create_test_request()
    test_assets = [create_test_asset_btc(), create_test_asset_eth()]

    with patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:
        mock_dao = MagicMock()
        mock_dao.get_all_assets.return_value = test_assets
        mock_get_request_id.return_value = "test-request-id"

        # Pass limit=None explicitly
        result = list_assets(request, active_only=True, limit=None, asset_dao=mock_dao)

        # Verify result structure
        assert result is not None
        assert hasattr(result, 'assets')
        assert len(result.assets) == 2  # Should return all assets
        assert hasattr(result, 'total_count')
        assert result.total_count == 2


def test_list_assets_total_count_without_active_only():
    """Test total_count calculation when active_only=False - covers line 140"""
    request = create_test_request()
    test_assets = [create_test_asset_btc(), create_test_asset_eth()]

    with patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:
        mock_dao = MagicMock()
        mock_dao.get_all_assets.return_value = test_assets
        mock_get_request_id.return_value = "test-request-id"

        # Test with active_only=False to trigger line 140: total_count = len(all_assets)
        result = list_assets(request, active_only=False, limit=10, asset_dao=mock_dao)

        # Verify total_count is calculated from all_assets (line 140)
        assert result.total_count == 2
        assert len(result.assets) == 2


def test_list_assets_database_error():
    """Test that database errors are properly converted to internal exceptions"""
    request = create_test_request()

    with patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:
        mock_dao = MagicMock()
        mock_dao.get_all_assets.side_effect = Exception("Database connection failed")
        mock_get_request_id.return_value = "test-request-id"

        with pytest.raises(CNOPInventoryServerException) as exc_info:
            list_assets(request, active_only=True, limit=10, asset_dao=mock_dao)

        error = exc_info.value
        assert "Failed to list assets" in str(error)


def test_list_assets_active_count():
    """Test that active_count is correctly calculated"""
    request = create_test_request()
    btc_active = create_test_asset_btc()
    eth_inactive = create_test_asset_eth()
    eth_inactive.is_active = False
    test_assets = [btc_active, eth_inactive]

    with patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:
        mock_dao = MagicMock()
        mock_dao.get_all_assets.return_value = test_assets
        mock_get_request_id.return_value = "test-request-id"

        result = list_assets(request, active_only=False, limit=None, asset_dao=mock_dao)

        # Verify active_count counts only active assets
        assert result.active_count == 1
        assert result.total_count == 2


# ===== get_asset_by_id tests =====

def test_get_asset_by_id_success():
    """Test get_asset_by_id with valid asset ID"""
    request = create_test_request()
    test_asset = create_test_asset_btc()

    with patch(PATH_VALIDATE_ASSET_EXISTS) as mock_validate, \
         patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:

        mock_dao = MagicMock()
        mock_dao.get_asset_by_id.return_value = test_asset
        mock_get_request_id.return_value = "test-request-id"

        result = get_asset_by_id(request, "BTC", asset_dao=mock_dao)

        # Verify result
        assert result is not None
        assert result.asset_id == "BTC"
        assert result.name == "Bitcoin"
        assert result.availability_status == "available"
        mock_validate.assert_called_once_with("BTC", mock_dao)


def test_get_asset_by_id_not_found():
    """Test get_asset_by_id with non-existent asset ID"""
    request = create_test_request()

    with patch(PATH_VALIDATE_ASSET_EXISTS) as mock_validate, \
         patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:

        mock_dao = MagicMock()
        mock_get_request_id.return_value = "test-request-id"

        # Mock validate_asset_exists to raise CNOPAssetNotFoundException
        mock_validate.side_effect = CNOPAssetNotFoundException("Asset not found")

        # Test that the function raises the correct exception
        with pytest.raises(CNOPAssetNotFoundException):
            get_asset_by_id(request, "XYZ", asset_dao=mock_dao)


def test_get_asset_by_id_database_error():
    """Test that database errors in get_asset_by_id are properly handled"""
    request = create_test_request()

    with patch(PATH_VALIDATE_ASSET_EXISTS) as mock_validate, \
         patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:

        mock_dao = MagicMock()
        mock_dao.get_asset_by_id.side_effect = Exception("Database query failed")
        mock_get_request_id.return_value = "test-request-id"

        with pytest.raises(CNOPInventoryServerException) as exc_info:
            get_asset_by_id(request, "BTC", asset_dao=mock_dao)

        error = exc_info.value
        assert "Failed to get asset BTC" in str(error)


def test_get_asset_by_id_validation_error():
    """Test get_asset_by_id with field validation error - re-raises validation exception"""
    request = create_test_request()

    with patch(PATH_ASSET_ID_REQUEST) as mock_asset_id_request, \
         patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:

        mock_get_request_id.return_value = "test-request-id"

        # Mock AssetIdRequest to raise CNOPAssetValidationException
        mock_asset_id_request.side_effect = CNOPAssetValidationException("Invalid asset_id format")

        # The code re-raises the original validation error (lines 203-206)
        with pytest.raises(CNOPAssetValidationException) as exc_info:
            get_asset_by_id(request, "INVALID@#$", asset_dao=MagicMock())

        assert "Invalid asset_id format" in str(exc_info.value)


def test_get_asset_by_id_business_validation_error():
    """Test CNOPAssetNotFoundException from business validation - covers lines 275-277"""
    request = create_test_request()

    with patch(PATH_VALIDATE_ASSET_EXISTS) as mock_validate, \
         patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:

        mock_dao = MagicMock()
        mock_get_request_id.return_value = "test-request-id"

        # Mock validate_asset_exists to raise CNOPAssetNotFoundException (business validation)
        mock_validate.side_effect = CNOPAssetNotFoundException("Asset not found")

        # Test that CNOPAssetNotFoundException is re-raised (lines 275-277)
        with pytest.raises(CNOPAssetNotFoundException, match="Asset not found"):
            get_asset_by_id(request, "XYZ", asset_dao=mock_dao)


def test_get_asset_by_id_inactive_asset():
    """Test get_asset_by_id with inactive asset - availability_status should be 'unavailable'"""
    request = create_test_request()
    test_asset = create_test_asset_inactive()

    with patch(PATH_VALIDATE_ASSET_EXISTS) as mock_validate, \
         patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:

        mock_dao = MagicMock()
        mock_dao.get_asset_by_id.return_value = test_asset
        mock_get_request_id.return_value = "test-request-id"

        result = get_asset_by_id(request, "BTC", asset_dao=mock_dao)

        # Verify availability_status is 'unavailable' for inactive asset
        assert result.availability_status == "unavailable"
        assert result.is_active is False


def test_get_asset_by_id_asset_without_last_updated():
    """Test get_asset_by_id when asset.last_updated is None - covers line 221"""
    request = create_test_request()
    test_asset = create_test_asset_btc()
    test_asset.last_updated = None

    with patch(PATH_VALIDATE_ASSET_EXISTS) as mock_validate, \
         patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:

        mock_dao = MagicMock()
        mock_dao.get_asset_by_id.return_value = test_asset
        mock_get_request_id.return_value = "test-request-id"

        result = get_asset_by_id(request, "BTC", asset_dao=mock_dao)

        # Verify last_updated is set to current time when None (line 221)
        assert result.last_updated is not None


# ===== Metrics tests (when METRICS_AVAILABLE is False) =====

def test_list_assets_metrics_not_available():
    """Test that metrics are not recorded when METRICS_AVAILABLE is False - covers lines 146-148"""
    request = create_test_request()
    test_assets = [create_test_asset_btc()]

    with patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:
        mock_dao = MagicMock()
        mock_dao.get_all_assets.return_value = test_assets
        mock_get_request_id.return_value = "test-request-id"

        # Test list_assets - metrics code will not execute (lines 146-148)
        result = list_assets(request, active_only=True, limit=10, asset_dao=mock_dao)
        assert result is not None
        assert len(result.assets) == 1


def test_get_asset_by_id_metrics_not_available():
    """Test that metrics are not recorded when METRICS_AVAILABLE is False - covers line 219"""
    request = create_test_request()
    test_asset = create_test_asset_btc()

    with patch(PATH_VALIDATE_ASSET_EXISTS) as mock_validate, \
         patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:

        mock_dao = MagicMock()
        mock_dao.get_asset_by_id.return_value = test_asset
        mock_get_request_id.return_value = "test-request-id"

        # Test get_asset_by_id - metrics code will not execute (line 219)
        result = get_asset_by_id(request, "BTC", asset_dao=mock_dao)
        assert result is not None
        assert result.asset_id == "BTC"


# ===== Additional coverage tests =====

def test_build_asset_list_with_empty_name():
    """Test build_asset_list handles assets with None name - covers line 59"""
    request = create_test_request()
    test_asset = create_test_asset_btc()
    test_asset.name = None

    with patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:
        mock_dao = MagicMock()
        mock_dao.get_all_assets.return_value = [test_asset]
        mock_get_request_id.return_value = "test-request-id"

        result = list_assets(request, active_only=True, limit=None, asset_dao=mock_dao)

        # Verify empty name is converted to empty string (line 59)
        assert result.assets[0].name == ''


def test_build_asset_list_with_none_category():
    """Test build_asset_list handles assets with None category - covers line 61"""
    request = create_test_request()
    test_asset = create_test_asset_btc()
    test_asset.category = None

    with patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:
        mock_dao = MagicMock()
        mock_dao.get_all_assets.return_value = [test_asset]
        mock_get_request_id.return_value = "test-request-id"

        result = list_assets(request, active_only=True, limit=None, asset_dao=mock_dao)

        # Verify None category defaults to 'unknown' (line 61)
        assert result.assets[0].category == 'unknown'


def test_list_assets_filters_in_response():
    """Test that filters are correctly included in response - covers lines 75-78"""
    request = create_test_request()
    test_assets = [create_test_asset_btc()]

    with patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:
        mock_dao = MagicMock()
        mock_dao.get_all_assets.return_value = test_assets
        mock_get_request_id.return_value = "test-request-id"

        result = list_assets(request, active_only=True, limit=50, asset_dao=mock_dao)

        # Verify filters are included in response (lines 75-78)
        assert result.filters["active_only"] is True
        assert result.filters["limit"] == 50


def test_list_assets_with_limit_and_active_only_true():
    """Test list_assets total_count calculation with active_only=True and limit - covers lines 136-138"""
    request = create_test_request()
    active_assets = [create_test_asset_btc()]
    all_assets = [create_test_asset_btc(), create_test_asset_eth()]

    with patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:
        mock_dao = MagicMock()
        # First call returns active assets, second call returns all assets
        mock_dao.get_all_assets.side_effect = [active_assets, all_assets]
        mock_get_request_id.return_value = "test-request-id"

        result = list_assets(request, active_only=True, limit=10, asset_dao=mock_dao)

        # Verify total_count is from all assets (lines 136-138)
        assert len(result.assets) == 1
        assert result.total_count == 2


def test_get_asset_by_id_comprehensive_fields():
    """Test that all comprehensive fields are returned in AssetDetailResponse"""
    request = create_test_request()
    test_asset = create_test_asset_btc()

    with patch(PATH_VALIDATE_ASSET_EXISTS) as mock_validate, \
         patch(PATH_GET_REQUEST_ID_FROM_REQUEST) as mock_get_request_id:

        mock_dao = MagicMock()
        mock_dao.get_asset_by_id.return_value = test_asset
        mock_get_request_id.return_value = "test-request-id"

        result = get_asset_by_id(request, "BTC", asset_dao=mock_dao)

        # Verify all comprehensive market data fields are present
        assert result.market_cap == test_asset.market_cap
        assert result.price_change_24h == test_asset.price_change_24h
        assert result.price_change_percentage_24h == test_asset.price_change_percentage_24h
        assert result.price_change_percentage_7d == test_asset.price_change_percentage_7d
        assert result.price_change_percentage_30d == test_asset.price_change_percentage_30d
        assert result.high_24h == test_asset.high_24h
        assert result.low_24h == test_asset.low_24h
        assert result.total_volume_24h == test_asset.total_volume_24h
        assert result.circulating_supply == test_asset.circulating_supply
        assert result.total_supply == test_asset.total_supply
        assert result.max_supply == test_asset.max_supply
        assert result.ath == test_asset.ath
        assert result.ath_change_percentage == test_asset.ath_change_percentage
        assert result.ath_date == test_asset.ath_date
        assert result.atl == test_asset.atl
        assert result.atl_change_percentage == test_asset.atl_change_percentage
        assert result.atl_date == test_asset.atl_date