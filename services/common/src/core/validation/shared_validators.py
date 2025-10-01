"""
Shared Validation Functions

Provides common validation utilities used across all microservices.
These functions are standardized and should be imported by individual services
to ensure consistency and reduce code duplication.
"""

import re
from typing import Optional


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Basic string sanitization - removes HTML tags, trims whitespace

    Args:
        value: String to sanitize
        max_length: Optional maximum length to truncate to

    Returns:
        Sanitized string with HTML tags removed and whitespace trimmed
    """
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
    """
    Check for potentially malicious content

    Args:
        value: String to check for suspicious patterns

    Returns:
        True if suspicious content is detected, False otherwise
    """
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


def validate_username(value: str) -> str:
    """
    Standardized username validation across all services

    Args:
        value: Username to validate

    Returns:
        Validated and normalized username (lowercase)

    Raises:
        ValueError: If username is invalid
    """
    if not value:
        raise ValueError("Username cannot be empty")

    # 1. Basic sanitization first (remove HTML tags, trim whitespace)
    value = sanitize_string(value)

    # 2. Check for empty after sanitization
    if not value:
        raise ValueError("Username cannot be empty")

    # 3. Check for suspicious content after sanitization
    if is_suspicious(value):
        raise ValueError("Username contains potentially malicious content")

    # 4. Format validation - alphanumeric and underscores only, 6-30 chars
    if not re.match(r'^[a-zA-Z0-9_]{6,30}$', value):
        raise ValueError("Username must be 6-30 alphanumeric characters and underscores only")

    # 5. Convert to lowercase for consistency
    return value.lower()
