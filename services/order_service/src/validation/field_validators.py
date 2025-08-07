"""
Order Service Field Validators

Provides field-specific validation logic for the order service.
Combines sanitization + format validation in each function.
"""

import re
from decimal import Decimal
from datetime import datetime

# Import proper exceptions
from common.exceptions.shared_exceptions import OrderValidationException


def sanitize_string(value: str, max_length: int = None) -> str:
    """Basic string sanitization - removes HTML tags, trims whitespace"""
    if not isinstance(value, str):
        return str(value)

    # Remove HTML tags first
    value = re.sub(r'<[^>]+>', '', value)

    # Trim whitespace
    value = value.strip()

    # Length limit
    if max_length and len(value) > max_length:
        value = value[:max_length]

    return value


def is_suspicious(value: str) -> bool:
    """Check for potentially malicious content"""
    if not isinstance(value, str):
        return False

    # Check for common attack patterns
    suspicious_patterns = [
        r'<script', r'javascript:', r'vbscript:', r'data:', r'<iframe',
        r'<object', r'<embed', r'<form', r'<input', r'<textarea',
        r'<select', r'<button', r'<link', r'<meta', r'<style',
        r'<base', r'<bgsound', r'<xmp', r'<plaintext', r'<listing',
        r'<marquee', r'<applet', r'<isindex', r'<dir', r'<menu',
        r'<nobr', r'<noembed', r'<noframes', r'<noscript', r'<wbr',
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            return True

    return False


def validate_order_id(v: str) -> str:
    """
    Order service: order_id validation (primary identifier)
    Combines sanitization + format validation
    """
    if not v:
        raise OrderValidationException("Order ID cannot be empty")

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise OrderValidationException("Order ID contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise OrderValidationException("Order ID cannot be empty")

    # 4. Format validation - order IDs should be alphanumeric with underscores, 10-50 chars
    if not re.match(r'^[a-zA-Z0-9_]{10,50}$', v):
        raise OrderValidationException("Order ID must be 10-50 alphanumeric characters and underscores")

    return v


def validate_username(v: str) -> str:
    """
    Order service: username validation (references user service)
    Combines sanitization + format validation
    """
    if not v:
        raise OrderValidationException("Username cannot be empty")

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise OrderValidationException("Username contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise OrderValidationException("Username cannot be empty")

    # 4. Format validation - usernames should be alphanumeric with underscores, 3-30 chars
    if not re.match(r'^[a-zA-Z0-9_]{3,30}$', v):
        raise OrderValidationException("Username must be 3-30 alphanumeric characters and underscores")

    # 5. Convert to lowercase for consistency
    return v.lower()


def validate_asset_id(v: str) -> str:
    """
    Order service: asset_id validation (references inventory service)
    Combines sanitization + format validation
    """
    if not v:
        raise OrderValidationException("Asset ID cannot be empty")

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise OrderValidationException("Asset ID contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise OrderValidationException("Asset ID cannot be empty")

    # 4. Format validation - asset IDs should be alphanumeric, 1-10 chars
    if not re.match(r'^[a-zA-Z0-9]{1,10}$', v):
        raise OrderValidationException("Asset ID must be 1-10 alphanumeric characters")

    # 5. Convert to uppercase for consistency
    return v.upper()


def validate_order_type(v: str) -> str:
    """
    Order service: order type validation
    Combines sanitization + format validation
    """
    if not v:
        raise OrderValidationException("Order type cannot be empty")

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise OrderValidationException("Order type contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise OrderValidationException("Order type cannot be empty")

    # 4. Format validation - check against valid order types
    valid_types = ['market_buy', 'market_sell', 'limit_buy', 'limit_sell']
    if v.lower() not in valid_types:
        raise OrderValidationException(f"Invalid order type. Must be one of: {valid_types}")

    # 5. Convert to lowercase for consistency
    return v.lower()


def validate_order_status(v: str) -> str:
    """
    Order service: order status validation
    Combines sanitization + format validation
    """
    if not v:
        raise OrderValidationException("Order status cannot be empty")

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise OrderValidationException("Order status contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise OrderValidationException("Order status cannot be empty")

    # 4. Format validation - check against valid order statuses
    valid_statuses = ['pending', 'completed', 'cancelled', 'failed']
    if v.lower() not in valid_statuses:
        raise OrderValidationException(f"Invalid order status. Must be one of: {valid_statuses}")

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
            raise OrderValidationException("Quantity must be a valid number")

    if v <= 0:
        raise OrderValidationException("Quantity must be greater than zero")

    if v < Decimal("0.001"):
        raise OrderValidationException("Order quantity below minimum threshold (0.001)")

    # Check for reasonable maximum (prevent excessive orders)
    if v > Decimal("1000000"):
        raise OrderValidationException("Order quantity exceeds maximum threshold (1,000,000)")

    return v


def validate_price(v: Decimal) -> Decimal:
    """
    Order service: price validation
    """
    if not isinstance(v, Decimal):
        try:
            v = Decimal(str(v))
        except (ValueError, TypeError):
            raise OrderValidationException("Price must be a valid number")

    if v <= 0:
        raise OrderValidationException("Price must be greater than zero")

    # Check for reasonable maximum (prevent excessive prices)
    if v > Decimal("1000000"):
        raise OrderValidationException("Price exceeds maximum threshold (1,000,000)")

    return v


def validate_expires_at(v: datetime) -> datetime:
    """
    Order service: expiration time validation
    """
    if not isinstance(v, datetime):
        raise OrderValidationException("Expiration time must be a valid datetime")

    if v <= datetime.utcnow():
        raise OrderValidationException("Expiration time must be in the future")

    # Check if expiration is too far in the future (e.g., more than 1 year)
    max_expiry = datetime.utcnow().replace(year=datetime.utcnow().year + 1)
    if v > max_expiry:
        raise OrderValidationException("Expiration time cannot be more than 1 year in the future")

    return v


def validate_limit(v: int) -> int:
    """
    Order service: pagination limit validation
    """
    if not isinstance(v, int):
        try:
            v = int(v)
        except (ValueError, TypeError):
            raise OrderValidationException("Limit must be a valid integer")

    if v < 1:
        raise OrderValidationException("Limit must be at least 1")

    if v > 1000:
        raise OrderValidationException("Limit cannot exceed 1000")

    return v


def validate_offset(v: int) -> int:
    """
    Order service: pagination offset validation
    """
    if not isinstance(v, int):
        try:
            v = int(v)
        except (ValueError, TypeError):
            raise OrderValidationException("Offset must be a valid integer")

    if v < 0:
        raise OrderValidationException("Offset cannot be negative")

    if v > 100000:
        raise OrderValidationException("Offset cannot exceed 100,000")

    return v