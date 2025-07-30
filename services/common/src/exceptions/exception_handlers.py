"""
Standardized exception handlers for FastAPI applications
Path: services/common/src/exceptions/exception_handlers.py
"""

import logging
import traceback
import uuid
from typing import Dict, Any, List
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from .error_codes import CommonErrorCode, get_http_status_code, map_service_error_to_common
from .error_models import (
    ErrorResponse,
    ValidationError,
    ErrorDetails,
    create_error_response,
    create_validation_error_response,
    create_internal_error_response
)

logger = logging.getLogger(__name__)


class CommonExceptionHandler:
    """Base class for standardized exception handling"""

    @staticmethod
    def get_request_id(request: Request) -> str:
        """Extract or generate request ID"""
        return request.headers.get("X-Request-ID", str(uuid.uuid4()))

    @staticmethod
    def log_error(
        request: Request,
        error: Exception,
        error_id: str,
        error_code: CommonErrorCode,
        context: Dict[str, Any] = None
    ):
        """Log error with structured context"""
        log_context = {
            "error_id": error_id,
            "error_code": error_code.value,
            "request_method": request.method,
            "request_url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }

        if context:
            log_context.update(context)

        logger.error(
            f"Error {error_id}: {error_code.value} - {str(error)}",
            extra=log_context
        )


def handle_validation_error(
    request: Request,
    exc: RequestValidationError,
    service_name: str = "unknown"
) -> JSONResponse:
    """Handle Pydantic validation errors with standardized response"""
    error_id = CommonExceptionHandler.get_request_id(request)

    # Log validation errors for debugging
    CommonExceptionHandler.log_error(
        request=request,
        error=exc,
        error_id=error_id,
        error_code=CommonErrorCode.VALIDATION_ERROR,
        context={
            "service_name": service_name,
            "validation_errors": exc.errors()
        }
    )

    # Convert Pydantic errors to standardized format
    validation_errors = []
    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "unknown"
        message = error["msg"]
        value = error.get("input")

        # Map common Pydantic error messages to user-friendly ones
        if "ensure this value is greater than or equal to" in message:
            if "limit" in field.lower():
                message = "Limit must be at least 1"
            else:
                message = f"{field.replace('_', ' ').title()} must be a positive number"
        elif "ensure this value is less than or equal to" in message:
            if "limit" in field.lower():
                message = "Limit cannot exceed 100"
        elif "value is not a valid boolean" in message:
            if "active_only" in field.lower():
                message = "active_only must be true or false"
        elif "field required" in message:
            message = f"{field.replace('_', ' ').title()} is required"
        elif "value is not a valid email" in message:
            message = "Please enter a valid email address"
        elif "ensure this value has at least" in message:
            min_length = message.split("least ")[-1].split(" ")[0]
            message = f"{field.replace('_', ' ').title()} must be at least {min_length} characters"
        elif "ensure this value has at most" in message:
            max_length = message.split("most ")[-1].split(" ")[0]
            message = f"{field.replace('_', ' ').title()} must be at most {max_length} characters"

        validation_errors.append(ValidationError(
            field=field,
            message=message,
            value=value
        ))

    # Create standardized error response
    error_response = create_validation_error_response(
        validation_errors=validation_errors,
        request_id=error_id
    )

    return JSONResponse(
        status_code=get_http_status_code(CommonErrorCode.VALIDATION_ERROR),
        content=error_response.model_dump()
    )


def handle_internal_error(
    request: Request,
    exc: Exception,
    service_name: str = "unknown"
) -> JSONResponse:
    """Handle unexpected exceptions with standardized response"""
    error_id = CommonExceptionHandler.get_request_id(request)

    # Log full details for debugging
    CommonExceptionHandler.log_error(
        request=request,
        error=exc,
        error_id=error_id,
        error_code=CommonErrorCode.INTERNAL_ERROR,
        context={
            "service_name": service_name,
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }
    )

    # Create standardized error response (never expose internal details)
    error_response = create_internal_error_response(request_id=error_id)

    return JSONResponse(
        status_code=get_http_status_code(CommonErrorCode.INTERNAL_ERROR),
        content=error_response.model_dump()
    )


def handle_http_error(
    request: Request,
    exc,
    service_name: str = "unknown"
) -> JSONResponse:
    """Handle HTTP exceptions with standardized response"""
    error_id = CommonExceptionHandler.get_request_id(request)

    # Log HTTP exceptions
    CommonExceptionHandler.log_error(
        request=request,
        error=exc,
        error_id=error_id,
        error_code=CommonErrorCode.RESOURCE_NOT_FOUND,
        context={
            "service_name": service_name,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )

    # Map HTTP status codes to appropriate error codes
    if exc.status_code == 404:
        # Extract resource info from URL if possible
        path_parts = str(request.url.path).split("/")
        resource_id = path_parts[-1] if len(path_parts) > 0 and path_parts[-1] != "" else None
        resource_type = path_parts[-2] if len(path_parts) > 1 else "resource"

        error_response = create_error_response(
            error_code=CommonErrorCode.RESOURCE_NOT_FOUND,
            message=f"{resource_type.title()} not found",
            details=ErrorDetails(
                field="id",
                context={"resource_type": resource_type, "resource_id": resource_id}
            ),
            request_id=error_id
        )
    elif exc.status_code == 503:
        error_response = create_error_response(
            error_code=CommonErrorCode.SERVICE_UNAVAILABLE,
            message="Service is temporarily unavailable. Please try again later.",
            request_id=error_id
        )
    elif exc.status_code == 429:
        error_response = create_error_response(
            error_code=CommonErrorCode.RATE_LIMIT_EXCEEDED,
            message="Too many requests. Please wait before trying again.",
            request_id=error_id
        )
    else:
        error_response = create_internal_error_response(request_id=error_id)

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


def handle_service_specific_error(
    request: Request,
    service_error_code: str,
    message: str,
    details: Dict[str, Any] = None,
    service_name: str = "unknown"
) -> JSONResponse:
    """Handle service-specific errors by mapping to common error codes"""
    error_id = CommonExceptionHandler.get_request_id(request)

    # Map service error to common error code
    common_error_code = map_service_error_to_common(service_error_code)

    # Log service-specific error
    CommonExceptionHandler.log_error(
        request=request,
        error=Exception(message),
        error_id=error_id,
        error_code=common_error_code,
        context={
            "service_name": service_name,
            "service_error_code": service_error_code,
            "details": details
        }
    )

    # Create standardized error response
    error_details = ErrorDetails(context=details) if details else None
    error_response = create_error_response(
        error_code=common_error_code,
        message=message,
        details=error_details,
        request_id=error_id
    )

    return JSONResponse(
        status_code=get_http_status_code(common_error_code),
        content=error_response.model_dump()
    )