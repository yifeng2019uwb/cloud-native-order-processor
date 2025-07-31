"""
Inventory service exceptions package
Path: services/inventory_service/src/exceptions/__init__.py
"""

# Import shared exceptions (mapped to external error codes)
from common.exceptions import (
    # Authentication (401)
    InvalidCredentialsException,
    TokenExpiredException,
    TokenInvalidException,

    # Resources (404)
    AssetNotFoundException,

    # Validation (422)
    AssetValidationException,

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

# Import inventory service specific exceptions
from .exceptions import (
    AssetAlreadyExistsException,
    AssetCreationException,
    InventoryServerException,
)

__all__ = [
    # Shared exceptions (mapped to external error codes)
    "InvalidCredentialsException",
    "TokenExpiredException",
    "TokenInvalidException",
    "AssetNotFoundException",
    "AssetValidationException",
    "InternalServerException",

    # Common exceptions (handled internally, NOT mapped)
    "DatabaseOperationException",
    "ConfigurationException",
    "ExternalServiceException",
    "AWSServiceException",

    # Inventory service specific exceptions
    "AssetAlreadyExistsException",
    "AssetCreationException",
    "InventoryServerException",
]