"""
Unit tests for Order utilities.
Tests cover OrderIdGenerator, OrderStatusManager, OrderValidationUtils, and OrderBusinessRules.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.data.entities.order.enums import OrderStatus, OrderType
from src.data.entities.order.utils import (OrderBusinessRules,
                                           OrderIdGenerator,
                                           OrderStatusManager,
                                           OrderStatusTransition,
                                           OrderValidationUtils)
from src.exceptions import CNOPEntityValidationException


class TestOrderIdGenerator:
    """Test OrderIdGenerator utility - Simplified"""

    def test_generate(self):
        """Test generating order ID using new simple method."""
        order_id = OrderIdGenerator.generate()

        # Should start with 'ord_' and have UUID
        assert order_id.startswith('ord_')
        assert len(order_id) == 20  # ord_ (4) + 16 hex chars = 20

        # Should be unique
        order_id2 = OrderIdGenerator.generate()
        assert order_id != order_id2

    def test_generate_order_id(self):
        """Test backward compatibility for generate_order_id()."""
        order_id = OrderIdGenerator.generate_order_id()

        assert order_id.startswith('ord_')
        assert len(order_id) == 20

    def test_generate_simple_order_id(self):
        """Test backward compatibility for generate_simple_order_id()."""
        order_id = OrderIdGenerator.generate_simple_order_id()

        assert order_id.startswith('ord_')
        assert len(order_id) == 20

    def test_generate_timestamped_order_id(self):
        """Test backward compatibility for generate_timestamped_order_id()."""
        order_id = OrderIdGenerator.generate_timestamped_order_id()

        assert order_id.startswith('ord_')
        assert len(order_id) == 20

    def test_uniqueness(self):
        """Test that generated IDs are unique."""
        ids = set()
        for _ in range(100):
            order_id = OrderIdGenerator.generate()
            ids.add(order_id)

        # All 100 IDs should be unique
        assert len(ids) == 100


class TestOrderStatusManager:
    """Test OrderStatusManager."""

    def test_can_transition(self):
        """Test status transition validation."""
        # Valid transitions
        assert OrderStatusManager.can_transition(OrderStatus.PENDING, OrderStatus.CONFIRMED) is True
        assert OrderStatusManager.can_transition(OrderStatus.CONFIRMED, OrderStatus.PROCESSING) is True
        assert OrderStatusManager.can_transition(OrderStatus.PROCESSING, OrderStatus.COMPLETED) is True

        # Invalid transitions
        assert OrderStatusManager.can_transition(OrderStatus.COMPLETED, OrderStatus.PENDING) is False
        assert OrderStatusManager.can_transition(OrderStatus.CANCELLED, OrderStatus.PROCESSING) is False

    def test_get_valid_transitions(self):
        """Test getting valid transitions."""
        transitions = OrderStatusManager.get_valid_transitions(OrderStatus.PENDING)
        expected = {OrderStatus.CONFIRMED, OrderStatus.CANCELLED, OrderStatus.FAILED}
        assert transitions == expected

    def test_is_terminal_status(self):
        """Test terminal status check."""
        assert OrderStatusManager.is_terminal_status(OrderStatus.COMPLETED) is True
        assert OrderStatusManager.is_terminal_status(OrderStatus.CANCELLED) is True
        assert OrderStatusManager.is_terminal_status(OrderStatus.PENDING) is False

    def test_can_user_cancel(self):
        """Test user cancellation check."""
        assert OrderStatusManager.can_user_cancel(OrderStatus.PENDING) is True
        assert OrderStatusManager.can_user_cancel(OrderStatus.CONFIRMED) is True
        assert OrderStatusManager.can_user_cancel(OrderStatus.PROCESSING) is False

    def test_validate_transition_valid(self):
        """Test valid transition validation."""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.PENDING, OrderStatus.CONFIRMED
        )
        assert is_valid is True
        assert error is None

    def test_validate_transition_invalid(self):
        """Test invalid transition validation."""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.PENDING, OrderStatus.COMPLETED
        )
        assert is_valid is False
        assert error is not None

    def test_validate_transition_terminal_state(self):
        """Test transition from terminal state."""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.COMPLETED, OrderStatus.PENDING
        )
        assert is_valid is False
        # The actual error message is different - it's caught by the first validation check
        assert "Invalid transition" in error

    def test_validate_transition_user_cancellation_allowed(self):
        """Test user cancellation when allowed."""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.PENDING, OrderStatus.CANCELLED, username="user123"
        )
        assert is_valid is True
        assert error is None

    def test_validate_transition_user_cancellation_not_allowed(self):
        """Test user cancellation when not allowed."""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.PROCESSING, OrderStatus.CANCELLED, username="user123"
        )
        assert is_valid is False
        # The actual error message is different - it's caught by the first validation check
        assert "Invalid transition" in error

    def test_validate_transition_system_failed_status(self):
        """Test system setting failed status."""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.PROCESSING, OrderStatus.FAILED, is_system=True
        )
        assert is_valid is True
        assert error is None

    def test_validate_transition_user_failed_status(self):
        """Test user trying to set failed status."""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.PROCESSING, OrderStatus.FAILED, username="user123"
        )
        assert is_valid is False
        assert "Only system can mark orders as failed" in error

    def test_validate_transition_system_expired_status(self):
        """Test system setting expired status."""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.QUEUED, OrderStatus.EXPIRED, is_system=True
        )
        assert is_valid is True
        assert error is None

    def test_validate_transition_user_expired_status(self):
        """Test user trying to set expired status."""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.QUEUED, OrderStatus.EXPIRED, username="user123"
        )
        assert is_valid is False
        assert "Only system can mark orders as expired" in error

    def test_is_active_status(self):
        """Test active status check."""
        assert OrderStatusManager.is_active_status(OrderStatus.PENDING) is True
        assert OrderStatusManager.is_active_status(OrderStatus.CONFIRMED) is True
        assert OrderStatusManager.is_active_status(OrderStatus.COMPLETED) is False


class TestOrderValidationUtils:
    """Test OrderValidationUtils."""

    def test_validate_quantity_range(self):
        """Test quantity range validation."""
        # Valid quantities
        is_valid, error = OrderValidationUtils.validate_quantity_range(Decimal("0.001"))
        assert is_valid is True
        assert error is None

        is_valid, error = OrderValidationUtils.validate_quantity_range(Decimal("100.0"))
        assert is_valid is True
        assert error is None

        # Invalid quantities
        is_valid, error = OrderValidationUtils.validate_quantity_range(Decimal("0.0001"))
        assert is_valid is False
        assert error is not None

        is_valid, error = OrderValidationUtils.validate_quantity_range(Decimal("2000.0"))
        assert is_valid is False
        assert error is not None

    def test_validate_quantity_precision(self):
        """Test quantity precision validation."""
        # Valid precision
        is_valid, error = OrderValidationUtils.validate_quantity_precision(Decimal("0.12345678"))
        assert is_valid is True
        assert error is None

        # Invalid precision (too many decimal places)
        is_valid, error = OrderValidationUtils.validate_quantity_precision(Decimal("0.123456789"))
        assert is_valid is False
        assert "precision cannot exceed" in error

    def test_validate_price_precision(self):
        """Test price precision validation."""
        # Valid precision
        is_valid, error = OrderValidationUtils.validate_price_precision(Decimal("45000.12"))
        assert is_valid is True
        assert error is None

        # Invalid precision (too many decimal places)
        is_valid, error = OrderValidationUtils.validate_price_precision(Decimal("45000.123"))
        assert is_valid is False
        assert "precision cannot exceed" in error

    def test_validate_order_value_buy_orders(self):
        """Test order value validation for buy orders."""
        # Valid value
        is_valid, error = OrderValidationUtils.validate_order_value(
            OrderType.MARKET_BUY, Decimal("1.0"), Decimal("50000.00")
        )
        assert is_valid is True
        assert error is None

        # Invalid value (too low)
        is_valid, error = OrderValidationUtils.validate_order_value(
            OrderType.LIMIT_BUY, Decimal("0.0001"), Decimal("50000.00")
        )
        assert is_valid is False
        assert "must be at least" in error

    def test_validate_order_value_sell_orders(self):
        """Test order value validation for sell orders."""
        # Sell orders don't require minimum value
        is_valid, error = OrderValidationUtils.validate_order_value(
            OrderType.MARKET_SELL, Decimal("0.0001")
        )
        assert is_valid is True
        assert error is None

    def test_validate_order_value_without_price(self):
        """Test order value validation without price (uses default)."""
        # Should use default price for estimation
        is_valid, error = OrderValidationUtils.validate_order_value(
            OrderType.MARKET_BUY, Decimal("1.0")
        )
        assert is_valid is True
        assert error is None

    def test_validate_expiration_time_valid(self):
        """Test valid expiration time validation."""
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        is_valid, error = OrderValidationUtils.validate_expiration_time(future_time)
        assert is_valid is True
        assert error is None

    def test_validate_expiration_time_past(self):
        """Test past expiration time validation."""
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        is_valid, error = OrderValidationUtils.validate_expiration_time(past_time)
        assert is_valid is False
        assert "must be in the future" in error

    def test_validate_expiration_time_too_far(self):
        """Test expiration time too far in future."""
        far_future = datetime.now(timezone.utc) + timedelta(days=31)
        is_valid, error = OrderValidationUtils.validate_expiration_time(far_future)
        assert is_valid is False
        assert "cannot be more than" in error

    def test_validate_expiration_time_none(self):
        """Test expiration time validation with None."""
        is_valid, error = OrderValidationUtils.validate_expiration_time(None)
        assert is_valid is True
        assert error is None


    def test_validate_order_type_requirements_limit_orders(self):
        """Test order type requirements for limit orders."""
        # Valid limit order with price
        is_valid, error = OrderValidationUtils.validate_order_type_requirements(
            OrderType.LIMIT_BUY, Decimal("45000.00")
        )
        assert is_valid is True
        assert error is None

        # Invalid limit order without price
        is_valid, error = OrderValidationUtils.validate_order_type_requirements(
            OrderType.LIMIT_SELL, None
        )
        assert is_valid is False
        assert "require an order_price" in error

    def test_validate_order_type_requirements_market_orders(self):
        """Test order type requirements for market orders."""
        # Valid market order without price
        is_valid, error = OrderValidationUtils.validate_order_type_requirements(
            OrderType.MARKET_BUY, None
        )
        assert is_valid is True
        assert error is None

        # Invalid market order with price
        is_valid, error = OrderValidationUtils.validate_order_type_requirements(
            OrderType.MARKET_SELL, Decimal("45000.00")
        )
        assert is_valid is False
        assert "should not specify order_price" in error


class TestOrderBusinessRules:
    """Test OrderBusinessRules."""

    def test_validate_all_business_rules_valid(self):
        """Test business rules validation for valid order."""
        errors = OrderBusinessRules.validate_all_business_rules(
            order_type=OrderType.MARKET_BUY,
            quantity=Decimal("1.0"),
            order_price=None  # Market orders shouldn't specify order_price
        )

        assert len(errors) == 0

    def test_validate_all_business_rules_valid_limit_order(self):
        """Test business rules validation for valid limit order."""
        errors = OrderBusinessRules.validate_all_business_rules(
            order_type=OrderType.LIMIT_BUY,
            quantity=Decimal("1.0"),
            order_price=Decimal("45000.00")
        )

        assert len(errors) == 0

    def test_validate_all_business_rules_invalid(self):
        """Test business rules validation for invalid order."""
        errors = OrderBusinessRules.validate_all_business_rules(
            order_type=OrderType.MARKET_BUY,
            quantity=Decimal("0.0001"),  # Too small
            order_price=None
        )

        assert len(errors) > 0
        assert any("quantity" in error.lower() for error in errors)

    def test_validate_all_business_rules_multiple_errors(self):
        """Test business rules validation with multiple errors."""
        errors = OrderBusinessRules.validate_all_business_rules(
            order_type=OrderType.LIMIT_BUY,
            quantity=Decimal("0.0001"),  # Too small
            order_price=Decimal("45000.123"),  # Too many decimal places
            expires_at=datetime.now(timezone.utc) + timedelta(days=31)  # Too far in future
        )

        assert len(errors) >= 3  # Should have multiple validation errors


class TestOrderStatusTransition:
    """Test OrderStatusTransition model."""

    def test_order_status_transition_creation(self):
        """Test creating OrderStatusTransition."""
        transition = OrderStatusTransition(
            from_status=OrderStatus.PENDING,
            to_status=OrderStatus.CONFIRMED,
            reason="User confirmed order",
            changed_by="user123"
        )

        assert transition.from_status == OrderStatus.PENDING
        assert transition.to_status == OrderStatus.CONFIRMED
        assert transition.reason == "User confirmed order"
        assert transition.changed_by == "user123"
        assert transition.context == {}

    def test_order_status_transition_defaults(self):
        """Test OrderStatusTransition with default values."""
        transition = OrderStatusTransition(
            from_status=OrderStatus.PENDING,
            to_status=OrderStatus.CONFIRMED
        )

        assert transition.reason is None
        assert transition.changed_by is None
        assert transition.context == {}
        assert transition.changed_at is not None