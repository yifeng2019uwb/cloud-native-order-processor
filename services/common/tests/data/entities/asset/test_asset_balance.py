"""
Tests for Asset Balance Entity Models
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.data.entities.asset import AssetBalance, AssetBalanceItem


class TestAssetBalance:
    """Test AssetBalance model validation"""

    def test_valid_asset_balance(self):
        """Test valid asset balance creation"""
        balance_data = {
            "username": "testuser123",
            "asset_id": "BTC",
            "quantity": Decimal("10.5")
        }
        balance = AssetBalance(**balance_data)
        assert balance.username == "testuser123"
        assert balance.asset_id == "BTC"
        assert balance.quantity == Decimal("10.5")
        """Test asset balance with missing username"""
        with pytest.raises(ValidationError) as exc_info:
            AssetBalance(
                asset_id="BTC",
                quantity=Decimal("10.0")
            )
        assert "username" in str(exc_info.value)

    def test_asset_balance_missing_asset_id(self):
        """Test asset balance with missing asset_id"""
        with pytest.raises(ValidationError) as exc_info:
            AssetBalance(
                username="testuser123",
                quantity=Decimal("10.0")
            )
        assert "asset_id" in str(exc_info.value)

    def test_asset_balance_empty_username(self):
        """Test asset balance with empty username"""
        # Empty strings are allowed by default in Pydantic
        balance = AssetBalance(
            username="",
            asset_id="BTC",
            quantity=Decimal("10.0")
        )
        assert balance.username == ""

    def test_asset_balance_empty_asset_id(self):
        """Test asset balance with empty asset_id"""
        # Empty strings are allowed by default in Pydantic
        balance = AssetBalance(
            username="testuser123",
            asset_id="",
            quantity=Decimal("10.0")
        )
        assert balance.asset_id == ""

    def test_asset_balance_with_timestamps(self):
        """Test asset balance with custom timestamps"""
        now = datetime.now(timezone.utc)
        balance_data = {
            "username": "testuser123",
            "asset_id": "BTC",
            "quantity": Decimal("10.5"),
            "created_at": now,
            "updated_at": now
        }
        balance = AssetBalance(**balance_data)
        assert balance.created_at == now
        assert balance.updated_at == now

    def test_asset_balance_json_serialization(self):
        """Test asset balance JSON serialization"""
        balance_data = {
            "username": "testuser123",
            "asset_id": "BTC",
            "quantity": Decimal("10.5")
        }
        balance = AssetBalance(**balance_data)

        # Test model_dump
        json_data = balance.model_dump()
        assert json_data["username"] == "testuser123"
        assert json_data["asset_id"] == "BTC"
        assert json_data["quantity"] == Decimal("10.5")
        assert "created_at" in json_data
        assert "updated_at" in json_data


class TestAssetBalanceItem:
    """Test AssetBalanceItem model validation"""

    def test_valid_asset_balance_item(self):
        """Test valid asset balance item creation"""
        now = datetime.now(timezone.utc)
        balance_item_data = {
            "Pk": "testuser123",
            "Sk": "ASSET#BTC",
            "username": "testuser123",
            "asset_id": "BTC",
            "quantity": Decimal("10.5"),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        balance_item = AssetBalanceItem(**balance_item_data)
        assert balance_item.Pk == "testuser123"
        assert balance_item.Sk == "ASSET#BTC"
        assert balance_item.username == "testuser123"
        assert balance_item.asset_id == "BTC"
        assert balance_item.quantity == Decimal("10.5")

    def test_asset_balance_item_from_entity(self):
        """Test creating AssetBalanceItem from AssetBalance entity"""
        balance = AssetBalance(
            username="testuser123",
            asset_id="BTC",
            quantity=Decimal("10.5")
        )
        balance_item = AssetBalanceItem.from_asset_balance(balance)
        assert balance_item.Pk == "testuser123"
        assert balance_item.Sk == "ASSET#BTC"
        assert balance_item.username == "testuser123"
        assert balance_item.asset_id == "BTC"
        assert balance_item.quantity == Decimal("10.5")

    def test_asset_balance_item_to_entity(self):
        """Test converting AssetBalanceItem to AssetBalance entity"""
        now = datetime.now(timezone.utc)
        balance_item = AssetBalanceItem(
            Pk="testuser123",
            Sk="ASSET#BTC",
            username="testuser123",
            asset_id="BTC",
            quantity=Decimal("10.5"),
            created_at=now.isoformat(),
            updated_at=now.isoformat()
        )
        balance = balance_item.to_asset_balance()
        assert balance.username == "testuser123"
        assert balance.asset_id == "BTC"
        assert balance.quantity == Decimal("10.5")
    def test_asset_balance_item_json_serialization(self):
        """Test asset balance item JSON serialization"""
        now = datetime.now(timezone.utc)
        balance_item_data = {
            "Pk": "testuser123",
            "Sk": "ASSET#BTC",
            "username": "testuser123",
            "asset_id": "BTC",
            "quantity": Decimal("10.5"),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        balance_item = AssetBalanceItem(**balance_item_data)

        # Test model_dump
        json_data = balance_item.model_dump()
        assert json_data["Pk"] == "testuser123"
        assert json_data["Sk"] == "ASSET#BTC"
        assert json_data["username"] == "testuser123"
        assert json_data["asset_id"] == "BTC"
        assert json_data["quantity"] == Decimal("10.5")
