"""
Order Service Field Validators

Provides field-specific validation logic for the order service.
Combines sanitization + format validation in each function.
"""

import re
from decimal import Decimal
from datetime import datetime, timezone

# Import proper exceptions
from order_exceptions.exceptions import CNOPOrderValidationException

# Local constants for validation messages (only used in this file)
MSG_ERROR_ORDER_ID_EMPTY = "Order ID cannot be empty"
MSG_ERROR_ORDER_TYPE_EMPTY = "Order type cannot be empty"
MSG_ERROR_ORDER_STATUS_EMPTY = "Order status cannot be empty"
MSG_ERROR_INVALID_ORDER_TYPE = "Invalid order type"
MSG_ERROR_INVALID_ORDER_STATUS = "Invalid order status"
from common.data.entities.order.enums import OrderType, OrderStatus

# Import shared validation functions from common module
from common.core.validation.shared_validators import (
    sanitize_string,
    is_suspicious,
    validate_username as shared_validate_username
)


# sanitize_string and is_suspicious are now imported from common module


def validate_order_id(v: str) -> str:
    """
    Order service: order_id validation (primary identifier)
    Combines sanitization + format validation
    """
    if not v:
        raise CNOPOrderValidationException(MSG_ERROR_ORDER_ID_EMPTY)

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise CNOPOrderValidationException("Order ID contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise CNOPOrderValidationException(MSG_ERROR_ORDER_ID_EMPTY)

    # 4. Format validation - order IDs should be alphanumeric with underscores, 10-50 chars
    if not re.match(r'^[a-zA-Z0-9_]{10,50}$', v):
        raise CNOPOrderValidationException("Order ID must be 10-50 alphanumeric characters and underscores")

    return v


def validate_username(v: str) -> str:
    """
    Order service: username validation (references user service)
    Uses shared validation logic with service-specific exception handling
    """
    try:
        return shared_validate_username(v)
    except ValueError as e:
        # Convert ValueError to service-specific exception
        raise CNOPOrderValidationException(str(e))


def validate_asset_id(v: str) -> str:
    """
    Order service: asset_id validation (references inventory service)
    Combines sanitization + format validation
    """
    if not v:
        raise CNOPOrderValidationException("Asset ID cannot be empty")

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise CNOPOrderValidationException("Asset ID contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise CNOPOrderValidationException("Asset ID cannot be empty")

    # 4. Format validation - asset IDs should be alphanumeric, 1-10 chars
    if not re.match(r'^[a-zA-Z0-9]{1,10}$', v):
        raise CNOPOrderValidationException("Asset ID must be 1-10 alphanumeric characters")

    # 5. Convert to uppercase for consistency
    return v.upper()


def validate_order_type(v: str) -> str:
    """
    Order service: order type validation
    Combines sanitization + format validation
    """
    if not v:
        raise CNOPOrderValidationException(MSG_ERROR_ORDER_TYPE_EMPTY)

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise CNOPOrderValidationException("Order type contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise CNOPOrderValidationException(MSG_ERROR_ORDER_TYPE_EMPTY)

    # 4. Format validation - check against valid order types
    valid_types = [order_type.value for order_type in OrderType]
    if v.lower() not in valid_types:
        raise CNOPOrderValidationException(f"{MSG_ERROR_INVALID_ORDER_TYPE}. Must be one of: {valid_types}")

    # 5. Convert to lowercase for consistency
    return v.lower()


def validate_order_status(v: str) -> str:
    """
    Order service: order status validation
    Combines sanitization + format validation
    """
    if not v:
        raise CNOPOrderValidationException(MSG_ERROR_ORDER_STATUS_EMPTY)

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise CNOPOrderValidationException("Order status contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise CNOPOrderValidationException(MSG_ERROR_ORDER_STATUS_EMPTY)

    # 4. Format validation - check against valid order statuses
    valid_statuses = [status.value for status in OrderStatus]
    if v.lower() not in valid_statuses:
        raise CNOPOrderValidationException(f"{MSG_ERROR_INVALID_ORDER_STATUS}. Must be one of: {valid_statuses}")

    # 5. Convert to lowercase for consistency
    return v.lower()


def validate_quantity(v: Decimal) -> Decimal:
    """
    Order service: quantity validation
    """
    if not isinstance(v, Decimal):
        try:
            v = Decimal(str(v))
        except (ValueError, TypeError):
            raise  CNOPOrderValidationException("Quantity must be a valid number")

    if v <= 0:
        raise CNOPOrderValidationException("Quantity must be greater than zero")

    if v < Decimal("0.001"):
        raise CNOPOrderValidationException("Order quantity below minimum threshold (0.001)")

    # Check for reasonable maximum (prevent excessive orders)
    if v > Decimal("1000000"):
        raise CNOPOrderValidationException("Order quantity exceeds maximum threshold (1,000,000)")

    return v


def validate_price(v: Decimal) -> Decimal:
    """
    Order service: price validation
    """
    if not isinstance(v, Decimal):
        try:
            v = Decimal(str(v))
        except (ValueError, TypeError):
            raise CNOPOrderValidationException("Price must be a valid number")

    if v <= 0:
        raise CNOPOrderValidationException("Price must be greater than zero")

    # Check for reasonable maximum (prevent excessive prices)
    if v > Decimal("1000000"):
        raise CNOPOrderValidationException("Price exceeds maximum threshold (1,000,000)")

    return v


def validate_expires_at(v: datetime) -> datetime:
    """
    Order service: expiration time validation
    """
    if not isinstance(v, datetime):
        raise CNOPOrderValidationException("Expiration time must be a valid datetime")

    current_time = datetime.now(timezone.utc)

    # Handle both naive and timezone-aware datetimes
    if v.tzinfo is None:
        # If input is naive, assume it's UTC and compare with naive current time
        current_time_naive = current_time.replace(tzinfo=None)
        if v <= current_time_naive:
            raise CNOPOrderValidationException("Expiration time must be in the future")

        # Check if expiration is too far in the future (e.g., more than 1 year)
        max_expiry = current_time_naive.replace(year=current_time_naive.year + 1)
        if v > max_expiry:
            raise CNOPOrderValidationException("Expiration time cannot be more than 1 year in the future")
    else:
        # If input is timezone-aware, compare with timezone-aware current time
        if v <= current_time:
            raise CNOPOrderValidationException("Expiration time must be in the future")

        # Check if expiration is too far in the future (e.g., more than 1 year)
        max_expiry = current_time.replace(year=current_time.year + 1)
        if v > max_expiry:
            raise CNOPOrderValidationException("Expiration time cannot be more than 1 year in the future")

    return v


def validate_limit(v: int) -> int:
    """
    Order service: pagination limit validation
    """
    if not isinstance(v, int):
        try:
            v = int(v)
        except (ValueError, TypeError):
            raise CNOPOrderValidationException("Limit must be a valid integer")

    if v < 1:
        raise CNOPOrderValidationException("Limit must be at least 1")

    if v > 1000:
        raise CNOPOrderValidationException("Limit cannot exceed 1000")

    return v


def validate_offset(v: int) -> int:
    """
    Order service: pagination offset validation
    """
    if not isinstance(v, int):
        try:
            v = int(v)
        except (ValueError, TypeError):
            raise CNOPOrderValidationException("Offset must be a valid integer")

    if v < 0:
        raise CNOPOrderValidationException("Offset cannot be negative")

    if v > 100000:
        raise CNOPOrderValidationException("Offset cannot exceed 100,000")

    return v