"""
Tests for OrderResponse model.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone

from src.data.entities.order.order import OrderResponse
from src.data.entities.order.order import Order
from src.data.entities.order.enums import OrderType, OrderStatus


class TestOrderResponse:
    """Test cases for OrderResponse model."""

    def test_order_response(self):
        """Test order response."""
        created_at = datetime.now(timezone.utc)
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
            status=OrderStatus.PENDING,
            created_at=created_at,
            updated_at=created_at
        )

        response = OrderResponse(
            order_id=order.order_id,
            username=order.username,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            price=order.price,
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        assert response.order_id == "order_123"
        assert response.username == "user123"
        assert response.order_type == OrderType.MARKET_BUY
        assert response.asset_id == "BTC"
        assert response.quantity == Decimal("1.5")
        assert response.price == Decimal("45000.00")
        assert response.total_amount == Decimal("67500.00")
        assert response.status == OrderStatus.PENDING
        assert response.created_at == created_at
        assert response.updated_at == created_at

    def test_order_response_limit_order(self):
        """Test order response for limit order."""
        created_at = datetime.now(timezone.utc)
        order = Order(
            Pk="order_456",
            Sk="ORDER",
            order_id="order_456",
            username="user456",
            order_type=OrderType.LIMIT_BUY,
            asset_id="ETH",
            quantity=Decimal("10.0"),
            price=Decimal("3000.00"),
            total_amount=Decimal("30000.00"),
            status=OrderStatus.PENDING,
            created_at=created_at,
            updated_at=created_at
        )

        response = OrderResponse(
            order_id=order.order_id,
            username=order.username,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            price=order.price,
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        assert response.order_id == "order_456"
        assert response.username == "user456"
        assert response.order_type == OrderType.LIMIT_BUY
        assert response.asset_id == "ETH"
        assert response.quantity == Decimal("10.0")
        assert response.price == Decimal("3000.00")
        assert response.total_amount == Decimal("30000.00")
        assert response.status == OrderStatus.PENDING

    def test_order_response_serialization(self):
        """Test order response serialization."""
        created_at = datetime.now(timezone.utc)
        response = OrderResponse(
            order_id="order_789",
            username="user789",
            order_type=OrderType.MARKET_SELL,
            asset_id="BTC",
            quantity=Decimal("0.5"),
            price=Decimal("50000.00"),
            total_amount=Decimal("25000.00"),
            status=OrderStatus.COMPLETED,
            created_at=created_at,
            updated_at=created_at
        )

        # Test model_dump
        data = response.model_dump()
        assert data['order_id'] == "order_789"
        assert data['username'] == "user789"
        assert data['order_type'] == OrderType.MARKET_SELL.value
        assert data['asset_id'] == "BTC"
        assert data['quantity'] == Decimal("0.5")  # Decimal values are preserved
        assert data['price'] == Decimal("50000.00")  # Decimal values are preserved
        assert data['total_amount'] == Decimal("25000.00")  # Decimal values are preserved
        assert data['status'] == OrderStatus.COMPLETED.value
        assert data['created_at'] == created_at  # datetime values are preserved
        assert data['updated_at'] == created_at  # datetime values are preserved

    def test_order_response_from_order(self):
        """Test creating OrderResponse from Order entity."""
        created_at = datetime.now(timezone.utc)
        order = Order(
            Pk="order_from_entity",
            Sk="ORDER",
            order_id="order_from_entity",
            username="user_from_entity",
            order_type=OrderType.LIMIT_SELL,
            asset_id="ETH",
            quantity=Decimal("5.0"),
            price=Decimal("3500.00"),
            total_amount=Decimal("17500.00"),
            status=OrderStatus.CANCELLED,
            created_at=created_at,
            updated_at=created_at
        )

        # Create response from order
        response = OrderResponse(
            order_id=order.order_id,
            username=order.username,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            price=order.price,
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        assert response.order_id == order.order_id
        assert response.username == order.username
        assert response.order_type == order.order_type
        assert response.asset_id == order.asset_id
        assert response.quantity == order.quantity
        assert response.price == order.price
        assert response.total_amount == order.total_amount
        assert response.status == order.status
        assert response.created_at == order.created_at
        assert response.updated_at == order.updated_at

    def test_order_response_different_statuses(self):
        """Test order response with different statuses."""
        created_at = datetime.now(timezone.utc)
        statuses = [OrderStatus.PENDING, OrderStatus.COMPLETED, OrderStatus.CANCELLED, OrderStatus.FAILED]

        for status in statuses:
            response = OrderResponse(
                order_id=f"order_{status.value}",
                username="testuser",
                order_type=OrderType.MARKET_BUY,
                asset_id="BTC",
                quantity=Decimal("1.0"),
                price=Decimal("50000.00"),
                total_amount=Decimal("50000.00"),
                status=status,
                created_at=created_at,
                updated_at=created_at
            )

            assert response.status == status
            assert response.order_id == f"order_{status.value}"

    def test_order_response_different_order_types(self):
        """Test order response with different order types."""
        created_at = datetime.now(timezone.utc)
        order_types = [OrderType.MARKET_BUY, OrderType.MARKET_SELL, OrderType.LIMIT_BUY, OrderType.LIMIT_SELL]

        for order_type in order_types:
            response = OrderResponse(
                order_id=f"order_{order_type.value}",
                username="testuser",
                order_type=order_type,
                asset_id="BTC",
                quantity=Decimal("1.0"),
                price=Decimal("50000.00"),
                total_amount=Decimal("50000.00"),
                status=OrderStatus.PENDING,
                created_at=created_at,
                updated_at=created_at
            )

            assert response.order_type == order_type
            assert response.order_id == f"order_{order_type.value}"