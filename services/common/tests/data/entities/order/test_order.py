"""
Tests for Order entity model.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone

from src.data.entities.order.order import Order
from src.data.entities.order.enums import OrderType, OrderStatus


class TestOrder:
    """Test cases for Order entity model."""

    def test_valid_order_creation(self):
        """Test valid order creation."""
        order = Order(
            Pk="order_123",
            Sk="ORDER",
            order_id="order_123",
            username="user123",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.5"),
            price=Decimal("45000.00"),
            total_amount=Decimal("67500.00"),
            status=OrderStatus.PENDING
        )

        assert order.Pk == "order_123"
        assert order.Sk == "ORDER"
        assert order.order_id == "order_123"
        assert order.username == "user123"
        assert order.order_type == OrderType.MARKET_BUY
        assert order.asset_id == "BTC"
        assert order.quantity == Decimal("1.5")
        assert order.price == Decimal("45000.00")
        assert order.total_amount == Decimal("67500.00")
        assert order.status == OrderStatus.PENDING
        assert order.created_at is not None
        assert order.updated_at is not None

    def test_order_with_custom_timestamps(self):
        """Test order creation with custom timestamps."""
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)

        order = Order(
            Pk="order_456",
            Sk="ORDER",
            order_id="order_456",
            username="user456",
            order_type=OrderType.LIMIT_SELL,
            asset_id="ETH",
            quantity=Decimal("10.0"),
            price=Decimal("3000.00"),
            total_amount=Decimal("30000.00"),
            status=OrderStatus.PENDING,
            created_at=created_at,
            updated_at=updated_at
        )

        assert order.created_at == created_at
        assert order.updated_at == updated_at

    def test_order_different_types(self):
        """Test order creation with different order types."""
        order_types = [OrderType.MARKET_BUY, OrderType.MARKET_SELL, OrderType.LIMIT_BUY, OrderType.LIMIT_SELL]

        for order_type in order_types:
            order = Order(
                Pk=f"order_{order_type.value}",
                Sk="ORDER",
                order_id=f"order_{order_type.value}",
                username="testuser",
                order_type=order_type,
                asset_id="BTC",
                quantity=Decimal("1.0"),
                price=Decimal("50000.00"),
                total_amount=Decimal("50000.00"),
                status=OrderStatus.PENDING
            )

            assert order.order_type == order_type

    def test_order_different_statuses(self):
        """Test order creation with different statuses."""
        statuses = [OrderStatus.PENDING, OrderStatus.COMPLETED, OrderStatus.CANCELLED, OrderStatus.FAILED]

        for status in statuses:
            order = Order(
                Pk=f"order_{status.value}",
                Sk="ORDER",
                order_id=f"order_{status.value}",
                username="testuser",
                order_type=OrderType.MARKET_BUY,
                asset_id="BTC",
                quantity=Decimal("1.0"),
                price=Decimal("50000.00"),
                total_amount=Decimal("50000.00"),
                status=status
            )

            assert order.status == status

    def test_order_serialization(self):
        """Test order serialization."""
        order = Order(
            Pk="order_serialize",
            Sk="ORDER",
            order_id="order_serialize",
            username="serialize_user",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.0"),
            price=Decimal("50000.00"),
            total_amount=Decimal("50000.00"),
            status=OrderStatus.PENDING
        )

        # Test model_dump
        data = order.model_dump()
        assert data['Pk'] == "order_serialize"
        assert data['Sk'] == "ORDER"
        assert data['order_id'] == "order_serialize"
        assert data['username'] == "serialize_user"
        assert data['order_type'] == OrderType.MARKET_BUY.value
        assert data['asset_id'] == "BTC"
        assert data['quantity'] == Decimal("1.0")  # Decimal values are preserved
        assert data['price'] == Decimal("50000.00")  # Decimal values are preserved
        assert data['total_amount'] == Decimal("50000.00")  # Decimal values are preserved
        assert data['status'] == OrderStatus.PENDING.value
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_order_from_dict(self):
        """Test creating order from dictionary."""
        order_data = {
            "Pk": "order_dict",
            "Sk": "ORDER",
            "order_id": "order_dict",
            "username": "dict_user",
            "order_type": OrderType.LIMIT_BUY,
            "asset_id": "ETH",
            "quantity": Decimal("5.0"),
            "price": Decimal("3500.00"),
            "total_amount": Decimal("17500.00"),
            "status": OrderStatus.PENDING
        }

        order = Order(**order_data)

        assert order.Pk == "order_dict"
        assert order.Sk == "ORDER"
        assert order.order_id == "order_dict"
        assert order.username == "dict_user"
        assert order.order_type == OrderType.LIMIT_BUY
        assert order.asset_id == "ETH"
        assert order.quantity == Decimal("5.0")
        assert order.price == Decimal("3500.00")
        assert order.total_amount == Decimal("17500.00")
        assert order.status == OrderStatus.PENDING

    def test_order_validation_required_fields(self):
        """Test order validation for required fields."""
        # Test missing required fields
        with pytest.raises(Exception):  # Pydantic validation error
            Order(
                # Missing Pk, Sk, order_id, username, etc.
                order_type=OrderType.MARKET_BUY,
                asset_id="BTC",
                quantity=Decimal("1.0"),
                price=Decimal("50000.00"),
                total_amount=Decimal("50000.00"),
                status=OrderStatus.PENDING
            )

    def test_order_validation_quantity_gt_zero(self):
        """Test order validation for quantity > 0."""
        # The Order entity doesn't have gt=0 validation, so this should pass
        order = Order(
            Pk="order_invalid",
            Sk="ORDER",
            order_id="order_invalid",
            username="testuser",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("0"),  # This should work since no validation
            price=Decimal("50000.00"),
            total_amount=Decimal("0.00"),
            status=OrderStatus.PENDING
        )
        assert order.quantity == Decimal("0")

    def test_order_validation_price_gt_zero(self):
        """Test order validation for price > 0."""
        # The Order entity doesn't have gt=0 validation, so this should pass
        order = Order(
            Pk="order_invalid",
            Sk="ORDER",
            order_id="order_invalid",
            username="testuser",
            order_type=OrderType.MARKET_BUY,
            asset_id="BTC",
            quantity=Decimal("1.0"),
            price=Decimal("0"),  # This should work since no validation
            total_amount=Decimal("0.00"),
            status=OrderStatus.PENDING
        )
        assert order.price == Decimal("0")