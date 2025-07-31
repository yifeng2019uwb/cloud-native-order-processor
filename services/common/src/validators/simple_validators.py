"""
Simple Pydantic Validators with Sanitization

Basic validators that incorporate simple sanitization.
"""

from pydantic import field_validator
from ..utils.sanitizer import sanitize_string, sanitize_username, sanitize_email, sanitize_phone, is_suspicious


def sanitized_string(max_length: int = None):
    """Simple string validator with sanitization"""
    def validator(v):
        if is_suspicious(v):
            raise ValueError("Input contains potentially malicious content")
        return sanitize_string(v, max_length)
    return validator


def sanitized_username():
    """Username validator with sanitization"""
    def validator(v):
        if is_suspicious(v):
            raise ValueError("Username contains potentially malicious content")
        return sanitize_username(v)
    return validator


def sanitized_email():
    """Email validator with sanitization"""
    def validator(v):
        if is_suspicious(v):
            raise ValueError("Email contains potentially malicious content")
        return sanitize_email(v)
    return validator


def sanitized_phone():
    """Phone validator with sanitization"""
    def validator(v):
        if not v:  # Allow empty/None
            return ""
        if is_suspicious(v):
            raise ValueError("Phone contains potentially malicious content")
        return sanitize_phone(v)
    return validator