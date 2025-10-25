"""
Tests for Order entity model - Simplified
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.data.entities.order.enums import OrderStatus, OrderType
from src.data.entities.order.order import Order

# Test constants
TEST_ORDER_ID_123 = "order_123"
TEST_USERNAME_123 = "user123"
TEST_ASSET_ID_BTC = "BTC"
TEST_QUANTITY_1_5 = Decimal("1.5")
TEST_PRICE_45000 = Decimal("45000.00")
TEST_TOTAL_AMOUNT_67500 = Decimal("67500.00")


class TestOrder:
    """Test cases for Order entity model - Simplified"""

    def test_valid_order_creation(self):
        """Test valid order creation"""
        order = Order(
            order_id=TEST_ORDER_ID_123,
            username=TEST_USERNAME_123,
            order_type=OrderType.MARKET_BUY,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_QUANTITY_1_5,
            price=TEST_PRICE_45000,
            total_amount=TEST_TOTAL_AMOUNT_67500,
            status=OrderStatus.PENDING
        )

        assert order.order_id == TEST_ORDER_ID_123
        assert order.username == TEST_USERNAME_123
        assert order.order_type == OrderType.MARKET_BUY
        assert order.asset_id == TEST_ASSET_ID_BTC
        assert order.quantity == TEST_QUANTITY_1_5
        assert order.price == TEST_PRICE_45000
        assert order.total_amount == TEST_TOTAL_AMOUNT_67500
        assert order.status == OrderStatus.PENDING
        assert order.created_at is not None
        assert order.updated_at is not None

    def test_order_with_custom_timestamps(self):
        """Test order creation with custom timestamps"""
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)

        order = Order(
            order_id=TEST_ORDER_ID_123,
            username=TEST_USERNAME_123,
            order_type=OrderType.LIMIT_SELL,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_QUANTITY_1_5,
            price=TEST_PRICE_45000,
            total_amount=TEST_TOTAL_AMOUNT_67500,
            status=OrderStatus.PENDING,
            created_at=created_at,
            updated_at=updated_at
        )

        assert order.created_at == created_at
        assert order.updated_at == updated_at

    def test_order_serialization(self):
        """Test order serialization"""
        order = Order(
            order_id=TEST_ORDER_ID_123,
            username=TEST_USERNAME_123,
            order_type=OrderType.MARKET_BUY,
            asset_id=TEST_ASSET_ID_BTC,
            quantity=TEST_QUANTITY_1_5,
            price=TEST_PRICE_45000,
            total_amount=TEST_TOTAL_AMOUNT_67500,
            status=OrderStatus.PENDING
        )

        data = order.model_dump()
        assert data['order_id'] == TEST_ORDER_ID_123
        assert data['username'] == TEST_USERNAME_123
        assert data['order_type'] == OrderType.MARKET_BUY.value
        assert data['asset_id'] == TEST_ASSET_ID_BTC
        assert data['quantity'] == TEST_QUANTITY_1_5
        assert data['price'] == TEST_PRICE_45000
        assert data['total_amount'] == TEST_TOTAL_AMOUNT_67500
        assert data['status'] == OrderStatus.PENDING.value
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_required_fields_validation(self):
        """Test order validation for required fields"""
        with pytest.raises(Exception):  # Pydantic validation error
            Order(
                # Missing order_id, username, etc.
                order_type=OrderType.MARKET_BUY,
                asset_id=TEST_ASSET_ID_BTC,
                quantity=TEST_QUANTITY_1_5,
                price=TEST_PRICE_45000,
                total_amount=TEST_TOTAL_AMOUNT_67500,
                status=OrderStatus.PENDING
            )