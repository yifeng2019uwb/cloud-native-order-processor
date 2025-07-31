"""
Unit tests for Order model.
Tests cover the Order entity class.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

import pytest
from decimal import Decimal
from datetime import datetime, timezone

from src.entities.order.order import Order
from src.entities.order.enums import OrderType, OrderStatus


class TestOrder:
    """Test Order model."""

    def test_valid_order(self):
        """Test valid order."""
        created_at = datetime.now(timezone.utc)
        order = Order(
            order_id="ord_user123_20231201123456789",
            user_id="user123",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.5"),
            price_per_unit=None,  # Market orders don't specify price_per_unit
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
        assert order.price_per_unit is None
        assert order.currency == "USD"
        assert order.status == OrderStatus.PENDING

    def test_order_gsi2_sort_key(self):
        """Test GSI2 sort key generation."""
        created_at = datetime.now(timezone.utc)
        order = Order(
            order_id="ord_user123_20231201123456789",
            user_id="user123",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.5"),
            price_per_unit=None,
            total_amount=Decimal("67500.00"),
            currency="USD",
            status=OrderStatus.PENDING,
            created_at=created_at,
            updated_at=created_at
        )

        # GSI2 sort key should be asset_id#status#created_at
        expected_key = f"BTC#{OrderStatus.PENDING.value}#{order.created_at.isoformat()}"
        assert order.gsi2_sort_key == expected_key

    def test_order_computed_properties(self):
        """Test order computed properties."""
        created_at = datetime.now(timezone.utc)
        order = Order(
            order_id="ord_user123_20231201123456789",
            user_id="user123",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.5"),
            price_per_unit=None,
            total_amount=Decimal("67500.00"),
            currency="USD",
            status=OrderStatus.PENDING,
            created_at=created_at,
            updated_at=created_at
        )

        # Test total amount is set correctly
        assert order.total_amount == Decimal("67500.00")

        # Test is_fully_executed
        assert order.is_fully_executed is False

        # Test remaining quantity
        assert order.remaining_quantity == Decimal("1.5")

    def test_order_with_executed_quantity(self):
        """Test order with executed quantity."""
        created_at = datetime.now(timezone.utc)
        order = Order(
            order_id="ord_user123_20231201123456789",
            user_id="user123",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.5"),
            price_per_unit=None,
            total_amount=Decimal("67500.00"),
            currency="USD",
            status=OrderStatus.PROCESSING,
            executed_quantity=Decimal("0.75"),
            created_at=created_at,
            updated_at=created_at
        )

        # Test remaining quantity with executed quantity
        assert order.remaining_quantity == Decimal("0.75")
        assert order.is_fully_executed is False

    def test_order_fully_executed(self):
        """Test order when fully executed."""
        created_at = datetime.now(timezone.utc)
        order = Order(
            order_id="ord_user123_20231201123456789",
            user_id="user123",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.5"),
            price_per_unit=None,
            total_amount=Decimal("67500.00"),
            currency="USD",
            status=OrderStatus.COMPLETED,
            executed_quantity=Decimal("1.5"),
            created_at=created_at,
            updated_at=created_at
        )

        # Test fully executed order
        assert order.remaining_quantity == Decimal("0")
        assert order.is_fully_executed is True