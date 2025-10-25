"""
Tests for Asset Transaction Entity Models
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.data.entities.asset import (AssetTransaction, AssetTransactionItem,
                                     AssetTransactionStatus,
                                     AssetTransactionType)

# =============================================================================
# LOCAL TEST VARIABLES - Avoid hardcoded values in tests
# =============================================================================

# Test user and asset data
TEST_USERNAME = "testuser123"
TEST_ASSET_ID_BTC = "BTC"
TEST_ASSET_ID_ETH = "ETH"

# Test transaction data
TEST_ORDER_ID = "order-123"

# Test quantities and prices
TEST_QUANTITY_2_5 = Decimal("2.5")
TEST_QUANTITY_1_0 = Decimal("1.0")
TEST_QUANTITY_10_0 = Decimal("10.0")
TEST_PRICE_50000 = Decimal("50000.00")
TEST_PRICE_3000 = Decimal("3000.00")
TEST_TOTAL_AMOUNT_125000 = Decimal("125000.00")
TEST_TOTAL_AMOUNT_30000 = Decimal("30000.00")

# Test timestamps
TEST_CURRENT_TIMESTAMP = datetime.now(timezone.utc)


class TestAssetTransaction:
    """Test AssetTransaction business logic and validation"""

    def test_asset_transaction_zero_quantity(self):
        """Test asset transaction with zero quantity - should be allowed"""
        transaction = AssetTransaction(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            transaction_type=AssetTransactionType.BUY,
            quantity=Decimal("0.0"),
            price=TEST_PRICE_50000,
            total_amount=Decimal("0.0")
        )
        assert transaction.quantity == Decimal("0.0")

    def test_asset_transaction_negative_quantity(self):
        """Test asset transaction with negative quantity - should be allowed for SELL"""
        transaction = AssetTransaction(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            transaction_type=AssetTransactionType.SELL,
            quantity=Decimal("-1.0"),
            price=TEST_PRICE_50000,
            total_amount=Decimal("-50000.0")
        )
        assert transaction.quantity == Decimal("-1.0")

    def test_asset_transaction_zero_price(self):
        """Test asset transaction with zero price - should be allowed"""
        transaction = AssetTransaction(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            transaction_type=AssetTransactionType.BUY,
            quantity=TEST_QUANTITY_2_5,
            price=Decimal("0.0"),
            total_amount=Decimal("0.0")
        )
        assert transaction.price == Decimal("0.0")

    def test_asset_transaction_missing_required_fields(self):
        """Test asset transaction with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            AssetTransaction(
                username=TEST_USERNAME,
                asset_id=TEST_ASSET_ID_BTC,
                transaction_type=AssetTransactionType.BUY
            )
        assert "quantity" in str(exc_info.value)


class TestAssetTransactionItem:
    """Test AssetTransactionItem business logic"""

    def test_asset_transaction_item_from_entity(self):
        """Test creating AssetTransactionItem from AssetTransaction entity"""
        transaction = AssetTransaction(
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            transaction_type=AssetTransactionType.BUY,
            quantity=TEST_QUANTITY_2_5,
            price=TEST_PRICE_50000,
            total_amount=TEST_TOTAL_AMOUNT_125000,
            order_id=TEST_ORDER_ID
        )
        transaction_item = AssetTransactionItem.from_asset_transaction(transaction)

        assert transaction_item.Pk == f"ASSET_TRANS#{TEST_USERNAME}#{TEST_ASSET_ID_BTC}"
        # Sk is a timestamp, not the same as Pk
        assert transaction_item.Sk is not None
        assert isinstance(transaction_item.Sk, str)
        assert transaction_item.username == TEST_USERNAME
        assert transaction_item.asset_id == TEST_ASSET_ID_BTC
        assert transaction_item.quantity == str(TEST_QUANTITY_2_5)  # String for PynamoDB

    def test_asset_transaction_item_to_entity(self):
        """Test converting AssetTransactionItem to AssetTransaction entity"""
        now = TEST_CURRENT_TIMESTAMP
        transaction_item = AssetTransactionItem(
            Pk=f"ASSET_TRANS#{TEST_USERNAME}#{TEST_ASSET_ID_BTC}",
            Sk=now.isoformat(),
            username=TEST_USERNAME,
            asset_id=TEST_ASSET_ID_BTC,
            transaction_type=AssetTransactionType.BUY,
            quantity=str(TEST_QUANTITY_2_5),
            price=str(TEST_PRICE_50000),
            total_amount=str(TEST_TOTAL_AMOUNT_125000),
            order_id=TEST_ORDER_ID,
            status=AssetTransactionStatus.COMPLETED,
            created_at=now
        )
        transaction = transaction_item.to_asset_transaction()

        assert transaction.username == TEST_USERNAME
        assert transaction.asset_id == TEST_ASSET_ID_BTC
        assert transaction.quantity == TEST_QUANTITY_2_5
        assert transaction.price == TEST_PRICE_50000
        assert transaction.total_amount == TEST_TOTAL_AMOUNT_125000