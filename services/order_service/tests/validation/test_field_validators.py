"""
Unit tests for Order Service Field Validators

Testing all validation functions to improve coverage.
"""

import pytest
import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta

# Add the src directory to Python path to resolve imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import exceptions and enums
from order_exceptions import CNOPOrderValidationException
from common.data.entities.order.enums import OrderType, OrderStatus

# Import the actual validation functions
from validation.field_validators import (
        sanitize_string,
        is_suspicious,
        validate_order_id,
        validate_username,
        validate_asset_id,
        validate_quantity,
        validate_price,
        validate_order_type,
        validate_order_status,
        validate_expires_at,
        validate_limit,
        validate_offset
    )


class TestFieldValidators:
    """Test class for field validation functions"""

    def test_sanitize_string_basic(self):
        """Test basic string sanitization"""
        # Test with normal string
        result = sanitize_string("Hello World")
        assert result == "Hello World"

        # Test with string containing HTML
        result = sanitize_string("<script>alert('xss')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result

        # Test with string containing special characters
        result = sanitize_string("Hello & World")
        assert result == "Hello & World"  # & is not HTML, so it's preserved

        # Test with max length
        result = sanitize_string("Hello World", max_length=5)
        assert result == "Hello"

    def test_sanitize_string_edge_cases(self):
        """Test sanitize_string edge cases"""
        # Test with non-string input
        result = sanitize_string(123)
        assert result == "123"

        # Test with None
        result = sanitize_string(None)
        assert result == "None"

        # Test with empty string
        result = sanitize_string("")
        assert result == ""

        # Test with whitespace only
        result = sanitize_string("   ")
        assert result == ""

    def test_is_suspicious_basic(self):
        """Test suspicious content detection"""
        # Test with normal string
        result = is_suspicious("Hello World")
        assert result is False

        # Test with suspicious content
        result = is_suspicious("<script>alert('xss')</script>")
        assert result is True

        # Test with javascript protocol
        result = is_suspicious("javascript:alert('xss')")
        assert result is True

        # Test with data protocol
        result = is_suspicious("data:text/html,<script>alert('xss')</script>")
        assert result is True

    def test_is_suspicious_edge_cases(self):
        """Test is_suspicious edge cases"""
        # Test with non-string input
        result = is_suspicious(123)
        assert result is False

        # Test with None
        result = is_suspicious(None)
        assert result is False

        # Test with empty string
        result = is_suspicious("")
        assert result is False

    def test_validate_order_id_basic(self):
        """Test order ID validation"""
        # Test with valid order ID (must be 10-50 chars)
        result = validate_order_id("order_12345")
        assert result == "order_12345"

        # Test with empty order ID
        with pytest.raises(CNOPOrderValidationException, match="Order ID cannot be empty"):
            validate_order_id("")

        # Test with whitespace-only order ID
        with pytest.raises(CNOPOrderValidationException, match="Order ID cannot be empty"):
            validate_order_id("   ")

        # Test with suspicious content
        with pytest.raises(CNOPOrderValidationException, match="Order ID contains potentially malicious content"):
            validate_order_id("<script>alert('xss')</script>")

        # Test with too short order ID
        with pytest.raises(CNOPOrderValidationException, match="Order ID must be 10-50 alphanumeric characters and underscores"):
            validate_order_id("order_123")

    def test_validate_username_basic(self):
        """Test username validation"""
        # Test with valid username
        result = validate_username("testuser123")
        assert result == "testuser123"  # Should be converted to lowercase

        # Test with empty username
        with pytest.raises(CNOPOrderValidationException, match="Username cannot be empty"):
            validate_username("")

        # Test with whitespace-only username
        with pytest.raises(CNOPOrderValidationException, match="Username cannot be empty"):
            validate_username("   ")

        # Test with suspicious content
        with pytest.raises(CNOPOrderValidationException, match="Username contains potentially malicious content"):
            validate_username("<script>alert('xss')</script>")

        # Test with invalid characters
        with pytest.raises(CNOPOrderValidationException, match="Username must be 3-30 alphanumeric characters and underscores"):
            validate_username("user-name")

    def test_validate_asset_id_basic(self):
        """Test asset ID validation"""
        # Test with valid asset ID
        result = validate_asset_id("BTC")
        assert result == "BTC"

        # Test with empty asset ID
        with pytest.raises(CNOPOrderValidationException, match="Asset ID cannot be empty"):
            validate_asset_id("")

        # Test with whitespace-only asset ID
        with pytest.raises(CNOPOrderValidationException, match="Asset ID cannot be empty"):
            validate_asset_id("   ")

        # Test with suspicious content
        with pytest.raises(CNOPOrderValidationException, match="Asset ID contains potentially malicious content"):
            validate_asset_id("<script>alert('xss')</script>")

        # Test with invalid format
        with pytest.raises(CNOPOrderValidationException, match="Asset ID must be 1-10 alphanumeric characters"):
            validate_asset_id("a" * 11)

    def test_validate_quantity_basic(self):
        """Test quantity validation"""
        # Test with valid quantity
        result = validate_quantity(Decimal("1.0"))
        assert result == Decimal("1.0")

        # Test with zero quantity
        with pytest.raises(CNOPOrderValidationException, match="Quantity must be greater than zero"):
            validate_quantity(Decimal("0.0"))

        # Test with negative quantity
        with pytest.raises(CNOPOrderValidationException, match="Quantity must be greater than zero"):
            validate_quantity(Decimal("-1.0"))

        # Test with very small quantity
        with pytest.raises(CNOPOrderValidationException, match="Order quantity below minimum threshold"):
            validate_quantity(Decimal("0.0001"))

        # Test with very large quantity
        with pytest.raises(CNOPOrderValidationException, match="Order quantity exceeds maximum threshold"):
            validate_quantity(Decimal("2000000.0"))

    def test_validate_quantity_non_decimal_input(self):
        """Test validate_quantity with non-Decimal input"""
        # Test with string input (should convert to Decimal)
        result = validate_quantity("1.5")
        assert result == Decimal("1.5")

        # Test with integer input (should convert to Decimal)
        result = validate_quantity(2)
        assert result == Decimal("2")

    def test_validate_quantity_invalid_conversion(self):
        """Test validate_quantity with invalid input that fails conversion"""
        # Test with a complex object that can't be converted to string (raises TypeError)
        class UnconvertibleObject:
            def __str__(self):
                raise TypeError("Cannot convert to string")

        with pytest.raises(CNOPOrderValidationException, match="Quantity must be a valid number"):
            validate_quantity(UnconvertibleObject())

        # Test with an object that raises ValueError when converted to string
        class ValueErrorObject:
            def __str__(self):
                raise ValueError("Cannot convert to string")

        with pytest.raises(CNOPOrderValidationException, match="Quantity must be a valid number"):
            validate_quantity(ValueErrorObject())

    def test_validate_price_non_decimal_input(self):
        """Test validate_price with non-Decimal input"""
        # Test with string input (should convert to Decimal)
        result = validate_price("100.50")
        assert result == Decimal("100.50")

        # Test with integer input (should convert to Decimal)
        result = validate_price(200)
        assert result == Decimal("200")

    def test_validate_price_invalid_conversion(self):
        """Test validate_price with invalid input that fails conversion"""
        # Test with a complex object that can't be converted to string (raises TypeError)
        class UnconvertibleObject:
            def __str__(self):
                raise TypeError("Cannot convert to string")

        with pytest.raises(CNOPOrderValidationException, match="Price must be a valid number"):
            validate_price(UnconvertibleObject())

        # Test with an object that raises ValueError when converted to string
        class ValueErrorObject:
            def __str__(self):
                raise ValueError("Cannot convert to string")

        with pytest.raises(CNOPOrderValidationException, match="Price must be a valid number"):
            validate_price(ValueErrorObject())

    def test_validate_price_basic(self):
        """Test price validation"""
        # Test with valid price
        result = validate_price(Decimal("100.00"))
        assert result == Decimal("100.00")

        # Test with zero price
        with pytest.raises(CNOPOrderValidationException, match="Price must be greater than zero"):
            validate_price(Decimal("0.0"))

        # Test with negative price
        with pytest.raises(CNOPOrderValidationException, match="Price must be greater than zero"):
            validate_price(Decimal("-100.00"))

        # Test with very small price (no minimum threshold for price)
        result = validate_price(Decimal("0.01"))
        assert result == Decimal("0.01")

        # Test with very large price
        with pytest.raises(CNOPOrderValidationException, match="Price exceeds maximum threshold"):
            validate_price(Decimal("2000000.00"))

    def test_validate_order_type_basic(self):
        """Test order type validation"""
        # Test with valid order type
        result = validate_order_type(OrderType.LIMIT_BUY)
        assert result == OrderType.LIMIT_BUY

        # Test with invalid order type
        with pytest.raises(CNOPOrderValidationException, match="Invalid order type"):
            validate_order_type("INVALID_TYPE")

        # Test with None order type
        with pytest.raises(CNOPOrderValidationException, match="Order type cannot be empty"):
            validate_order_type(None)

    def test_validate_order_type_suspicious_content(self):
        """Test validate_order_type with suspicious content"""
        # Test with script tag (should be detected as suspicious)
        with pytest.raises(CNOPOrderValidationException, match="Order type contains potentially malicious content"):
            validate_order_type("<script>alert('xss')</script>market_buy")

        # Test with javascript protocol (should be detected as suspicious)
        with pytest.raises(CNOPOrderValidationException, match="Order type contains potentially malicious content"):
            validate_order_type("javascript:alert('xss')")

        # Test with data protocol (should be detected as suspicious)
        with pytest.raises(CNOPOrderValidationException, match="Order type contains potentially malicious content"):
            validate_order_type("data:text/html,<script>alert('xss')</script>")

    def test_validate_order_type_empty_after_sanitization(self):
        """Test validate_order_type with input that becomes empty after sanitization"""
        # Test with only HTML tags (should become empty after sanitization)
        with pytest.raises(CNOPOrderValidationException, match="Order type cannot be empty"):
            validate_order_type("<div></div>")

        # Test with only whitespace (should become empty after sanitization)
        with pytest.raises(CNOPOrderValidationException, match="Order type cannot be empty"):
            validate_order_type("   ")

        # Test with only HTML tags and whitespace
        with pytest.raises(CNOPOrderValidationException, match="Order type cannot be empty"):
            validate_order_type("  <span></span>  ")

    def test_validate_order_status_basic(self):
        """Test order status validation"""
        # Test with valid order status
        result = validate_order_status(OrderStatus.PENDING)
        assert result == OrderStatus.PENDING

        # Test with invalid order status
        with pytest.raises(CNOPOrderValidationException, match="Invalid order status"):
            validate_order_status("INVALID_STATUS")

        # Test with None order status
        with pytest.raises(CNOPOrderValidationException, match="Order status cannot be empty"):
            validate_order_status(None)

    def test_validate_order_status_suspicious_content(self):
        """Test validate_order_status with suspicious content"""
        # Test with script tag (should be detected as suspicious)
        with pytest.raises(CNOPOrderValidationException, match="Order status contains potentially malicious content"):
            validate_order_status("<script>alert('xss')</script>pending")

        # Test with javascript protocol (should be detected as suspicious)
        with pytest.raises(CNOPOrderValidationException, match="Order status contains potentially malicious content"):
            validate_order_status("javascript:alert('xss')")

        # Test with data protocol (should be detected as suspicious)
        with pytest.raises(CNOPOrderValidationException, match="Order status contains potentially malicious content"):
            validate_order_status("data:text/html,<script>alert('xss')</script>")

    def test_validate_order_status_empty_after_sanitization(self):
        """Test validate_order_status with input that becomes empty after sanitization"""
        # Test with only HTML tags (should become empty after sanitization)
        with pytest.raises(CNOPOrderValidationException, match="Order status cannot be empty"):
            validate_order_status("<div></div>")

        # Test with only whitespace (should become empty after sanitization)
        with pytest.raises(CNOPOrderValidationException, match="Order status cannot be empty"):
            validate_order_status("   ")

        # Test with only HTML tags and whitespace
        with pytest.raises(CNOPOrderValidationException, match="Order status cannot be empty"):
            validate_order_status("  <span></span>  ")

    def test_validate_expires_at_basic(self):
        """Test expiration time validation"""
        # Test with valid future date
        future_date = datetime.now() + timedelta(days=1)
        result = validate_expires_at(future_date)
        assert result == future_date

        # Test with past date
        past_date = datetime.now() - timedelta(days=1)
        with pytest.raises(CNOPOrderValidationException, match="Expiration time must be in the future"):
            validate_expires_at(past_date)

        # Test with current date
        current_date = datetime.now()
        with pytest.raises(CNOPOrderValidationException, match="Expiration time must be in the future"):
            validate_expires_at(current_date)

        # Test with None date (should not be allowed)
        with pytest.raises(CNOPOrderValidationException, match="Expiration time must be a valid datetime"):
            validate_expires_at(None)

    def test_validate_expires_at_too_far_future(self):
        """Test validate_expires_at with date too far in the future"""
        # Test with date more than 1 year in the future
        too_far_future = datetime.now() + timedelta(days=400)  # More than 1 year
        with pytest.raises(CNOPOrderValidationException, match="Expiration time cannot be more than 1 year in the future"):
            validate_expires_at(too_far_future)

        # Test with date exactly 1 year + 1 day in the future
        one_year_one_day = datetime.now() + timedelta(days=366)  # 1 year + 1 day
        with pytest.raises(CNOPOrderValidationException, match="Expiration time cannot be more than 1 year in the future"):
            validate_expires_at(one_year_one_day)

    def test_validate_limit_basic(self):
        """Test limit validation"""
        # Test with valid limit
        result = validate_limit(10)
        assert result == 10

        # Test with zero limit
        with pytest.raises(CNOPOrderValidationException, match="Limit must be at least 1"):
            validate_limit(0)

        # Test with negative limit
        with pytest.raises(CNOPOrderValidationException, match="Limit must be at least 1"):
            validate_limit(-10)

        # Test with very large limit
        with pytest.raises(CNOPOrderValidationException, match="Limit cannot exceed 1000"):
            validate_limit(1001)

    def test_validate_limit_non_integer_input(self):
        """Test validate_limit with non-integer input"""
        # Test with string input (should convert to int)
        result = validate_limit("50")
        assert result == 50

        # Test with float input (should convert to int)
        result = validate_limit(25.0)
        assert result == 25

    def test_validate_limit_invalid_conversion(self):
        """Test validate_limit with invalid input that fails conversion"""
        # Test with a complex object that can't be converted to int (raises TypeError)
        class UnconvertibleObject:
            def __int__(self):
                raise TypeError("Cannot convert to int")

        with pytest.raises(CNOPOrderValidationException, match="Limit must be a valid integer"):
            validate_limit(UnconvertibleObject())

        # Test with an object that raises ValueError when converted to int
        class ValueErrorObject:
            def __int__(self):
                raise ValueError("Cannot convert to int")

        with pytest.raises(CNOPOrderValidationException, match="Limit must be a valid integer"):
            validate_limit(ValueErrorObject())

    def test_validate_offset_basic(self):
        """Test offset validation"""
        # Test with valid offset
        result = validate_offset(10)
        assert result == 10

        # Test with zero offset
        result = validate_offset(0)
        assert result == 0

        # Test with negative offset
        with pytest.raises(CNOPOrderValidationException, match="Offset cannot be negative"):
            validate_offset(-10)

        # Test with None offset (should not be allowed)
        with pytest.raises(CNOPOrderValidationException, match="Offset must be a valid integer"):
            validate_offset(None)

    def test_validate_offset_maximum_value(self):
        """Test validate_offset with maximum value exceeded"""
        # Test with offset exactly at the limit (should pass)
        result = validate_offset(100000)
        assert result == 100000

        # Test with offset exceeding the limit (should fail)
        with pytest.raises(CNOPOrderValidationException, match="Offset cannot exceed 100,000"):
            validate_offset(100001)

        # Test with offset well above the limit
        with pytest.raises(CNOPOrderValidationException, match="Offset cannot exceed 100,000"):
            validate_offset(200000)
