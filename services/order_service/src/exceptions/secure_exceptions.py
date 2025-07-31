"""
Secure exception handling for order service
Path: services/order_service/src/exceptions/secure_exceptions.py
"""
import uuid
import traceback
from datetime import datetime
from typing import Dict, Any, List

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from .internal_exceptions import (
    InternalOrderError,
    InternalOrderNotFoundError,
    InternalOrderExistsError,
    InternalOrderValidationError,
    InternalOrderStatusError,
    InternalDatabaseError
)

# Import common package exceptions
from common.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    ConfigurationError,
    EntityValidationError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
    BusinessRuleError,
    AWSError
)

logger = logging.getLogger(__name__)


class StandardErrorResponse:
    """Standard error responses for client consumption"""

    @staticmethod
    def validation_error(validation_errors: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validation error response"""
        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Invalid order data provided",
            "validation_errors": validation_errors or [],
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def order_not_found() -> Dict[str, Any]:
        """Order not found error response"""
        return {
            "success": False,
            "error": "ORDER_NOT_FOUND",
            "message": "The requested order was not found",
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def order_exists() -> Dict[str, Any]:
        """Order already exists error response"""
        return {
            "success": False,
            "error": "ORDER_EXISTS",
            "message": "Order creation failed",
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def order_status_error() -> Dict[str, Any]:
        """Order status error response"""
        return {
            "success": False,
            "error": "ORDER_STATUS_ERROR",
            "message": "Order status update failed",
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def service_unavailable() -> Dict[str, Any]:
        """Service unavailable error response"""
        return {
            "success": False,
            "error": "SERVICE_UNAVAILABLE",
            "message": "Service is temporarily unavailable. Please try again later.",
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
    def map_to_client_response(internal_error: InternalOrderError) -> tuple[int, Dict[str, Any]]:
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
            "ORDER_NOT_FOUND_DETAILED": (status.HTTP_404_NOT_FOUND, StandardErrorResponse.order_not_found()),
            "ORDER_EXISTS_DETAILED": (status.HTTP_409_CONFLICT, StandardErrorResponse.order_exists()),
            "ORDER_VALIDATION_ERROR_DETAILED": (status.HTTP_422_UNPROCESSABLE_ENTITY, StandardErrorResponse.validation_error()),
            "ORDER_STATUS_ERROR_DETAILED": (status.HTTP_400_BAD_REQUEST, StandardErrorResponse.order_status_error()),
            "DATABASE_ERROR_DETAILED": (status.HTTP_503_SERVICE_UNAVAILABLE, StandardErrorResponse.service_unavailable()),
        }

        return mapping.get(
            internal_error.error_code,
            (status.HTTP_500_INTERNAL_SERVER_ERROR, StandardErrorResponse.internal_error())
        )


# ========================================
# FASTAPI EXCEPTION HANDLERS
# ========================================

async def secure_internal_exception_handler(request: Request, exc: InternalOrderError):
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


# ========================================
# COMMON PACKAGE EXCEPTION HANDLERS
# ========================================

async def secure_common_exception_handler(request: Request, exc):
    """
    Generic handler for all common package internal exceptions

    Converts any common package exception to order service internal exception
    and then handles it through the secure exception system
    """
    # Determine the type of common package exception and convert appropriately
    if isinstance(exc, DatabaseConnectionError):
        internal_error = InternalDatabaseError(
            operation="connection",
            table_name="orders",
            original_error=exc
        )
    elif isinstance(exc, DatabaseOperationError):
        internal_error = InternalDatabaseError(
            operation="operation",
            table_name="orders",
            original_error=exc
        )
    elif isinstance(exc, EntityAlreadyExistsError):
        internal_error = InternalOrderExistsError(
            order_id=exc.context.get("order_id", "unknown"),
            order_type=exc.context.get("order_type", "unknown"),
            asset_id=exc.context.get("asset_id", "unknown"),
            user_id=exc.context.get("user_id")
        )
    elif isinstance(exc, EntityValidationError):
        internal_error = InternalOrderValidationError(
            field=exc.context.get("field", "unknown"),
            value=exc.context.get("value"),
            rule=exc.context.get("rule", "validation"),
            details=exc.message,
            order_type=exc.context.get("order_type")
        )
    elif isinstance(exc, ConfigurationError):
        internal_error = InternalDatabaseError(
            operation="configuration",
            table_name="orders",
            original_error=exc
        )
    elif isinstance(exc, AWSError):
        internal_error = InternalDatabaseError(
            operation="aws_operation",
            table_name="orders",
            original_error=exc
        )
    elif isinstance(exc, EntityNotFoundError):
        internal_error = InternalOrderNotFoundError(
            order_id=exc.context.get("order_id", "unknown"),
            user_id=exc.context.get("user_id"),
            search_criteria=exc.context.get("search_criteria")
        )
    elif isinstance(exc, BusinessRuleError):
        internal_error = InternalOrderValidationError(
            field="business_rule",
            value="unknown",
            rule="business_validation",
            details=exc.message,
            order_type=exc.context.get("order_type")
        )
    else:
        # Fallback for any other common package exception
        internal_error = InternalDatabaseError(
            operation="unknown",
            table_name="orders",
            original_error=exc
        )

    # Handle through the secure exception system
    return await secure_internal_exception_handler(request, internal_error)


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
            if "quantity" in field.lower():
                message = "Quantity must be at least 0.001"
            elif "order_price" in field.lower():
                message = "Order price must be greater than 0"
        elif "ensure this value has at most" in message:
            if "quantity" in field.lower():
                message = "Quantity exceeds maximum allowed"
        elif "ensure this value is greater than" in message:
            if "quantity" in field.lower():
                message = "Quantity must be greater than 0"
            elif "order_price" in field.lower():
                message = "Order price must be greater than 0"
        elif "field required" in message:
            if "order_type" in field.lower():
                message = "Order type is required"
            elif "asset_id" in field.lower():
                message = "Asset ID is required"
            elif "quantity" in field.lower():
                message = "Quantity is required"
        elif "value is not a valid" in message:
            if "order_type" in field.lower():
                message = "Invalid order type. Must be one of: market_buy, market_sell, limit_buy, limit_sell"
            elif "asset_id" in field.lower():
                message = "Invalid asset ID format"

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
