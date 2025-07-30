"""
Simple role definitions for the Order Processor system.
"""

from enum import Enum


class UserRole(str, Enum):
    """User roles - simple and focused."""

    CUSTOMER = "customer"  # Basic authenticated users
    ADMIN = "admin"        # System administrators


# Simple constants for backward compatibility
DEFAULT_USER_ROLE = UserRole.CUSTOMER.value
VALID_ROLES = [role.value for role in UserRole]