"""
Secure exception handlers for inventory service
Path: services/inventory-service/src/exceptions/secure_exceptions.py
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Dict, Any, List
import logging
from datetime import datetime
import traceback
import uuid

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
    def asset_not_found(asset_id: str = None) -> Dict[str, Any]:
        """Asset not found error response"""
        if asset_id:
            return {
                "success": False,
                "error": "ASSET_NOT_FOUND",
                "message": f"Asset '{asset_id}' not found.",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "ASSET_NOT_FOUND",
                "message": "The requested asset was not found.",
                "timestamp": datetime.utcnow().isoformat()
            }

    @staticmethod
    def service_unavailable() -> Dict[str, Any]:
        """Generic service unavailable"""
        return {
            "success": False,
            "error": "SERVICE_UNAVAILABLE",
            "message": "Inventory service is temporarily unavailable. Please try again later.",
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def database_error() -> Dict[str, Any]:
        """Database connection error"""
        return {
            "success": False,
            "error": "DATABASE_ERROR",
            "message": "Unable to connect to inventory database. Please try again later.",
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


# ========================================
# FASTAPI EXCEPTION HANDLERS
# ========================================

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


async def secure_http_exception_handler(request: Request, exc):
    """
    Handle HTTP exceptions (like 404, 500) securely
    """
    error_id = str(uuid.uuid4())

    # Log HTTP exceptions
    logger.warning(
        f"HTTP exception {error_id}: {request.method} {request.url} - {exc.status_code}: {exc.detail}",
        extra={
            "error_id": error_id,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "request_method": request.method,
            "request_url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown"
        }
    )

    # Map HTTP status codes to appropriate responses
    if exc.status_code == 404:
        # Extract asset_id from URL if possible
        path_parts = str(request.url.path).split("/")
        asset_id = path_parts[-1] if len(path_parts) > 0 and path_parts[-1] != "assets" else None
        content = StandardErrorResponse.asset_not_found(asset_id)
    elif exc.status_code == 503:
        content = StandardErrorResponse.service_unavailable()
    elif exc.status_code == 429:
        content = StandardErrorResponse.rate_limited()
    else:
        content = StandardErrorResponse.internal_error()

    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )