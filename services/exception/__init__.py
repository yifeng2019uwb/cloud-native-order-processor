"""
Standardized exception models for external API responses
Path: services/exception/__init__.py

This package defines the standard error responses that are returned to external clients
(frontend, API consumers) across all services.
"""

from .error_models import (
    StandardErrorResponse,
    ValidationError,
    ErrorDetails,
    create_standard_error_response,
    create_validation_error_response,
    create_resource_not_found_response,
    create_resource_exists_response,
    create_authentication_failed_response,
    create_internal_error_response
)

from .error_codes import (
    StandardErrorCode,
    get_http_status_code,
    map_service_error_to_standard
)

__all__ = [
    # Error codes
    "StandardErrorCode",
    "get_http_status_code",
    "map_service_error_to_standard",

    # Error models
    "StandardErrorResponse",
    "ValidationError",
    "ErrorDetails",
    "create_standard_error_response",
    "create_validation_error_response",
    "create_resource_not_found_response",
    "create_resource_exists_response",
    "create_authentication_failed_response",
    "create_internal_error_response"
]