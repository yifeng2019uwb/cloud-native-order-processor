"""
Exception handling package for inventory service
"""

# Import internal exceptions
from .internal_exceptions import (
    InternalInventoryError,
    InternalAssetNotFoundError,
    InternalDatabaseError,
    InternalValidationError,
    AssetNotFoundException,
    InvalidAssetDataException,
    raise_asset_not_found,
    raise_database_error,
    raise_validation_error
)

# Import secure exception handlers
from .secure_exceptions import (
    secure_validation_exception_handler,
    secure_general_exception_handler,
    secure_http_exception_handler,
    StandardErrorResponse,
    # Single generic handler for all common package exceptions
    secure_common_exception_handler,
    secure_internal_exception_handler
)

__all__ = [
    # Internal exceptions
    "InternalInventoryError",
    "InternalAssetNotFoundError",
    "InternalDatabaseError",
    "InternalValidationError",
    "AssetNotFoundException",
    "InvalidAssetDataException",
    "raise_asset_not_found",
    "raise_database_error",
    "raise_validation_error",

    # Secure exception handlers
    "secure_validation_exception_handler",
    "secure_general_exception_handler",
    "secure_http_exception_handler",
    "StandardErrorResponse",
    "secure_internal_exception_handler",

    # Single generic handler for all common package exceptions
    "secure_common_exception_handler"
]