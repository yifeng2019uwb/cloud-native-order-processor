"""
User service exceptions package

This package contains user service-specific exceptions for business logic validation.
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
#     UserNotFoundException,
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
#     # Business logic exceptions
#     InsufficientBalanceException,
# )

# Import user service specific exceptions
from .exceptions import (
    CNOPUserAlreadyExistsException,
    CNOPUserServerException,
    CNOPUserValidationException,
    CNOPDailyLimitExceededException,
)

__all__ = [
    # Shared exceptions (mapped to external error codes) - COMMENTED OUT BUT KEPT FOR REFERENCE
    # "InvalidCredentialsException",
    # "TokenExpiredException",
    # "TokenInvalidException",
    # "UserNotFoundException",
    # "UserValidationException",
    # "InternalServerException",

    # Common exceptions (handled internally, NOT mapped) - COMMENTED OUT BUT KEPT FOR REFERENCE
    # "DatabaseOperationException",
    # "ConfigurationException",
    # "ExternalServiceException",
    # "InsufficientBalanceException",

    # User service specific exceptions
    "CNOPUserAlreadyExistsException",
    "CNOPUserServerException",
    "CNOPUserValidationException",
    "CNOPDailyLimitExceededException",
]