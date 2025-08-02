"""
User service exceptions package

TECH DEBT: This module was renamed from 'exceptions' to 'user_exceptions' to avoid
naming conflicts with the common package's 'exceptions' module. Python's module
resolution was finding the common package's exceptions module first, causing import
errors.

TODO: Consider a better long-term solution such as:
1. Restructuring the common package to avoid the naming conflict
2. Using namespace packages
3. Implementing a more robust module resolution strategy

Current path: services/user_service/src/user_exceptions/__init__.py
"""

# Import shared exceptions (mapped to external error codes)
from common.exceptions import (
    # Authentication (401)
    InvalidCredentialsException,
    TokenExpiredException,
    TokenInvalidException,

    # Resources (404)
    UserNotFoundException,

    # Validation (422)
    UserValidationException,

    # Internal Server (500) - general use by services
    InternalServerException,
)

# Import common exceptions (handled internally, NOT mapped)
from common.exceptions import (
    # Database (500) - handled internally
    DatabaseOperationException,
    ConfigurationException,
    ExternalServiceException,
)

# Import user service specific exceptions
from .exceptions import (
    UserAlreadyExistsException,
)

__all__ = [
    # Shared exceptions (mapped to external error codes)
    "InvalidCredentialsException",
    "TokenExpiredException",
    "TokenInvalidException",
    "UserNotFoundException",
    "UserValidationException",
    "InternalServerException",

    # Common exceptions (handled internally, NOT mapped)
    "DatabaseOperationException",
    "ConfigurationException",
    "ExternalServiceException",

    # User service specific exceptions
    "UserAlreadyExistsException",
]