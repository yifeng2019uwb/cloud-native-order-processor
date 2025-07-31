"""
Unit tests for OrderResponse models.
Tests cover OrderResponse and OrderListResponse entity classes.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

import pytest
from decimal import Decimal
from datetime import datetime, timezone

from src.entities.order.orderResponse import OrderResponse, OrderListResponse
from src.entities.order.order import Order
from src.entities.order.enums import OrderType, OrderStatus


class TestOrderResponse:
    """Test OrderResponse model."""

    def test_order_response(self):
        """Test order response."""
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

        response = OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            price_per_unit=order.price_per_unit,
            total_amount=order.total_amount,
            executed_quantity=order.executed_quantity,
            currency=order.currency,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        assert response.order_id == order.order_id
        assert response.user_id == order.user_id
        assert response.order_type == order.order_type
        assert response.asset_id == order.asset_id
        assert response.quantity == order.quantity
        assert response.price_per_unit == order.price_per_unit
        assert response.currency == order.currency
        assert response.status == order.status

    def test_order_response_with_executed_quantity(self):
        """Test order response with executed quantity."""
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

        response = OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            price_per_unit=order.price_per_unit,
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
            price_per_unit=None,
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
            price_per_unit=order.price_per_unit,
            total_amount=order.total_amount,
            executed_quantity=order.executed_quantity,
            currency=order.currency,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        # Test model_dump
        data = response.model_dump()
        assert data['order_id'] == order.order_id
        assert data['user_id'] == order.user_id
        assert data['order_type'] == order.order_type.value
        assert data['asset_id'] == order.asset_id
        assert data['quantity'] == order.quantity  # model_dump returns Decimal, not string
        assert data['currency'] == order.currency
        assert data['status'] == order.status.value


class TestOrderListResponse:
    """Test OrderListResponse model."""

    def test_order_list_response(self):
        """Test order list response."""
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

        order_response = OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            price_per_unit=order.price_per_unit,
            total_amount=order.total_amount,
            executed_quantity=order.executed_quantity,
            currency=order.currency,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        response = OrderListResponse(
            orders=[order_response],
            total_count=1,
            active_count=1,
            completed_count=0,
            cancelled_count=0
        )

        assert len(response.orders) == 1
        assert response.orders[0].order_id == order.order_id

    def test_order_list_response_empty(self):
        """Test order list response with empty orders."""
        response = OrderListResponse(
            orders=[],
            total_count=0,
            active_count=0,
            completed_count=0,
            cancelled_count=0
        )

        assert len(response.orders) == 0

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
                price_per_unit=None,
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
                price_per_unit=Decimal("3000.00"),
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
                price_per_unit=order.price_per_unit,
                total_amount=order.total_amount,
                executed_quantity=order.executed_quantity,
                currency=order.currency,
                status=order.status,
                created_at=order.created_at,
                updated_at=order.updated_at
            ) for order in orders
        ]

        response = OrderListResponse(
            orders=order_responses,
            total_count=2,
            active_count=1,
            completed_count=0,
            cancelled_count=0
        )

        assert len(response.orders) == 2
        assert response.orders[0].order_id == orders[0].order_id
        assert response.orders[1].order_id == orders[1].order_id
        assert response.orders[0].asset_id == "BTC"
        assert response.orders[1].asset_id == "ETH"

    def test_order_list_response_serialization(self):
        """Test order list response serialization."""
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

        order_response = OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            price_per_unit=order.price_per_unit,
            total_amount=order.total_amount,
            executed_quantity=order.executed_quantity,
            currency=order.currency,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

        response = OrderListResponse(
            orders=[order_response],
            total_count=1,
            active_count=1,
            completed_count=0,
            cancelled_count=0
        )

        # Test model_dump
        data = response.model_dump()
        assert 'orders' in data
        assert len(data['orders']) == 1
        assert data['orders'][0]['order_id'] == order.order_id