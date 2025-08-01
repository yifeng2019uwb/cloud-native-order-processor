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


def validate_user_id(v: str) -> str:
    """
    Order service: user_id validation (references user service)

    Args:
        v: User ID to validate

    Returns:
        Validated user ID

    Raises:
        ValueError: If user ID doesn't meet requirements
    """
    # TODO: Implement user ID validation
    # - Could be UUID, numeric ID, etc.
    # - Validate format based on user service requirements
    pass


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

    Args:
        v: Order type to validate

    Returns:
        Validated order type (uppercase)

    Raises:
        ValueError: If order type doesn't meet requirements
    """
    # TODO: Implement order type validation
    # - Check against valid types: ['BUY', 'SELL']
    # - Convert to uppercase
    # - Return validated type
    pass


def validate_order_status(v: str) -> str:
    """
    Order service: order status validation

    Args:
        v: Order status to validate

    Returns:
        Validated order status (uppercase)

    Raises:
        ValueError: If order status doesn't meet requirements
    """
    # TODO: Implement order status validation
    # - Check against valid statuses: ['PENDING', 'COMPLETED', 'CANCELLED', 'FAILED']
    # - Convert to uppercase
    # - Return validated status
    pass


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

    return v


def validate_expires_at(v: datetime) -> datetime:
    """
    Order service: expiration time validation
    """
    if not isinstance(v, datetime):
        raise OrderValidationException("Expiration time must be a valid datetime")

    if v <= datetime.utcnow():
        raise OrderValidationException("Expiration time must be in the future")

    return v