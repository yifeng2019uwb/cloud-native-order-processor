"""
Unit tests for Order utilities
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

# Test constants
TEST_USERNAME = "testuser"
TEST_QUANTITY_1_0 = Decimal("1.0")
TEST_QUANTITY_0_001 = Decimal("0.001")  # At minimum threshold
TEST_QUANTITY_0_0001 = Decimal("0.0001")  # Below minimum threshold
TEST_QUANTITY_1000_0 = Decimal("1000.0")
TEST_QUANTITY_0_000000001 = Decimal("0.000000001")  # Too many decimal places (9 places)
TEST_QUANTITY_1001_0 = Decimal("1001.0")  # Too large
TEST_PRICE_50000 = Decimal("50000.00")
TEST_PRICE_50000_123 = Decimal("50000.123")  # Too many decimal places
TEST_PRICE_50000_1 = Decimal("50000.1")
TEST_MIN_ORDER_VALUE = Decimal("10.00")
TEST_ORDER_VALUE_5 = Decimal("5.00")  # Below minimum
TEST_ORDER_VALUE_15 = Decimal("15.00")  # Above minimum
TEST_EXPIRATION_DAYS_1 = 1
TEST_EXPIRATION_DAYS_31 = 31  # Too many days
TEST_REASON_CANCELLED = "User requested cancellation"
TEST_CONTEXT_DATA = {"reason": "test"}


class TestOrderIdGenerator:
    """Test OrderIdGenerator utility"""

    def test_generate(self):
        """Test generating order ID"""
        order_id = OrderIdGenerator.generate()
        assert order_id.startswith('ord_')
        assert len(order_id) == 20  # ord_ (4) + 16 hex chars = 20

    def test_generate_uniqueness(self):
        """Test that generated IDs are unique"""
        ids = set()
        for _ in range(10):
            order_id = OrderIdGenerator.generate()
            ids.add(order_id)
        assert len(ids) == 10

    def test_generate_order_id_backward_compatibility(self):
        """Test backward compatibility for generate_order_id()"""
        order_id = OrderIdGenerator.generate_order_id()
        assert order_id.startswith('ord_')
        assert len(order_id) == 20

    def test_generate_simple_order_id_backward_compatibility(self):
        """Test backward compatibility for generate_simple_order_id()"""
        order_id = OrderIdGenerator.generate_simple_order_id()
        assert order_id.startswith('ord_')
        assert len(order_id) == 20

    def test_generate_timestamped_order_id_backward_compatibility(self):
        """Test backward compatibility for generate_timestamped_order_id()"""
        order_id = OrderIdGenerator.generate_timestamped_order_id()
        assert order_id.startswith('ord_')
        assert len(order_id) == 20


class TestOrderStatusTransition:
    """Test OrderStatusTransition model"""

    def test_status_transition_creation(self):
        """Test creating status transition"""
        transition = OrderStatusTransition(
            from_status=OrderStatus.PENDING,
            to_status=OrderStatus.CONFIRMED,
            reason=TEST_REASON_CANCELLED,
            changed_by=TEST_USERNAME,
            context=TEST_CONTEXT_DATA
        )
        assert transition.from_status == OrderStatus.PENDING
        assert transition.to_status == OrderStatus.CONFIRMED
        assert transition.reason == TEST_REASON_CANCELLED
        assert transition.changed_by == TEST_USERNAME
        assert transition.context == TEST_CONTEXT_DATA
        assert transition.changed_at is not None

    def test_status_transition_defaults(self):
        """Test status transition with defaults"""
        transition = OrderStatusTransition(
            from_status=OrderStatus.PENDING,
            to_status=OrderStatus.CONFIRMED
        )
        assert transition.reason is None
        assert transition.changed_by is None
        assert transition.context == {}
        assert transition.changed_at is not None


class TestOrderStatusManager:
    """Test OrderStatusManager"""

    def test_can_transition_valid(self):
        """Test valid status transitions"""
        assert OrderStatusManager.can_transition(OrderStatus.PENDING, OrderStatus.CONFIRMED) is True
        assert OrderStatusManager.can_transition(OrderStatus.CONFIRMED, OrderStatus.PROCESSING) is True
        assert OrderStatusManager.can_transition(OrderStatus.PROCESSING, OrderStatus.COMPLETED) is True

    def test_can_transition_invalid(self):
        """Test invalid status transitions"""
        assert OrderStatusManager.can_transition(OrderStatus.COMPLETED, OrderStatus.PENDING) is False
        assert OrderStatusManager.can_transition(OrderStatus.CANCELLED, OrderStatus.PROCESSING) is False

    def test_validate_transition_valid(self):
        """Test valid transition validation"""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.PENDING, OrderStatus.CONFIRMED, TEST_USERNAME
        )
        assert is_valid is True
        assert error is None

    def test_validate_transition_invalid_structure(self):
        """Test invalid transition structure"""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.COMPLETED, OrderStatus.PENDING, TEST_USERNAME
        )
        assert is_valid is False
        assert "Invalid transition" in error

    def test_validate_transition_terminal_state(self):
        """Test transition from terminal state"""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.COMPLETED, OrderStatus.CONFIRMED, TEST_USERNAME
        )
        assert is_valid is False
        assert "Invalid transition" in error  # The error message is about invalid transition, not terminal state

    def test_validate_transition_user_cancellation_allowed(self):
        """Test user cancellation when allowed"""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.PENDING, OrderStatus.CANCELLED, TEST_USERNAME, is_system=False
        )
        assert is_valid is True
        assert error is None

    def test_validate_transition_user_cancellation_not_allowed(self):
        """Test user cancellation when not allowed"""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.PROCESSING, OrderStatus.CANCELLED, TEST_USERNAME, is_system=False
        )
        assert is_valid is False
        assert "Invalid transition" in error  # The error message is about invalid transition, not user cancellation

    def test_validate_transition_system_failed(self):
        """Test system setting failed status"""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.PROCESSING, OrderStatus.FAILED, TEST_USERNAME, is_system=True
        )
        assert is_valid is True
        assert error is None

    def test_validate_transition_user_failed_not_allowed(self):
        """Test user cannot set failed status"""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.PROCESSING, OrderStatus.FAILED, TEST_USERNAME, is_system=False
        )
        assert is_valid is False
        assert "Only system can mark orders as failed" in error

    def test_validate_transition_user_expired_not_allowed(self):
        """Test user cannot set expired status"""
        is_valid, error = OrderStatusManager.validate_transition(
            OrderStatus.QUEUED, OrderStatus.EXPIRED, TEST_USERNAME, is_system=False
        )
        assert is_valid is False
        assert "Only system can mark orders as expired" in error

    def test_get_valid_transitions(self):
        """Test getting valid transitions"""
        transitions = OrderStatusManager.get_valid_transitions(OrderStatus.PENDING)
        expected = {OrderStatus.CONFIRMED, OrderStatus.CANCELLED, OrderStatus.FAILED}
        assert transitions == expected

    def test_is_terminal_status(self):
        """Test terminal status check"""
        assert OrderStatusManager.is_terminal_status(OrderStatus.COMPLETED) is True
        assert OrderStatusManager.is_terminal_status(OrderStatus.CANCELLED) is True
        assert OrderStatusManager.is_terminal_status(OrderStatus.FAILED) is True
        assert OrderStatusManager.is_terminal_status(OrderStatus.EXPIRED) is True
        assert OrderStatusManager.is_terminal_status(OrderStatus.PENDING) is False

    def test_is_active_status(self):
        """Test active status check"""
        assert OrderStatusManager.is_active_status(OrderStatus.PENDING) is True
        assert OrderStatusManager.is_active_status(OrderStatus.CONFIRMED) is True
        assert OrderStatusManager.is_active_status(OrderStatus.COMPLETED) is False
        assert OrderStatusManager.is_active_status(OrderStatus.CANCELLED) is False

    def test_can_user_cancel(self):
        """Test user cancellation check"""
        assert OrderStatusManager.can_user_cancel(OrderStatus.PENDING) is True
        assert OrderStatusManager.can_user_cancel(OrderStatus.CONFIRMED) is True
        assert OrderStatusManager.can_user_cancel(OrderStatus.QUEUED) is True
        assert OrderStatusManager.can_user_cancel(OrderStatus.PROCESSING) is False
        assert OrderStatusManager.can_user_cancel(OrderStatus.COMPLETED) is False


class TestOrderValidationUtils:
    """Test OrderValidationUtils"""

    def test_validate_quantity_range_valid(self):
        """Test valid quantity range"""
        is_valid, error = OrderValidationUtils.validate_quantity_range(TEST_QUANTITY_1_0)
        assert is_valid is True
        assert error is None

    def test_validate_quantity_range_minimum(self):
        """Test quantity at minimum threshold"""
        is_valid, error = OrderValidationUtils.validate_quantity_range(TEST_QUANTITY_0_001)
        assert is_valid is True
        assert error is None

    def test_validate_quantity_range_maximum(self):
        """Test quantity at maximum threshold"""
        is_valid, error = OrderValidationUtils.validate_quantity_range(TEST_QUANTITY_1000_0)
        assert is_valid is True
        assert error is None

    def test_validate_quantity_range_too_small(self):
        """Test quantity below minimum"""
        is_valid, error = OrderValidationUtils.validate_quantity_range(TEST_QUANTITY_0_0001)
        assert is_valid is False
        assert "below minimum threshold" in error

    def test_validate_quantity_range_too_large(self):
        """Test quantity above maximum"""
        is_valid, error = OrderValidationUtils.validate_quantity_range(TEST_QUANTITY_1001_0)
        assert is_valid is False
        assert "exceeds maximum threshold" in error

    def test_validate_quantity_precision_valid(self):
        """Test valid quantity precision"""
        is_valid, error = OrderValidationUtils.validate_quantity_precision(TEST_QUANTITY_1_0)
        assert is_valid is True
        assert error is None

    def test_validate_quantity_precision_invalid(self):
        """Test invalid quantity precision"""
        is_valid, error = OrderValidationUtils.validate_quantity_precision(TEST_QUANTITY_0_000000001)
        assert is_valid is False
        assert "precision cannot exceed" in error

    def test_validate_price_precision_valid(self):
        """Test valid price precision"""
        is_valid, error = OrderValidationUtils.validate_price_precision(TEST_PRICE_50000)
        assert is_valid is True
        assert error is None

    def test_validate_price_precision_invalid(self):
        """Test invalid price precision"""
        is_valid, error = OrderValidationUtils.validate_price_precision(TEST_PRICE_50000_123)
        assert is_valid is False
        assert "precision cannot exceed" in error

    def test_validate_order_value_market_buy_valid(self):
        """Test valid market buy order value"""
        is_valid, error = OrderValidationUtils.validate_order_value(
            OrderType.MARKET_BUY, TEST_QUANTITY_1_0, TEST_PRICE_50000
        )
        assert is_valid is True
        assert error is None

    def test_validate_order_value_market_buy_invalid(self):
        """Test invalid market buy order value"""
        small_quantity = Decimal("0.0001")  # Will result in value < $10
        is_valid, error = OrderValidationUtils.validate_order_value(
            OrderType.MARKET_BUY, small_quantity, TEST_PRICE_50000
        )
        assert is_valid is False
        assert "Order value must be at least" in error

    def test_validate_order_value_limit_buy_valid(self):
        """Test valid limit buy order value"""
        is_valid, error = OrderValidationUtils.validate_order_value(
            OrderType.LIMIT_BUY, TEST_QUANTITY_1_0, TEST_PRICE_50000
        )
        assert is_valid is True
        assert error is None

    def test_validate_order_value_sell_orders(self):
        """Test sell orders don't require minimum value"""
        is_valid, error = OrderValidationUtils.validate_order_value(
            OrderType.MARKET_SELL, TEST_QUANTITY_0_001, TEST_PRICE_50000
        )
        assert is_valid is True
        assert error is None

    def test_validate_expiration_time_valid(self):
        """Test valid expiration time"""
        future_time = datetime.now(timezone.utc) + timedelta(days=TEST_EXPIRATION_DAYS_1)
        is_valid, error = OrderValidationUtils.validate_expiration_time(future_time)
        assert is_valid is True
        assert error is None

    def test_validate_expiration_time_none(self):
        """Test None expiration time (valid)"""
        is_valid, error = OrderValidationUtils.validate_expiration_time(None)
        assert is_valid is True
        assert error is None

    def test_validate_expiration_time_past(self):
        """Test past expiration time"""
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        is_valid, error = OrderValidationUtils.validate_expiration_time(past_time)
        assert is_valid is False
        assert "must be in the future" in error

    def test_validate_expiration_time_too_far(self):
        """Test expiration time too far in future"""
        far_future = datetime.now(timezone.utc) + timedelta(days=TEST_EXPIRATION_DAYS_31)
        is_valid, error = OrderValidationUtils.validate_expiration_time(far_future)
        assert is_valid is False
        assert "cannot be more than" in error

    def test_validate_order_type_requirements_limit_with_price(self):
        """Test limit order with price (valid)"""
        is_valid, error = OrderValidationUtils.validate_order_type_requirements(
            OrderType.LIMIT_BUY, TEST_PRICE_50000
        )
        assert is_valid is True
        assert error is None

    def test_validate_order_type_requirements_limit_without_price(self):
        """Test limit order without price (invalid)"""
        is_valid, error = OrderValidationUtils.validate_order_type_requirements(
            OrderType.LIMIT_BUY, None
        )
        assert is_valid is False
        assert "require an order_price" in error

    def test_validate_order_type_requirements_market_with_price(self):
        """Test market order with price (invalid)"""
        is_valid, error = OrderValidationUtils.validate_order_type_requirements(
            OrderType.MARKET_BUY, TEST_PRICE_50000
        )
        assert is_valid is False
        assert "should not specify order_price" in error

    def test_validate_order_type_requirements_market_without_price(self):
        """Test market order without price (valid)"""
        is_valid, error = OrderValidationUtils.validate_order_type_requirements(
            OrderType.MARKET_BUY, None
        )
        assert is_valid is True
        assert error is None


class TestOrderBusinessRules:
    """Test OrderBusinessRules"""

    def test_validate_all_business_rules_valid(self):
        """Test valid business rules"""
        errors = OrderBusinessRules.validate_all_business_rules(
            OrderType.MARKET_BUY, TEST_QUANTITY_1_0, None  # MARKET orders should not have price
        )
        assert errors == []

    def test_validate_all_business_rules_invalid_quantity(self):
        """Test invalid quantity business rules"""
        errors = OrderBusinessRules.validate_all_business_rules(
            OrderType.MARKET_BUY, TEST_QUANTITY_0_0001, None  # MARKET_BUY should not have price
        )
        assert len(errors) > 0
        assert any("below minimum threshold" in error for error in errors)

    def test_validate_all_business_rules_invalid_price_precision(self):
        """Test invalid price precision business rules"""
        errors = OrderBusinessRules.validate_all_business_rules(
            OrderType.LIMIT_BUY, TEST_QUANTITY_1_0, TEST_PRICE_50000_123
        )
        assert len(errors) > 0
        assert any("precision cannot exceed" in error for error in errors)

    def test_validate_all_business_rules_invalid_order_type(self):
        """Test invalid order type business rules"""
        errors = OrderBusinessRules.validate_all_business_rules(
            OrderType.LIMIT_BUY, TEST_QUANTITY_1_0, None  # Missing price for limit order
        )
        assert len(errors) > 0
        assert any("require an order_price" in error for error in errors)

    def test_validate_all_business_rules_invalid_expiration(self):
        """Test invalid expiration business rules"""
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        errors = OrderBusinessRules.validate_all_business_rules(
            OrderType.MARKET_BUY, TEST_QUANTITY_1_0, None, past_time
        )
        assert len(errors) > 0
        assert any("must be in the future" in error for error in errors)