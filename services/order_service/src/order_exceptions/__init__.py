"""
Order service exceptions package
Path: services/order_service/src/exceptions/__init__.py

This package contains order service-specific exceptions for business logic validation.
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
#     OrderNotFoundException,
#     UserNotFoundException,
#     AssetNotFoundException,
#
#     # Validation (422)
#     OrderValidationException,
#     UserValidationException,
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

# Import order service specific exceptions
from .exceptions import (
    CNOPOrderAlreadyExistsException,
    CNOPOrderServerException,
    CNOPOrderValidationException,
)

__all__ = [
    # Shared exceptions (mapped to external error codes) - COMMENTED OUT BUT KEPT FOR REFERENCE
    # "InvalidCredentialsException",
    # "TokenExpiredException",
    # "TokenInvalidException",
    # "OrderNotFoundException",
    # "UserNotFoundException",
    # "AssetNotFoundException",
    # "OrderValidationException",
    # "UserValidationException",
    # "InternalServerException",

    # Common exceptions (handled internally, NOT mapped) - COMMENTED OUT BUT KEPT FOR REFERENCE
    # "DatabaseOperationException",
    # "ConfigurationException",
    # "ExternalServiceException",
    # "AWSServiceException",

    # Order service specific exceptions
    "CNOPOrderAlreadyExistsException",
    "CNOPOrderServerException",
    "CNOPOrderValidationException",
]
