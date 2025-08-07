"""
Order service exceptions package
Path: services/order_service/src/exceptions/__init__.py
"""

# Import shared exceptions (mapped to external error codes)
from common.exceptions import (
    # Authentication (401)
    InvalidCredentialsException,
    TokenExpiredException,
    TokenInvalidException,

    # Resources (404)
    OrderNotFoundException,
    UserNotFoundException,
    AssetNotFoundException,

    # Validation (422)
    OrderValidationException,
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
    AWSServiceException,
)

# Import order service specific exceptions
from .exceptions import (
    OrderAlreadyExistsException,
    OrderStatusException,
    OrderServerException,
)

__all__ = [
    # Shared exceptions (mapped to external error codes)
    "InvalidCredentialsException",
    "TokenExpiredException",
    "TokenInvalidException",
    "OrderNotFoundException",
    "UserNotFoundException",
    "AssetNotFoundException",
    "OrderValidationException",
    "UserValidationException",
    "InternalServerException",

    # Common exceptions (handled internally, NOT mapped)
    "DatabaseOperationException",
    "ConfigurationException",
    "ExternalServiceException",
    "AWSServiceException",

    # Order service specific exceptions
    "OrderAlreadyExistsException",
    "OrderStatusException",
    "OrderServerException",
]
