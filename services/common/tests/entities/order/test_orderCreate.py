"""
Unit tests for OrderCreate model.
Tests cover the OrderCreate entity class.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError

from src.entities.order.orderCreate import OrderCreate
from src.entities.order.enums import OrderType


class TestOrderCreate:
    """Test OrderCreate model."""

    def test_valid_order_create(self):
        """Test valid order creation."""
        order = OrderCreate(
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.5"),
            currency="USD"
        )

        assert order.order_type == OrderType.MARKET_BUY
        assert order.asset_id == "BTC"
        assert order.quantity == Decimal("1.5")
        assert order.price_per_unit is None
        assert order.currency == "USD"

    def test_order_create_with_limit_price(self):
        """Test order creation with limit price."""
        order = OrderCreate(
            order_type=OrderType.LIMIT_BUY,
            asset_id="BTC",
            quantity=Decimal("1.0"),
            limit_price=Decimal("44000.00"),
            price_per_unit=Decimal("44000.00"),  # Required for limit orders
            currency="USD"
        )

        assert order.limit_price == Decimal("44000.00")

    def test_order_create_with_expiration(self):
        """Test order creation with expiration."""
        expires_at = datetime.now(timezone.utc) + timedelta(days=1)
        order = OrderCreate(
            order_type=OrderType.LIMIT_BUY,
            asset_id="BTC",
            quantity=Decimal("1.0"),
            limit_price=Decimal("45000.00"),
            price_per_unit=Decimal("45000.00"),  # Required for limit orders
            expires_at=expires_at,
            currency="USD"
        )

        assert order.expires_at == expires_at

    def test_order_create_with_stop_price(self):
        """Test order creation with stop price."""
        order = OrderCreate(
            order_type=OrderType.STOP_LOSS,
            asset_id="BTC",
            quantity=Decimal("1.0"),
            stop_price=Decimal("44000.00"),
            currency="USD"
        )

        assert order.stop_price == Decimal("44000.00")

    def test_order_create_missing_required_fields(self):
        """Test order creation with missing required fields."""
        # Missing order_type
        with pytest.raises(ValidationError):
            OrderCreate(
                asset_id="BTC",
                quantity=Decimal("1.5"),
                currency="USD"
            )

        # Missing asset_id
        with pytest.raises(ValidationError):
            OrderCreate(
                order_type=OrderType.MARKET_BUY,
                quantity=Decimal("1.5"),
                currency="USD"
            )

        # Missing quantity
        with pytest.raises(ValidationError):
            OrderCreate(
                order_type=OrderType.MARKET_BUY,
                asset_id="BTC",
                currency="USD"
            )

    def test_order_create_invalid_quantity(self):
        """Test order creation with invalid quantity."""
        with pytest.raises(ValidationError):
            OrderCreate(
                order_type=OrderType.MARKET_BUY,
                asset_id="BTC",
                quantity=Decimal("-1.5"),  # Negative quantity
                currency="USD"
            )

    def test_order_create_invalid_price(self):
        """Test order creation with invalid price."""
        with pytest.raises(ValidationError):
            OrderCreate(
                order_type=OrderType.LIMIT_BUY,
                asset_id="BTC",
                quantity=Decimal("1.5"),
                limit_price=Decimal("-45000.00"),  # Negative price
                price_per_unit=Decimal("45000.00"),
                currency="USD"
            )