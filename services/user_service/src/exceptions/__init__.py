"""
User service exceptions package
Path: services/user_service/src/exceptions/__init__.py
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
    UserRegistrationException,
    UserServerException,
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
    "UserRegistrationException",
    "UserServerException",
]