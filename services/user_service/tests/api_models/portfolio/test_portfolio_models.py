"""
Tests for portfolio API models
"""
import pytest
import os
import sys
from datetime import datetime
from decimal import Decimal
from pydantic import ValidationError

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'common', 'src'))

from api_models.portfolio.portfolio_models import (
    GetPortfolioRequest,
    GetPortfolioResponse,
    PortfolioAssetData
)


class TestGetPortfolioRequest:
    """Test GetPortfolioRequest model"""

    def test_get_portfolio_request_valid(self):
        """Test valid GetPortfolioRequest creation"""
        request = GetPortfolioRequest()
        assert request is not None

    def test_get_portfolio_request_empty(self):
        """Test GetPortfolioRequest with empty data"""
        request = GetPortfolioRequest()
        assert request.model_dump() == {}


class TestPortfolioAssetData:
    """Test PortfolioAssetData model"""

    def test_portfolio_asset_data_valid(self):
        """Test valid PortfolioAssetData creation"""
        asset_data = PortfolioAssetData(
            asset_id="BTC",
            quantity=Decimal("1.5"),
            current_price=Decimal("45000.50"),
            market_value=Decimal("67507.50"),
            percentage=Decimal("25.5")
        )

        assert asset_data.asset_id == "BTC"
        assert asset_data.quantity == Decimal("1.5")
        assert asset_data.current_price == Decimal("45000.50")
        assert asset_data.market_value == Decimal("67507.50")
        assert asset_data.percentage == Decimal("25.5")

    def test_portfolio_asset_data_missing_required_fields(self):
        """Test PortfolioAssetData with missing required fields"""
        with pytest.raises(ValidationError):
            PortfolioAssetData()

    def test_portfolio_asset_data_invalid_asset_id(self):
        """Test PortfolioAssetData with invalid asset_id"""
        with pytest.raises(ValidationError):
            PortfolioAssetData(
                asset_id="",  # Empty asset_id should fail validation
                quantity=Decimal("1.5"),
                current_price=Decimal("45000.50"),
                market_value=Decimal("67507.50"),
                percentage=Decimal("25.5")
            )

    def test_portfolio_asset_data_negative_quantity(self):
        """Test PortfolioAssetData with negative quantity"""
        with pytest.raises(ValidationError):
            PortfolioAssetData(
                asset_id="BTC",
                quantity=Decimal("-1.5"),  # Negative quantity should fail
                current_price=Decimal("45000.50"),
                market_value=Decimal("67507.50"),
                percentage=Decimal("25.5")
            )

    def test_portfolio_asset_data_negative_price(self):
        """Test PortfolioAssetData with negative price"""
        with pytest.raises(ValidationError):
            PortfolioAssetData(
                asset_id="BTC",
                quantity=Decimal("1.5"),
                current_price=Decimal("-45000.50"),  # Negative price should fail
                market_value=Decimal("67507.50"),
                percentage=Decimal("25.5")
            )

    def test_portfolio_asset_data_zero_values(self):
        """Test PortfolioAssetData with zero values"""
        asset_data = PortfolioAssetData(
            asset_id="BTC",
            quantity=Decimal("0"),
            current_price=Decimal("0"),
            market_value=Decimal("0"),
            percentage=Decimal("0")
        )

        assert asset_data.quantity == Decimal("0")
        assert asset_data.current_price == Decimal("0")
        assert asset_data.market_value == Decimal("0")
        assert asset_data.percentage == Decimal("0")

    def test_portfolio_asset_data_high_precision(self):
        """Test PortfolioAssetData with high precision values"""
        asset_data = PortfolioAssetData(
            asset_id="BTC",
            quantity=Decimal("1.123456789"),
            current_price=Decimal("45000.123456789"),
            market_value=Decimal("50550.138888888888888889"),
            percentage=Decimal("25.123456789")
        )

        assert asset_data.quantity == Decimal("1.123456789")
        assert asset_data.current_price == Decimal("45000.123456789")
        assert asset_data.market_value == Decimal("50550.138888888888888889")
        assert asset_data.percentage == Decimal("25.123456789")


class TestGetPortfolioResponse:
    """Test GetPortfolioResponse model"""

    def test_get_portfolio_response_valid(self):
        """Test valid GetPortfolioResponse creation"""
        portfolio_data = {
            "username": "testuser",
            "usd_balance": 10000.00,
            "total_asset_value": 67507.50,
            "total_portfolio_value": 77507.50,
            "asset_count": 2,
            "assets": [
                {
                    "asset_id": "BTC",
                    "quantity": 1.5,
                    "current_price": 45000.50,
                    "market_value": 67507.50,
                    "percentage": 87.1
                }
            ]
        }

        response = GetPortfolioResponse(
            success=True,
            message="Portfolio retrieved successfully",
            data=portfolio_data,
            timestamp=datetime.utcnow()
        )

        assert response.success is True
        assert response.message == "Portfolio retrieved successfully"
        assert response.data == portfolio_data
        assert isinstance(response.timestamp, datetime)

    def test_get_portfolio_response_missing_required_fields(self):
        """Test GetPortfolioResponse with missing required fields"""
        with pytest.raises(ValidationError):
            GetPortfolioResponse()

    def test_get_portfolio_response_success_type_coercion(self):
        """Test GetPortfolioResponse with string success (should be coerced to boolean)"""
        # Pydantic automatically converts string "true" to boolean True
        response = GetPortfolioResponse(
            success="true",  # Will be converted to True
            message="Test message",
            data={},
            timestamp=datetime.utcnow()
        )
        assert response.success is True

    def test_get_portfolio_response_empty_message(self):
        """Test GetPortfolioResponse with empty message"""
        with pytest.raises(ValidationError):
            GetPortfolioResponse(
                success=True,
                message="",  # Empty message should fail
                data={},
                timestamp=datetime.utcnow()
            )

    def test_get_portfolio_response_invalid_timestamp(self):
        """Test GetPortfolioResponse with invalid timestamp"""
        with pytest.raises(ValidationError):
            GetPortfolioResponse(
                success=True,
                message="Test message",
                data={},
                timestamp="invalid_timestamp"  # Should be datetime
            )

    def test_get_portfolio_response_complex_data(self):
        """Test GetPortfolioResponse with complex portfolio data"""
        portfolio_data = {
            "username": "testuser",
            "usd_balance": 10000.00,
            "total_asset_value": 67507.50,
            "total_portfolio_value": 77507.50,
            "asset_count": 2,
            "assets": [
                {
                    "asset_id": "BTC",
                    "quantity": 1.5,
                    "current_price": 45000.50,
                    "market_value": 67507.50,
                    "percentage": 87.1
                },
                {
                    "asset_id": "ETH",
                    "quantity": 10.0,
                    "current_price": 3000.00,
                    "market_value": 30000.00,
                    "percentage": 38.7
                }
            ]
        }

        response = GetPortfolioResponse(
            success=True,
            message="Portfolio retrieved successfully",
            data=portfolio_data,
            timestamp=datetime.utcnow()
        )

        assert response.success is True
        assert response.data["asset_count"] == 2
        assert len(response.data["assets"]) == 2
        assert response.data["assets"][0]["asset_id"] == "BTC"
        assert response.data["assets"][1]["asset_id"] == "ETH"

    def test_get_portfolio_response_json_serialization(self):
        """Test GetPortfolioResponse JSON serialization"""
        portfolio_data = {
            "username": "testuser",
            "usd_balance": 10000.00,
            "total_asset_value": 67507.50,
            "total_portfolio_value": 77507.50,
            "asset_count": 1,
            "assets": []
        }

        response = GetPortfolioResponse(
            success=True,
            message="Portfolio retrieved successfully",
            data=portfolio_data,
            timestamp=datetime.utcnow()
        )

        # Test that the response can be serialized to JSON
        json_data = response.model_dump()
        assert "success" in json_data
        assert "message" in json_data
        assert "data" in json_data
        assert "timestamp" in json_data
        assert json_data["success"] is True
