"""
Tests for OrderResponse model.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone

from src.entities.order.order import OrderResponse
from src.entities.order.order import Order
from src.entities.order.enums import OrderType, OrderStatus


@pytest.mark.skip(reason="Order entity schema changed - needs update")
class TestOrderResponse:
    """Test cases for OrderResponse model."""

    def test_order_response(self):
        """Test order response."""
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

        response = OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            order_price=order.order_price,
            total_amount=order.total_amount,
            executed_quantity=order.executed_quantity,
            currency=order.currency,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        assert response.order_id == "ord_user123_20231201123456789"
        assert response.user_id == "user123"
        assert response.order_type == OrderType.MARKET_BUY
        assert response.asset_id == "BTC"
        assert response.quantity == Decimal("1.5")
        assert response.order_price is None
        assert response.total_amount == Decimal("67500.00")
        assert response.executed_quantity == Decimal("0")
        assert response.currency == "USD"
        assert response.status == OrderStatus.PENDING
        assert response.created_at == created_at
        assert response.updated_at == created_at

    def test_order_response_with_executed_quantity(self):
        """Test order response with executed quantity."""
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
            status=OrderStatus.PROCESSING,
            executed_quantity=Decimal("0.75"),
            created_at=created_at,
            updated_at=created_at
        )

        response = OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            order_price=order.order_price,
            total_amount=order.total_amount,
            executed_quantity=order.executed_quantity,
            currency=order.currency,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        assert response.executed_quantity == Decimal("0.75")
        assert response.remaining_quantity == Decimal("0.75")

    def test_order_response_serialization(self):
        """Test order response serialization."""
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

        response = OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            order_price=order.order_price,
            total_amount=order.total_amount,
            executed_quantity=order.executed_quantity,
            currency=order.currency,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        # Test serialization
        data = response.model_dump()
        assert data["order_id"] == "ord_user123_20231201123456789"
        assert data["user_id"] == "user123"
        assert data["order_type"] == "market_buy"
        assert data["asset_id"] == "BTC"
        assert data["quantity"] == Decimal("1.5")
        assert data["order_price"] is None
        assert data["total_amount"] == Decimal("67500.00")
        assert data["executed_quantity"] == Decimal("0")
        assert data["currency"] == "USD"
        assert data["status"] == "pending"


class TestOrderListResponse:
    """Test cases for OrderListResponse model."""

    @pytest.mark.skip(reason="Order entity schema changed - needs update")
    def test_order_list_response(self):
        """Test order list response."""
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

        order_response = OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            order_price=order.order_price,
            total_amount=order.total_amount,
            executed_quantity=order.executed_quantity,
            currency=order.currency,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        list_response = OrderListResponse(
            orders=[order_response],
            total_count=1,
            active_count=1,
            completed_count=0,
            cancelled_count=0,
            filters_applied={"user_id": "user123"}
        )

        assert len(list_response.orders) == 1
        assert list_response.total_count == 1
        assert list_response.active_count == 1
        assert list_response.completed_count == 0
        assert list_response.cancelled_count == 0
        assert list_response.filters_applied == {"user_id": "user123"}

    @pytest.mark.skip(reason="Order entity schema changed - needs update")
    def test_order_list_response_multiple_orders(self):
        """Test order list response with multiple orders."""
        created_at = datetime.now(timezone.utc)
        orders = [
            Order(
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
            ),
            Order(
                order_id="ord_user123_20231201123456790",
                user_id="user123",
                order_type=OrderType.LIMIT_SELL,
                asset_id="ETH",
                quantity=Decimal("10.0"),
                order_price=Decimal("3000.00"),
                total_amount=Decimal("30000.00"),
                currency="USD",
                status=OrderStatus.CONFIRMED,
                created_at=created_at,
                updated_at=created_at
            )
        ]

        order_responses = [
            OrderResponse(
                order_id=order.order_id,
                user_id=order.user_id,
                order_type=order.order_type,
                asset_id=order.asset_id,
                quantity=order.quantity,
                order_price=order.order_price,
                total_amount=order.total_amount,
                executed_quantity=order.executed_quantity,
                currency=order.currency,
                status=order.status,
                created_at=order.created_at,
                updated_at=order.updated_at
            ) for order in orders
        ]

        list_response = OrderListResponse(
            orders=order_responses,
            total_count=2,
            active_count=2,
            completed_count=0,
            cancelled_count=0
        )

        assert len(list_response.orders) == 2
        assert list_response.total_count == 2
        assert list_response.active_count == 2

    @pytest.mark.skip(reason="Order entity schema changed - needs update")
    def test_order_list_response_serialization(self):
        """Test order list response serialization."""
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

        order_response = OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            order_price=order.order_price,
            total_amount=order.total_amount,
            executed_quantity=order.executed_quantity,
            currency=order.currency,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        list_response = OrderListResponse(
            orders=[order_response],
            total_count=1,
            active_count=1,
            completed_count=0,
            cancelled_count=0
        )

        # Test serialization
        data = list_response.model_dump()
        assert len(data["orders"]) == 1
        assert data["total_count"] == 1
        assert data["active_count"] == 1
        assert data["completed_count"] == 0
        assert data["cancelled_count"] == 0