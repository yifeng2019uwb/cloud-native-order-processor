"""
Inventory service exceptions package
Path: services/inventory_service/src/exceptions/__init__.py

This package contains inventory service-specific exceptions for business logic validation.
These exceptions are exposed to clients via the gateway and mapped to appropriate HTTP status codes.

NOTE: Old exception imports are commented out but kept for reference in case they're still needed
for service-level or integration tests. They can be uncommented if needed.
"""

# Import shared exceptions (mapped to external error codes) - COMMENTED OUT BUT KEPT FOR REFERENCE
# from common.exceptions import (
#     # Authentication (401)
#     InvalidCredentialsException,
#     TokenExpiredException,
#     TokenInvalidException,
#
#     # Resources (404)
#     AssetNotFoundException,
#
#     # Validation (422)
#     AssetValidationException,
#
#     # Internal Server (500) - general use by services
#     InternalServerException,
# )

# Import common exceptions (handled internally, NOT mapped) - COMMENTED OUT BUT KEPT FOR REFERENCE
# from common.exceptions import (
#     # Database (500) - handled internally
#     DatabaseOperationException,
#     ConfigurationException,
#     ExternalServiceException,
#     AWSServiceException,
# )

# Import inventory service specific exceptions
from .exceptions import (
    CNOPAssetAlreadyExistsException,
    CNOPInventoryServerException,
    CNOPAssetValidationException,
)

__all__ = [
    # Shared exceptions (mapped to external error codes) - COMMENTED OUT BUT KEPT FOR REFERENCE
    # "InvalidCredentialsException",
    # "TokenExpiredException",
    # "TokenInvalidException",
    # "AssetNotFoundException",
    # "AssetValidationException",
    # "InternalServerException",

    # Common exceptions (handled internally, NOT mapped) - COMMENTED OUT BUT KEPT FOR REFERENCE
    # "DatabaseOperationException",
    # "ConfigurationException",
    # "ExternalServiceException",
    # "AWSServiceException",

    # Inventory service specific exceptions
    "CNOPAssetAlreadyExistsException",
    "CNOPInventoryServerException",
    "CNOPAssetValidationException",
]