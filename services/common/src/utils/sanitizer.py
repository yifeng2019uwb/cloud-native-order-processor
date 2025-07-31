"""
Simple Input Sanitization

Basic sanitization utilities for common security concerns.
"""

import re
import html
from typing import Optional


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Simple string sanitization

    Args:
        value: Input string
        max_length: Maximum allowed length

    Returns:
        Sanitized string
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


def sanitize_username(value: str) -> str:
    """
    Simple username sanitization

    Args:
        value: Username input

    Returns:
        Sanitized username
    """
    if not value:
        raise ValueError("Username cannot be empty")

    # Remove HTML tags first
    value = re.sub(r'<[^>]+>', '', value)

    # Remove special characters
    value = re.sub(r'[<>"\']', '', value)

    # Only allow alphanumeric, underscores, hyphens
    value = re.sub(r'[^a-zA-Z0-9_-]', '', value)

    # Convert to lowercase
    value = value.lower().strip()

    # Length validation
    if len(value) < 3:
        raise ValueError("Username must be at least 3 characters")
    if len(value) > 30:
        raise ValueError("Username must be no more than 30 characters")

    return value


def sanitize_email(value: str) -> str:
    """
    Simple email sanitization

    Args:
        value: Email input

    Returns:
        Sanitized email
    """
    if not value:
        raise ValueError("Email cannot be empty")

    # Remove HTML tags first
    value = re.sub(r'<[^>]+>', '', value)

    # Convert to lowercase
    value = value.lower().strip()

    # Basic email validation after sanitization
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, value):
        raise ValueError("Invalid email format")

    return value


def sanitize_phone(value: str) -> str:
    """
    Simple phone sanitization

    Args:
        value: Phone input

    Returns:
        Sanitized phone (digits only)
    """
    if not value:
        return ""

    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', value)

    # Validate length
    if len(digits_only) < 10:
        raise ValueError("Phone number must contain at least 10 digits")
    if len(digits_only) > 15:
        raise ValueError("Phone number must contain no more than 15 digits")

    return digits_only


def is_suspicious(value: str) -> bool:
    """
    Simple suspicious input detection

    Args:
        value: Input string

    Returns:
        True if suspicious patterns detected
    """
    if not isinstance(value, str):
        return False

    # Check for common attack patterns
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'vbscript:',
        r'data:',
        r'<iframe',
        r'<object',
        r'<embed',
        r'<form',
        r'<input',
        r'<textarea',
        r'<select',
        r'<button',
        r'<link',
        r'<meta',
        r'<style',
        r'<base',
        r'<bgsound',
        r'<xmp',
        r'<plaintext',
        r'<listing',
        r'<marquee',
        r'<applet',
        r'<isindex',
        r'<dir',
        r'<menu',
        r'<nobr',
        r'<noembed',
        r'<noframes',
        r'<noscript',
        r'<wbr',
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            return True

    return False