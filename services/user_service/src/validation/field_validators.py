"""
User Service Field Validators

Provides field-specific validation logic for the user service.
Only validates API request fields for registration and login.
Combines sanitization + format validation in each function.
"""

import re
from datetime import date, timedelta
from decimal import Decimal
from user_exceptions import CNOPUserValidationException

# Import shared validation functions from common module
from common.core.validation.shared_validators import (
    sanitize_string,
    is_suspicious,
    validate_username as shared_validate_username
)


def validate_username(v: str) -> str:
    """
    User service: username validation (used as ID)
    Uses shared validation logic with service-specific exception handling
    """
    try:
        return shared_validate_username(v)
    except ValueError as e:
        # Convert ValueError to service-specific exception
        raise CNOPUserValidationException(str(e))


def validate_name(v: str) -> str:
    """
    User service: name validation (first_name, last_name)
    Combines sanitization + format validation
    """
    if not v:
        raise CNOPUserValidationException("Name cannot be empty")

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise CNOPUserValidationException("Name contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise CNOPUserValidationException("Name cannot be empty")

    # 4. Format validation - letters, spaces, apostrophes, and hyphens only
    if not re.match(r'^[a-zA-Z\s\'-]+$', v):
        raise CNOPUserValidationException("Name must contain only letters, spaces, apostrophes, and hyphens")

    # 5. Convert to title case
    return v.title()


def validate_email(v: str) -> str:
    """
    User service: email validation
    Combines sanitization + format validation
    """
    if not v:
        raise CNOPUserValidationException("Email cannot be empty")

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise CNOPUserValidationException("Email contains potentially malicious content")

    # 2. Format validation - check email pattern before sanitization
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
        raise CNOPUserValidationException("Invalid email format")

    # 3. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 4. Check for empty after sanitization
    if not v:
        raise CNOPUserValidationException("Email cannot be empty")

    # 5. Convert to lowercase
    return v.lower()


def validate_phone(v: str) -> str:
    """
    User service: phone validation
    Combines sanitization + format validation
    """
    if not v:
        return ""  # Phone is optional

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise CNOPUserValidationException("Phone contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        return ""

    # 4. Extract digits only
    digits_only = re.sub(r'\D', '', v)

    # 5. Format validation - 10-15 digits
    if not re.match(r'^[0-9]{10,15}$', digits_only):
        raise CNOPUserValidationException("Phone number must contain 10-15 digits")

    return digits_only


def validate_password(v: str) -> str:
    """
    User service: password validation
    Combines sanitization + format validation
    """
    if not v:
        raise CNOPUserValidationException("Password cannot be empty")

    # 1. Check for suspicious content first
    if is_suspicious(v):
        raise CNOPUserValidationException("Password contains potentially malicious content")

    # 2. Basic sanitization (remove HTML tags, trim whitespace)
    v = sanitize_string(v)

    # 3. Check for empty after sanitization
    if not v:
        raise CNOPUserValidationException("Password cannot be empty")

    # 4. Length validation
    if len(v) < 12:
        raise CNOPUserValidationException("Password must be at least 12 characters long")
    if len(v) > 20:
        raise CNOPUserValidationException("Password must be no more than 20 characters long")

    # 5. Complexity validation
    if not re.search(r"[A-Z]", v):
        raise CNOPUserValidationException("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", v):
        raise CNOPUserValidationException("Password must contain at least one lowercase letter")

    if not re.search(r"\d", v):
        raise CNOPUserValidationException("Password must contain at least one number")

    if not re.search(r"[!@#$%^&*()\-_=+]", v):
        raise CNOPUserValidationException("Password must contain at least one special character (!@#$%^&*()-_=+)")

    return v


def validate_date_of_birth(v: date) -> date:
    """
    User service: date of birth validation
    """
    if not v:
        return v  # Date of birth is optional

    today = date.today()
    age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))

    # Check minimum age (13 years for COPPA compliance)
    if age < 13:
        raise CNOPUserValidationException("User must be at least 13 years old")

    # Check maximum reasonable age (120 years)
    if age > 120:
        raise CNOPUserValidationException("Invalid date of birth")

    return v


def validate_amount(v: Decimal) -> Decimal:
    """
    User service: amount validation for balance operations
    """
    if not v:
        raise CNOPUserValidationException("Amount cannot be empty")

    # Check for positive amount
    if v <= 0:
        raise CNOPUserValidationException("Amount must be greater than 0")

    # Check for reasonable maximum amount (1 million)
    if v > 1000000:
        raise CNOPUserValidationException("Amount cannot exceed 1,000,000")

    # Check for reasonable precision (2 decimal places)
    if v.as_tuple().exponent < -2:
        raise CNOPUserValidationException("Amount cannot have more than 2 decimal places")

    return v
