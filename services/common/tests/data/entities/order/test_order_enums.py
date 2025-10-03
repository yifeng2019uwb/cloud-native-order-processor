"""
Tests for Order enums.
"""

import pytest

from src.data.entities.order.enums import OrderStatus, OrderType


class TestOrderEnums:
    """Test cases for Order enums."""

    def test_order_type_values(self):
        """Test OrderType enum values."""
        assert OrderType.MARKET_BUY.value == "market_buy"
        assert OrderType.MARKET_SELL.value == "market_sell"
        assert OrderType.LIMIT_BUY.value == "limit_buy"
        assert OrderType.LIMIT_SELL.value == "limit_sell"

    def test_order_status_values(self):
        """Test OrderStatus enum values."""
        assert OrderStatus.PENDING.value == "pending"
        assert OrderStatus.CONFIRMED.value == "confirmed"
        assert OrderStatus.QUEUED.value == "queued"
        assert OrderStatus.TRIGGERED.value == "triggered"
        assert OrderStatus.PROCESSING.value == "processing"
        assert OrderStatus.COMPLETED.value == "completed"
        assert OrderStatus.CANCELLED.value == "cancelled"
        assert OrderStatus.FAILED.value == "failed"
        assert OrderStatus.EXPIRED.value == "expired"

    def test_order_type_enum_members(self):
        """Test OrderType enum members."""
        assert OrderType.MARKET_BUY in OrderType
        assert OrderType.MARKET_SELL in OrderType
        assert OrderType.LIMIT_BUY in OrderType
        assert OrderType.LIMIT_SELL in OrderType

    def test_order_status_enum_members(self):
        """Test OrderStatus enum members."""
        assert OrderStatus.PENDING in OrderStatus
        assert OrderStatus.CONFIRMED in OrderStatus
        assert OrderStatus.QUEUED in OrderStatus
        assert OrderStatus.TRIGGERED in OrderStatus
        assert OrderStatus.PROCESSING in OrderStatus
        assert OrderStatus.COMPLETED in OrderStatus
        assert OrderStatus.CANCELLED in OrderStatus
        assert OrderStatus.FAILED in OrderStatus
        assert OrderStatus.EXPIRED in OrderStatus