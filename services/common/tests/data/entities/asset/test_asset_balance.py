"""
Tests for Asset Balance Entity Models
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.data.entities.asset import AssetBalance, AssetBalanceItem

# =============================================================================
# LOCAL TEST VARIABLES - Avoid hardcoded values in tests
# =============================================================================

# Test user and asset data
TEST_USERNAME = "testuser123"
TEST_ASSET_ID_BTC = "BTC"
TEST_ASSET_ID_ETH = "ETH"

# Test quantities
TEST_QUANTITY_10_5 = Decimal("10.5")
TEST_QUANTITY_5_0 = Decimal("5.0")
TEST_QUANTITY_0_0 = Decimal("0.0")
TEST_QUANTITY_NEGATIVE_1_0 = Decimal("-1.0")

# Test timestamps
TEST_CURRENT_TIMESTAMP = datetime.now(timezone.utc)


class TestAssetBalance:
    """Test AssetBalance business logic and validation"""

    def test_asset_balance_zero_quantity(self):
        """Test asset balance with zero quantity - should be allowed"""
        balance = AssetBalance(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_QUANTITY_0_0
        )
        assert balance.quantity == TEST_QUANTITY_0_0

    def test_asset_balance_negative_quantity(self):
        """Test asset balance with negative quantity - should be allowed"""
        balance = AssetBalance(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_QUANTITY_NEGATIVE_1_0
        )
        assert balance.quantity == TEST_QUANTITY_NEGATIVE_1_0

    def test_asset_balance_missing_required_fields(self):
        """Test asset balance with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            AssetBalance(
                asset_id=TEST_ASSET_ID_BTC,
                quantity=TEST_QUANTITY_10_5
            )
        assert "username" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            AssetBalance(
                username=TEST_USERNAME,
                quantity=TEST_QUANTITY_10_5
            )
        assert "asset_id" in str(exc_info.value)


class TestAssetBalanceItem:
    """Test AssetBalanceItem business logic"""

    def test_asset_balance_item_from_entity(self):
        """Test creating AssetBalanceItem from AssetBalance entity"""
        balance = AssetBalance(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_QUANTITY_10_5
        )
        balance_item = AssetBalanceItem.from_asset_balance(balance)

        assert balance_item.Pk == TEST_USERNAME
        assert balance_item.Sk == f"ASSET#{TEST_ASSET_ID_BTC}"
        assert balance_item.username == TEST_USERNAME
        assert balance_item.asset_id == TEST_ASSET_ID_BTC
        assert balance_item.quantity == str(TEST_QUANTITY_10_5)  # String for PynamoDB

    def test_asset_balance_item_to_entity(self):
        """Test converting AssetBalanceItem to AssetBalance entity"""
        now = TEST_CURRENT_TIMESTAMP
        balance_item = AssetBalanceItem(
            Pk=TEST_USERNAME,
            Sk=f"ASSET#{TEST_ASSET_ID_BTC}",
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=str(TEST_QUANTITY_10_5),
            created_at=now.isoformat()
        )
        balance = balance_item.to_asset_balance()

        assert balance.username == TEST_USERNAME
        assert balance.asset_id == TEST_ASSET_ID_BTC
        assert balance.quantity == TEST_QUANTITY_10_5