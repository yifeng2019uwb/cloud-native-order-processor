"""
Tests for OrderUpdate model.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timezone

from src.entities.order.order import OrderUpdate
from src.entities.order.enums import OrderStatus


class TestOrderUpdate:
    """Test cases for OrderUpdate model."""

    def test_valid_order_update_with_status(self):
        """Test valid order update with status."""
        order_update = OrderUpdate(
            status=OrderStatus.COMPLETED
        )

        assert order_update.status == OrderStatus.COMPLETED

    def test_valid_order_update_without_status(self):
        """Test valid order update without status."""
        order_update = OrderUpdate()

        assert order_update.status is None

    def test_order_update_with_none_status(self):
        """Test order update with explicit None status."""
        order_update = OrderUpdate(
            status=None
        )

        assert order_update.status is None

    def test_order_update_different_statuses(self):
        """Test order update with different status values."""
        statuses = [
            OrderStatus.PENDING,
            OrderStatus.COMPLETED,
            OrderStatus.CANCELLED,
            OrderStatus.FAILED
        ]

        for status in statuses:
            order_update = OrderUpdate(status=status)
            assert order_update.status == status

    def test_order_update_model_validation(self):
        """Test that OrderUpdate model validates correctly."""
        # This should work without any fields
        order_update = OrderUpdate()
        assert isinstance(order_update, OrderUpdate)

        # This should work with status
        order_update = OrderUpdate(status=OrderStatus.PENDING)
        assert isinstance(order_update, OrderUpdate)
        assert order_update.status == OrderStatus.PENDING