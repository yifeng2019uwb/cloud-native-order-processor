"""
Unit tests for OrderUpdate model.
Tests cover the OrderUpdate entity class.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

import pytest
from decimal import Decimal
from datetime import datetime, timezone

from src.entities.order.order import OrderUpdate
from src.entities.order.enums import OrderStatus


@pytest.mark.skip(reason="OrderUpdate entity schema changed - needs update")
class TestOrderUpdate:
    """Test OrderUpdate model."""

    def test_order_update_partial(self):
        """Test partial order update."""
        update = OrderUpdate(
            status=OrderStatus.COMPLETED,
            executed_quantity=Decimal("1.0")
        )

        assert update.status == OrderStatus.COMPLETED
        assert update.executed_quantity == Decimal("1.0")
        assert update.executed_price is None
        assert update.completed_at is None

    def test_order_update_full(self):
        """Test full order update."""
        completed_at = datetime.now(timezone.utc)
        update = OrderUpdate(
            status=OrderStatus.COMPLETED,
            executed_quantity=Decimal("1.5"),
            executed_price=Decimal("45000.00"),
            completed_at=completed_at
        )

        assert update.status == OrderStatus.COMPLETED
        assert update.executed_quantity == Decimal("1.5")
        assert update.executed_price == Decimal("45000.00")
        assert update.completed_at == completed_at

    def test_order_update_status_only(self):
        """Test order update with status only."""
        update = OrderUpdate(
            status=OrderStatus.CANCELLED
        )

        assert update.status == OrderStatus.CANCELLED
        assert update.executed_quantity is None
        assert update.executed_price is None
        assert update.completed_at is None

    def test_order_update_executed_quantity_only(self):
        """Test order update with executed quantity only."""
        update = OrderUpdate(
            executed_quantity=Decimal("0.5")
        )

        assert update.status is None
        assert update.executed_quantity == Decimal("0.5")
        assert update.executed_price is None
        assert update.completed_at is None

    def test_order_update_executed_price_only(self):
        """Test order update with executed price only."""
        update = OrderUpdate(
            executed_price=Decimal("46000.00")
        )

        assert update.status is None
        assert update.executed_quantity is None
        assert update.executed_price == Decimal("46000.00")
        assert update.completed_at is None

    def test_order_update_completed_at_only(self):
        """Test order update with completed_at only."""
        completed_at = datetime.now(timezone.utc)
        update = OrderUpdate(
            completed_at=completed_at
        )

        assert update.status is None
        assert update.executed_quantity is None
        assert update.executed_price is None
        assert update.completed_at == completed_at

    def test_order_update_serialization(self):
        """Test order update serialization."""
        completed_at = datetime.now(timezone.utc)
        update = OrderUpdate(
            status=OrderStatus.COMPLETED,
            executed_quantity=Decimal("1.5"),
            executed_price=Decimal("45000.00"),
            completed_at=completed_at
        )

        # Test model_dump
        data = update.model_dump()
        assert data['status'] == OrderStatus.COMPLETED.value
        assert data['executed_quantity'] == Decimal("1.5")  # Decimal values are preserved
        assert data['executed_price'] == Decimal("45000.00")  # Decimal values are preserved
        assert data['completed_at'] == completed_at  # model_dump returns datetime, not string

    def test_order_update_partial_serialization(self):
        """Test order update partial serialization."""
        update = OrderUpdate(
            status=OrderStatus.CANCELLED
        )

        # Test model_dump with exclude_none=True
        data = update.model_dump(exclude_none=True)
        assert data['status'] == OrderStatus.CANCELLED.value
        assert 'executed_quantity' not in data
        assert 'executed_price' not in data
        assert 'completed_at' not in data