"""
Unit tests for Order utilities.
Tests cover OrderIdGenerator, OrderStatusManager, OrderValidationUtils, and OrderBusinessRules.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from src.entities.order.utils import OrderIdGenerator, OrderStatusManager, OrderValidationUtils, OrderBusinessRules
from src.entities.order.enums import OrderType, OrderStatus


class TestOrderIdGenerator:
    """Test OrderIdGenerator utility."""

    def test_generate_order_id(self):
        """Test generating order ID."""
        order_id = OrderIdGenerator.generate_order_id()

        # Should start with 'ord' and contain separator
        assert order_id.startswith('ord')
        assert OrderIdGenerator.SEPARATOR in order_id
        assert len(order_id) > 10

    def test_generate_order_id_with_user_id(self):
        """Test generating order ID with user ID."""
        user_id = "user123"
        order_id = OrderIdGenerator.generate_order_id(user_id)

        # Should contain user ID
        assert user_id in order_id
        assert order_id.startswith('ord')

    def test_generate_simple_order_id(self):
        """Test generating simple order ID."""
        order_id = OrderIdGenerator.generate_simple_order_id()

        # Should start with 'ord' and be reasonable length
        assert order_id.startswith('ord')
        assert len(order_id) > 10

    def test_generate_timestamped_order_id(self):
        """Test generating timestamped order ID."""
        order_id = OrderIdGenerator.generate_timestamped_order_id()

        # Should start with 'ord' and contain timestamp
        assert order_id.startswith('ord')
        assert len(order_id) > 10

        # Should be parseable
        parsed = OrderIdGenerator.parse_order_id(order_id)
        assert parsed['prefix'] == 'ord'
        assert 'unique_id' in parsed

    def test_parse_order_id(self):
        """Test parsing order ID."""
        order_id = "ord_20231201123456789_user123"
        parsed = OrderIdGenerator.parse_order_id(order_id)

        assert parsed['prefix'] == 'ord'
        assert parsed['unique_id'] == 'user123'
        # user_id is only present if there are 4+ parts
        assert 'user_id' not in parsed  # This format has 3 parts, so no user_id

    def test_parse_order_id_with_user_id(self):
        """Test parsing order ID with user ID."""
        order_id = "ord_20231201123456789_abc123def_user123"
        parsed = OrderIdGenerator.parse_order_id(order_id)

        assert parsed['prefix'] == 'ord'
        assert parsed['unique_id'] == 'user123'
        assert parsed['user_id'] == 'user123'  # This format has 4+ parts, so user_id is present

    def test_is_valid_order_id(self):
        """Test validating order ID."""
        valid_id = "ord_20231201123456789_user123"
        invalid_id = "invalid_id"

        assert OrderIdGenerator.is_valid_order_id(valid_id) is True
        assert OrderIdGenerator.is_valid_order_id(invalid_id) is False


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

    def test_validate_currency(self):
        """Test currency validation."""
        # Valid currencies
        is_valid, error = OrderValidationUtils.validate_currency("USD")
        assert is_valid is True
        assert error is None

        # Invalid currencies
        is_valid, error = OrderValidationUtils.validate_currency("INVALID")
        assert is_valid is False
        assert error is not None


class TestOrderBusinessRules:
    """Test OrderBusinessRules."""

    def test_validate_all_business_rules_valid(self):
        """Test business rules validation for valid order."""
        errors = OrderBusinessRules.validate_all_business_rules(
            order_type=OrderType.MARKET_BUY,
            quantity=Decimal("1.0"),
            price_per_unit=None,  # Market orders shouldn't specify price_per_unit
            currency="USD"
        )

        assert len(errors) == 0

    def test_validate_all_business_rules_valid_limit_order(self):
        """Test business rules validation for valid limit order."""
        errors = OrderBusinessRules.validate_all_business_rules(
            order_type=OrderType.LIMIT_BUY,
            quantity=Decimal("1.0"),
            limit_price=Decimal("45000.00"),
            price_per_unit=Decimal("45000.00"),
            currency="USD"
        )

        assert len(errors) == 0

    def test_validate_all_business_rules_invalid(self):
        """Test business rules validation for invalid order."""
        errors = OrderBusinessRules.validate_all_business_rules(
            order_type=OrderType.MARKET_BUY,
            quantity=Decimal("0.0001"),  # Too small
            price_per_unit=None,
            currency="INVALID"  # Invalid currency
        )

        assert len(errors) > 0