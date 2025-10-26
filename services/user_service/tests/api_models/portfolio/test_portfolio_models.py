"""
Tests for portfolio API models - Focus on field validation
"""
import pytest
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pydantic import ValidationError

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'common', 'src'))

from api_models.portfolio.portfolio_models import (
    GetPortfolioRequest,
    GetPortfolioResponse,
    GetAssetBalanceResponse,
    PortfolioAssetData
)

# Test constants
TEST_ASSET_ID = "BTC"
TEST_ASSET_NAME = "Bitcoin"
TEST_QUANTITY = Decimal("1.5")
TEST_CURRENT_PRICE = Decimal("45000.50")
TEST_MARKET_VALUE = Decimal("67507.50")
TEST_PERCENTAGE = Decimal("87.1")
TEST_TOTAL_VALUE = 67507.50
TEST_CURRENT_PRICE_FLOAT = 45000.50
TEST_TIMESTAMP = datetime.now(timezone.utc)


def test_get_portfolio_request_valid():
    """Test valid GetPortfolioRequest creation"""
    request = GetPortfolioRequest()
    assert request is not None


def test_portfolio_asset_data_validation():
    """Test PortfolioAssetData field validation"""
    # Valid data
    asset_data = PortfolioAssetData(
        asset_id=TEST_ASSET_ID,
        quantity=TEST_QUANTITY,
        current_price=TEST_CURRENT_PRICE,
        market_value=TEST_MARKET_VALUE,
        percentage=TEST_PERCENTAGE
    )
    assert asset_data.asset_id == TEST_ASSET_ID
    assert asset_data.quantity == TEST_QUANTITY

    # Missing required fields
    with pytest.raises(ValidationError):
        PortfolioAssetData()

    # Invalid asset_id (too short)
    with pytest.raises(ValidationError):
        PortfolioAssetData(
            asset_id="",  # Empty asset_id should fail validation
            quantity=TEST_QUANTITY,
            current_price=TEST_CURRENT_PRICE,
            market_value=TEST_MARKET_VALUE,
            percentage=TEST_PERCENTAGE
        )

    # Negative quantity
    with pytest.raises(ValidationError):
        PortfolioAssetData(
            asset_id=TEST_ASSET_ID,
            quantity=Decimal("-1.5"),  # Negative quantity should fail
            current_price=TEST_CURRENT_PRICE,
            market_value=TEST_MARKET_VALUE,
            percentage=TEST_PERCENTAGE
        )

    # Negative price
    with pytest.raises(ValidationError):
        PortfolioAssetData(
            asset_id=TEST_ASSET_ID,
            quantity=TEST_QUANTITY,
            current_price=Decimal("-45000.50"),  # Negative price should fail
            market_value=TEST_MARKET_VALUE,
            percentage=TEST_PERCENTAGE
        )

    # Percentage > 100
    with pytest.raises(ValidationError):
        PortfolioAssetData(
            asset_id=TEST_ASSET_ID,
            quantity=TEST_QUANTITY,
            current_price=TEST_CURRENT_PRICE,
            market_value=TEST_MARKET_VALUE,
            percentage=Decimal("150")  # Percentage > 100 should fail
        )


def test_get_portfolio_response_validation():
    """Test GetPortfolioResponse field validation"""
    # Valid response
    assets = [
        PortfolioAssetData(
            asset_id=TEST_ASSET_ID,
            quantity=TEST_QUANTITY,
            current_price=TEST_CURRENT_PRICE,
            market_value=TEST_MARKET_VALUE,
            percentage=TEST_PERCENTAGE
        )
    ]
    response = GetPortfolioResponse(assets=assets)
    assert len(response.assets) == 1

    # Empty assets list (valid)
    response = GetPortfolioResponse(assets=[])
    assert len(response.assets) == 0


def test_get_asset_balance_response_validation():
    """Test GetAssetBalanceResponse field validation"""
    # Valid response
    response = GetAssetBalanceResponse(
        asset_id=TEST_ASSET_ID,
        asset_name=TEST_ASSET_NAME,
        quantity=TEST_QUANTITY,
        current_price=TEST_CURRENT_PRICE_FLOAT,
        total_value=TEST_TOTAL_VALUE,
        created_at=TEST_TIMESTAMP,
        updated_at=TEST_TIMESTAMP
    )
    assert response.asset_id == TEST_ASSET_ID
    assert response.asset_name == TEST_ASSET_NAME

    # Missing required fields
    with pytest.raises(ValidationError):
        GetAssetBalanceResponse()

    # GetAssetBalanceResponse doesn't have field validators, so it accepts any values
    # This test verifies that the model accepts various values without validation
    response = GetAssetBalanceResponse(
        asset_id="",  # Empty asset_id accepted as str
        asset_name=TEST_ASSET_NAME,
        quantity=TEST_QUANTITY,
        current_price=-45000.50,  # Negative price accepted as float
        total_value=TEST_TOTAL_VALUE,
        created_at=TEST_TIMESTAMP,
        updated_at=TEST_TIMESTAMP
    )
    assert response.asset_id == ""
    assert response.current_price == -45000.50
