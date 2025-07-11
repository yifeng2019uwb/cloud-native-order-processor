"""
Secure exception handlers that map internal exceptions to safe client responses
Path: cloud-native-order-processor/services/user-service/src/exceptions/secure_exceptions.py
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Dict, Any, List
import logging
from datetime import datetime
import traceback
import uuid

from .internal_exceptions import InternalAuthError

logger = logging.getLogger(__name__)


class StandardErrorResponse:
    """Standard error responses that are safe to send to clients"""

    @staticmethod
    def validation_error(validation_errors: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validation error response with optional field-specific errors"""
        if validation_errors:
            return {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "Please correct the following errors:",
                "validation_errors": validation_errors,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "INVALID_INPUT",
                "message": "The provided information is invalid. Please check your input and try again.",
                "timestamp": datetime.utcnow().isoformat()
            }

    @staticmethod
    def user_exists_error(field: str = None) -> Dict[str, Any]:
        """User exists error response - can be specific about which field exists"""
        if field:
            return {
                "success": False,
                "error": "USER_EXISTS",
                "message": f"{field.capitalize()} already exists. Please choose a different {field}.",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "REGISTRATION_FAILED",
                "message": "Unable to create account. Please try again or contact support.",
                "timestamp": datetime.utcnow().isoformat()
            }

    @staticmethod
    def authentication_failed() -> Dict[str, Any]:
        """Generic authentication failure"""
        return {
            "success": False,
            "error": "AUTHENTICATION_FAILED",
            "message": "Invalid credentials. Please check your information and try again.",
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def service_unavailable() -> Dict[str, Any]:
        """Generic service unavailable"""
        return {
            "success": False,
            "error": "SERVICE_UNAVAILABLE",
            "message": "Service is temporarily unavailable. Please try again later.",
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def rate_limited() -> Dict[str, Any]:
        """Generic rate limit response"""
        return {
            "success": False,
            "error": "TOO_MANY_REQUESTS",
            "message": "Too many requests. Please wait before trying again.",
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def internal_error() -> Dict[str, Any]:
        """Generic internal error"""
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat()
        }


class SecureExceptionMapper:
    """Maps internal exceptions to safe client responses"""

    @staticmethod
    def map_to_client_response(internal_error: InternalAuthError) -> tuple[int, Dict[str, Any]]:
        """
        Map internal exception to safe client response

        Args:
            internal_error: Internal exception with detailed context

        Returns:
            Tuple of (status_code, response_dict)
        """
        # Log detailed internal error for debugging
        logger.error(
            f"Internal error {internal_error.error_id}: {internal_error.error_code} - {internal_error.message}",
            extra={
                "error_id": internal_error.error_id,
                "error_code": internal_error.error_code,
                "context": internal_error.context,
                "timestamp": internal_error.timestamp.isoformat()
            }
        )

        # Map to safe client responses
        mapping = {
            "USER_EXISTS_DETAILED": (status.HTTP_409_CONFLICT, StandardErrorResponse.user_exists_error()),
            "DATABASE_ERROR_DETAILED": (status.HTTP_503_SERVICE_UNAVAILABLE, StandardErrorResponse.service_unavailable()),
            "VALIDATION_ERROR_DETAILED": (status.HTTP_422_UNPROCESSABLE_ENTITY, StandardErrorResponse.validation_error()),
            "SECURITY_VIOLATION_DETAILED": (status.HTTP_429_TOO_MANY_REQUESTS, StandardErrorResponse.rate_limited()),
        }

        return mapping.get(
            internal_error.error_code,
            (status.HTTP_500_INTERNAL_SERVER_ERROR, StandardErrorResponse.internal_error())
        )


# ========================================
# FASTAPI EXCEPTION HANDLERS
# ========================================

async def secure_internal_exception_handler(request: Request, exc: InternalAuthError):
    """
    Handle internal exceptions securely - log details, return generic response
    """
    # Map to safe client response
    status_code, response_content = SecureExceptionMapper.map_to_client_response(exc)

    # Add request context to logs
    logger.error(
        f"Request {exc.error_id} failed: {request.method} {request.url}",
        extra={
            "error_id": exc.error_id,
            "request_method": request.method,
            "request_url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
    )

    return JSONResponse(
        status_code=status_code,
        content=response_content
    )


async def secure_validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with specific field-level error messages
    """
    # Log detailed validation errors for debugging
    error_id = str(uuid.uuid4())
    logger.warning(
        f"Validation error {error_id}: {request.method} {request.url}",
        extra={
            "error_id": error_id,
            "validation_errors": exc.errors(),
            "request_method": request.method,
            "request_url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown"
        }
    )

    # Convert Pydantic errors to user-friendly format
    validation_errors = []
    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "unknown"
        message = error["msg"]

        # Map common Pydantic error messages to user-friendly ones
        if "ensure this value has at least" in message:
            if "username" in field.lower():
                message = "Username must be at least 6 characters"
            elif "password" in field.lower():
                message = "Password must be at least 12 characters"
            elif "first_name" in field.lower() or "last_name" in field.lower():
                message = f"{field.replace('_', ' ').title()} must be at least 1 character"
        elif "ensure this value has at most" in message:
            if "username" in field.lower():
                message = "Username must be no more than 30 characters"
            elif "password" in field.lower():
                message = "Password must be no more than 20 characters"
        elif "value is not a valid email address" in message:
            message = "Please enter a valid email address"
        elif "ensure this value matches" in message:
            if "username" in field.lower():
                message = "Username can only contain letters, numbers, and underscores. Cannot start/end with underscore."
            elif "password" in field.lower():
                message = "Password must contain uppercase, lowercase, numbers, and special characters"
        elif "ensure this value contains" in message:
            if "password" in field.lower():
                if "uppercase" in message:
                    message = "Password must contain at least one uppercase letter"
                elif "lowercase" in message:
                    message = "Password must contain at least one lowercase letter"
                elif "number" in message:
                    message = "Password must contain at least one number"
                elif "special character" in message:
                    message = "Password must contain at least one special character (!@#$%^&*()-_=+)"

        validation_errors.append({
            "field": field,
            "message": message
        })

    # Return specific validation errors to client
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=StandardErrorResponse.validation_error(validation_errors)
    )


async def secure_general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions securely
    """
    error_id = str(uuid.uuid4())

    # Log full details for debugging
    logger.error(
        f"Unexpected error {error_id}: {request.method} {request.url} - {str(exc)}",
        extra={
            "error_id": error_id,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
            "request_method": request.method,
            "request_url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown"
        }
    )

    # Return generic error to client (never expose internal details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=StandardErrorResponse.internal_error()
    )