"""
Tests for Asset Balance Entity Models
"""

import pytest
from pydantic import ValidationError
from decimal import Decimal
from datetime import datetime, timezone

from common.entities.asset import AssetBalance, AssetBalanceCreate, AssetBalanceResponse


class TestAssetBalanceCreate:
    """Test AssetBalanceCreate model validation"""

    def test_valid_asset_balance_create(self):
        """Test valid asset balance creation data"""
        balance_data = {
            "username": "testuser123",
            "asset_id": "BTC",
            "initial_quantity": Decimal("10.5")
        }
        balance = AssetBalanceCreate(**balance_data)
        assert balance.username == "testuser123"
        assert balance.asset_id == "BTC"
        assert balance.initial_quantity == Decimal("10.5")

    def test_asset_balance_create_default_quantity(self):
        """Test asset balance creation with default quantity"""
        balance_data = {
            "username": "testuser123",
            "asset_id": "ETH"
        }
        balance = AssetBalanceCreate(**balance_data)
        assert balance.username == "testuser123"
        assert balance.asset_id == "ETH"
        assert balance.initial_quantity == Decimal("0.00")

    def test_asset_balance_create_zero_quantity(self):
        """Test asset balance creation with zero quantity"""
        balance_data = {
            "username": "testuser123",
            "asset_id": "BTC",
            "initial_quantity": Decimal("0.00")
        }
        balance = AssetBalanceCreate(**balance_data)
        assert balance.initial_quantity == Decimal("0.00")

    def test_asset_balance_create_negative_quantity(self):
        """Test asset balance creation with negative quantity"""
        balance_data = {
            "username": "testuser123",
            "asset_id": "BTC",
            "initial_quantity": Decimal("-5.0")
        }
        balance = AssetBalanceCreate(**balance_data)
        assert balance.initial_quantity == Decimal("-5.0")

    def test_asset_balance_create_missing_username(self):
        """Test asset balance creation with missing username"""
        with pytest.raises(ValidationError) as exc_info:
            AssetBalanceCreate(
                asset_id="BTC",
                initial_quantity=Decimal("10.0")
            )
        assert "username" in str(exc_info.value)

    def test_asset_balance_create_missing_asset_id(self):
        """Test asset balance creation with missing asset_id"""
        with pytest.raises(ValidationError) as exc_info:
            AssetBalanceCreate(
                username="testuser123",
                initial_quantity=Decimal("10.0")
            )
        assert "asset_id" in str(exc_info.value)

    def test_asset_balance_create_empty_username(self):
        """Test asset balance creation with empty username"""
        # Empty strings are allowed by default in Pydantic
        balance = AssetBalanceCreate(
            username="",
            asset_id="BTC",
            initial_quantity=Decimal("10.0")
        )
        assert balance.username == ""

    def test_asset_balance_create_empty_asset_id(self):
        """Test asset balance creation with empty asset_id"""
        # Empty strings are allowed by default in Pydantic
        balance = AssetBalanceCreate(
            username="testuser123",
            asset_id="",
            initial_quantity=Decimal("10.0")
        )
        assert balance.asset_id == ""


class TestAssetBalance:
    """Test AssetBalance model validation"""

    def test_valid_asset_balance(self):
        """Test valid asset balance data"""
        now = datetime.now(timezone.utc)
        balance_data = {
            "Pk": "testuser123",
            "Sk": "ASSET#BTC",
            "username": "testuser123",
            "asset_id": "BTC",
            "quantity": Decimal("10.5"),
            "created_at": now,
            "updated_at": now
        }
        balance = AssetBalance(**balance_data)
        assert balance.Pk == "testuser123"
        assert balance.Sk == "ASSET#BTC"
        assert balance.username == "testuser123"
        assert balance.asset_id == "BTC"
        assert balance.quantity == Decimal("10.5")
        assert balance.created_at == now
        assert balance.updated_at == now

    def test_asset_balance_default_quantity(self):
        """Test asset balance with default quantity"""
        now = datetime.now(timezone.utc)
        balance_data = {
            "Pk": "testuser123",
            "Sk": "ASSET#ETH",
            "username": "testuser123",
            "asset_id": "ETH",
            "created_at": now,
            "updated_at": now
        }
        balance = AssetBalance(**balance_data)
        assert balance.quantity == Decimal("0.00")

    def test_asset_balance_default_timestamps(self):
        """Test asset balance with default timestamps"""
        balance_data = {
            "Pk": "testuser123",
            "Sk": "ASSET#BTC",
            "username": "testuser123",
            "asset_id": "BTC",
            "quantity": Decimal("10.5")
        }
        balance = AssetBalance(**balance_data)
        assert balance.created_at is not None
        assert balance.updated_at is not None
        assert isinstance(balance.created_at, datetime)
        assert isinstance(balance.updated_at, datetime)

    def test_asset_balance_negative_quantity(self):
        """Test asset balance with negative quantity"""
        now = datetime.now(timezone.utc)
        balance_data = {
            "Pk": "testuser123",
            "Sk": "ASSET#BTC",
            "username": "testuser123",
            "asset_id": "BTC",
            "quantity": Decimal("-5.0"),
            "created_at": now,
            "updated_at": now
        }
        balance = AssetBalance(**balance_data)
        assert balance.quantity == Decimal("-5.0")

    def test_asset_balance_missing_required_fields(self):
        """Test asset balance with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            AssetBalance(
                username="testuser123",
                asset_id="BTC",
                quantity=Decimal("10.0")
            )
        assert "Pk" in str(exc_info.value)
        assert "Sk" in str(exc_info.value)

    def test_asset_balance_json_serialization(self):
        """Test asset balance JSON serialization"""
        now = datetime.now(timezone.utc)
        balance_data = {
            "Pk": "testuser123",
            "Sk": "ASSET#BTC",
            "username": "testuser123",
            "asset_id": "BTC",
            "quantity": Decimal("10.5"),
            "created_at": now,
            "updated_at": now
        }
        balance = AssetBalance(**balance_data)

        # Test JSON serialization
        json_data = balance.model_dump()
        assert json_data["Pk"] == "testuser123"
        assert json_data["Sk"] == "ASSET#BTC"
        assert json_data["username"] == "testuser123"
        assert json_data["asset_id"] == "BTC"
        assert json_data["quantity"] == Decimal("10.5")  # Decimal remains as Decimal in model_dump
        assert json_data["created_at"] == now
        assert json_data["updated_at"] == now


class TestAssetBalanceResponse:
    """Test AssetBalanceResponse model validation"""

    def test_valid_asset_balance_response(self):
        """Test valid asset balance response data"""
        now = datetime.now(timezone.utc)
        response_data = {
            "username": "testuser123",
            "asset_id": "BTC",
            "quantity": Decimal("10.5"),
            "updated_at": now
        }
        response = AssetBalanceResponse(**response_data)
        assert response.username == "testuser123"
        assert response.asset_id == "BTC"
        assert response.quantity == Decimal("10.5")
        assert response.updated_at == now

    def test_asset_balance_response_zero_quantity(self):
        """Test asset balance response with zero quantity"""
        now = datetime.now(timezone.utc)
        response_data = {
            "username": "testuser123",
            "asset_id": "ETH",
            "quantity": Decimal("0.00"),
            "updated_at": now
        }
        response = AssetBalanceResponse(**response_data)
        assert response.quantity == Decimal("0.00")

    def test_asset_balance_response_negative_quantity(self):
        """Test asset balance response with negative quantity"""
        now = datetime.now(timezone.utc)
        response_data = {
            "username": "testuser123",
            "asset_id": "BTC",
            "quantity": Decimal("-5.0"),
            "updated_at": now
        }
        response = AssetBalanceResponse(**response_data)
        assert response.quantity == Decimal("-5.0")

    def test_asset_balance_response_missing_fields(self):
        """Test asset balance response with missing fields"""
        with pytest.raises(ValidationError) as exc_info:
            AssetBalanceResponse(
                username="testuser123",
                asset_id="BTC"
            )
        assert "quantity" in str(exc_info.value)
        assert "updated_at" in str(exc_info.value)

    def test_asset_balance_response_json_serialization(self):
        """Test asset balance response JSON serialization"""
        now = datetime.now(timezone.utc)
        response_data = {
            "username": "testuser123",
            "asset_id": "BTC",
            "quantity": Decimal("10.5"),
            "updated_at": now
        }
        response = AssetBalanceResponse(**response_data)

        # Test JSON serialization
        json_data = response.model_dump()
        assert json_data["username"] == "testuser123"
        assert json_data["asset_id"] == "BTC"
        assert json_data["quantity"] == Decimal("10.5")  # Decimal remains as Decimal in model_dump
        assert json_data["updated_at"] == now