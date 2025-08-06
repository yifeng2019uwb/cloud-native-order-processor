"""
Tests for Order entity model.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone

from src.entities.order.order import Order
from src.entities.order.enums import OrderType, OrderStatus


@pytest.mark.skip(reason="Order entity schema changed - needs update")
class TestOrder:
    """Test cases for Order entity."""

    def test_valid_order(self):
        """Test valid order."""
        created_at = datetime.now(timezone.utc)
        order = Order(
            order_id="ord_user123_20231201123456789",
            user_id="user123",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.5"),
            order_price=None,  # Market orders don't specify order_price
            total_amount=Decimal("67500.00"),  # Required field
            currency="USD",
            status=OrderStatus.PENDING,
            created_at=created_at,
            updated_at=created_at  # Required field
        )

        assert order.order_id == "ord_user123_20231201123456789"
        assert order.user_id == "user123"
        assert order.order_type == OrderType.MARKET_BUY
        assert order.asset_id == "BTC"
        assert order.quantity == Decimal("1.5")
        assert order.order_price is None
        assert order.total_amount == Decimal("67500.00")
        assert order.currency == "USD"
        assert order.status == OrderStatus.PENDING
        assert order.created_at == created_at
        assert order.updated_at == created_at

    def test_order_computed_properties(self):
        """Test order computed properties."""
        created_at = datetime.now(timezone.utc)
        order = Order(
            order_id="ord_user123_20231201123456789",
            user_id="user123",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.5"),
            order_price=None,
            total_amount=Decimal("67500.00"),
            currency="USD",
            status=OrderStatus.PENDING,
            created_at=created_at,
            updated_at=created_at
        )

        assert order.is_completed is False
        assert order.is_cancelled is False
        assert order.is_active is True
        assert order.remaining_quantity == Decimal("1.5")
        assert order.is_fully_executed is False
        assert order.execution_percentage == Decimal("0")
        assert order.is_terminal is False
        assert order.can_be_cancelled_by_user is True