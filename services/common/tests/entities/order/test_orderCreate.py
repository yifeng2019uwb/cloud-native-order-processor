"""
Tests for OrderCreate model.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from src.entities.order.order import OrderCreate
from src.entities.order.enums import OrderType
from pydantic import ValidationError


class TestOrderCreate:
    """Test cases for OrderCreate model."""

    def test_valid_order_create(self):
        """Test valid order creation."""
        order = OrderCreate(
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.5"),
            price=Decimal("50000.00")
        )

        assert order.order_type == OrderType.MARKET_BUY
        assert order.asset_id == "BTC"
        assert order.quantity == Decimal("1.5")
        assert order.price == Decimal("50000.00")

    def test_order_create_with_limit_price(self):
        """Test order creation with limit price."""
        order = OrderCreate(
            order_type=OrderType.LIMIT_BUY,
            asset_id="BTC",
            quantity=Decimal("1.0"),
            price=Decimal("44000.00")
        )

        assert order.order_type == OrderType.LIMIT_BUY
        assert order.asset_id == "BTC"
        assert order.quantity == Decimal("1.0")
        assert order.price == Decimal("44000.00")

    def test_order_create_missing_quantity(self):
        """Test order creation with missing quantity."""
        with pytest.raises(ValidationError):
            OrderCreate(
                order_type=OrderType.MARKET_BUY,
                asset_id="BTC",
                price=Decimal("50000.00")
                # Missing quantity
            )

    def test_order_create_missing_price(self):
        """Test order creation with missing price."""
        with pytest.raises(ValidationError):
            OrderCreate(
                order_type=OrderType.MARKET_BUY,
                asset_id="BTC",
                quantity=Decimal("1.0")
                # Missing price
            )

    def test_order_create_invalid_price(self):
        """Test order creation with invalid price."""
        with pytest.raises(ValidationError):
            OrderCreate(
                order_type=OrderType.LIMIT_BUY,
                asset_id="BTC",
                quantity=Decimal("1.0"),
                price=Decimal("-100.00")  # Negative price
            )

    def test_order_create_invalid_quantity(self):
        """Test order creation with invalid quantity"""
        with pytest.raises(ValidationError):
            OrderCreate(
                order_type=OrderType.MARKET_BUY,
                asset_id="BTC",
                quantity=Decimal("-1.0"),  # Negative quantity
                price=Decimal("50000.00")
            )

    def test_order_create_zero_quantity(self):
        """Test order creation with zero quantity"""
        with pytest.raises(ValidationError):
            OrderCreate(
                order_type=OrderType.MARKET_BUY,
                asset_id="BTC",
                quantity=Decimal("0.0"),  # Zero quantity
                price=Decimal("50000.00")
            )

    def test_order_create_zero_price(self):
        """Test order creation with zero price"""
        with pytest.raises(ValidationError):
            OrderCreate(
                order_type=OrderType.LIMIT_BUY,
                asset_id="BTC",
                quantity=Decimal("1.0"),
                price=Decimal("0.0")  # Zero price
            )

    def test_order_create_different_asset(self):
        """Test order creation with different asset."""
        order = OrderCreate(
            order_type=OrderType.MARKET_SELL,
            asset_id="ETH",
            quantity=Decimal("10.0"),
            price=Decimal("3000.00")
        )

        assert order.order_type == OrderType.MARKET_SELL
        assert order.asset_id == "ETH"
        assert order.quantity == Decimal("10.0")
        assert order.price == Decimal("3000.00")

    def test_order_create_limit_sell(self):
        """Test limit sell order creation."""
        order = OrderCreate(
            order_type=OrderType.LIMIT_SELL,
            asset_id="BTC",
            quantity=Decimal("0.5"),
            price=Decimal("55000.00")
        )

        assert order.order_type == OrderType.LIMIT_SELL
        assert order.asset_id == "BTC"
        assert order.quantity == Decimal("0.5")
        assert order.price == Decimal("55000.00")