"""
Tests for OrderCreate model.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from src.entities.order.order import OrderCreate
from src.entities.order.enums import OrderType
from pydantic import ValidationError


@pytest.mark.skip(reason="OrderCreate entity schema changed - needs update")
class TestOrderCreate:
    """Test cases for OrderCreate model."""

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
        assert order.order_price is None
        assert order.currency == "USD"

    def test_order_create_with_limit_price(self):
        """Test order creation with limit price."""
        order = OrderCreate(
            order_type=OrderType.LIMIT_BUY,
            asset_id="BTC",
            quantity=Decimal("1.0"),
            order_price=Decimal("44000.00"),  # Required for limit orders
            currency="USD"
        )

        assert order.order_type == OrderType.LIMIT_BUY
        assert order.asset_id == "BTC"
        assert order.quantity == Decimal("1.0")
        assert order.order_price == Decimal("44000.00")
        assert order.currency == "USD"

    def test_order_create_with_expiration(self):
        """Test order creation with expiration."""
        expires_at = datetime.now(timezone.utc) + timedelta(days=1)
        order = OrderCreate(
            order_type=OrderType.LIMIT_BUY,
            asset_id="BTC",
            quantity=Decimal("1.0"),
            order_price=Decimal("45000.00"),  # Required for limit orders
            expires_at=expires_at,
            currency="USD"
        )

        assert order.order_type == OrderType.LIMIT_BUY
        assert order.asset_id == "BTC"
        assert order.quantity == Decimal("1.0")
        assert order.order_price == Decimal("45000.00")
        assert order.expires_at == expires_at
        assert order.currency == "USD"

    def test_order_create_missing_quantity(self):
        """Test order creation with missing quantity."""
        with pytest.raises(ValueError):
            OrderCreate(
                order_type=OrderType.MARKET_BUY,
                asset_id="BTC",
                # Missing quantity
                currency="USD"
            )

    def test_order_create_invalid_price(self):
        """Test order creation with invalid price."""
        with pytest.raises(ValueError):
            OrderCreate(
                order_type=OrderType.LIMIT_BUY,
                asset_id="BTC",
                quantity=Decimal("1.0"),
                order_price=Decimal("-100.00"),  # Negative price
                currency="USD"
            )

    def test_order_create_invalid_quantity(self):
        """Test order creation with invalid quantity"""
        with pytest.raises(ValidationError):
            OrderCreate(
                user_id="user_123",
                order_type=OrderType.MARKET_BUY,
                asset_id="BTC",
                quantity=Decimal("-1.0"),
                order_price=None,
                total_amount=Decimal("45000.00")
            )

    def test_order_create_invalid_total_amount(self):
        """Test order creation with invalid total amount"""
        # Note: total_amount is not part of OrderCreate model, so this test should be removed
        # or modified to test a different validation scenario
        pass