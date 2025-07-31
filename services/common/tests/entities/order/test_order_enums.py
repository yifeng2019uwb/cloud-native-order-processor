"""
Unit tests for Order enums.
Tests cover OrderType and OrderStatus enums.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

import pytest
from src.entities.order.enums import OrderType, OrderStatus


class TestOrderEnums:
    """Test OrderType and OrderStatus enums."""

    def test_order_type_values(self):
        """Test OrderType enum values."""
        assert OrderType.MARKET_BUY.value == "market_buy"
        assert OrderType.MARKET_SELL.value == "market_sell"
        assert OrderType.LIMIT_BUY.value == "limit_buy"
        assert OrderType.LIMIT_SELL.value == "limit_sell"
        assert OrderType.STOP_LOSS.value == "stop_loss"
        assert OrderType.TAKE_PROFIT.value == "take_profit"

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