"""
Inventory Service Field Validators

Only validates API request fields (GET endpoints only).
Combines sanitization + format validation in each function.
"""

import re

# Import proper exceptions
from common.exceptions.shared_exceptions import AssetValidationException


def sanitize_string(value: str, max_length: int = None) -> str:
    """Basic string sanitization - removes HTML tags, trim whitespace"""
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


def validate_asset_id(v: str) -> str:
    """
    Inventory service: asset_id validation (path parameter)
    Combines sanitization + format validation
    """
    if not v:
        raise AssetValidationException("Asset ID cannot be empty")

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise AssetValidationException("Asset ID contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise AssetValidationException("Asset ID cannot be empty")

    # 4. Format validation - asset IDs should be alphanumeric, 1-10 chars
    if not re.match(r'^[a-zA-Z0-9]{1,10}$', v):
        raise AssetValidationException("Asset ID must be 1-10 alphanumeric characters")

    # 5. Convert to uppercase for consistency
    return v.upper()