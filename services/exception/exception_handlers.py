"""
Exception Handlers for FastAPI Integration

Provides standardized exception handlers that can be used with FastAPI
to return RFC 7807 Problem Details responses.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from .error_codes import ErrorCode
from .error_models import (
    ProblemDetails,
    ValidationError,
    ErrorDetails,
    create_problem_details,
    create_validation_error
)

logger = logging.getLogger(__name__)


class ExceptionHandler:
    """Base exception handler for standardized error responses"""

    @staticmethod
    def handle_validation_error(
        request: Request,
        exc: PydanticValidationError,
        trace_id: Optional[str] = None
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors

        Args:
            request: FastAPI request object
            exc: Pydantic validation error
            trace_id: Request trace ID for debugging

        Returns:
            JSONResponse with RFC 7807 Problem Details
        """

        # Extract field errors from Pydantic validation error
        errors = []
        for error in exc.errors():
            field = error.get('loc', ['unknown'])[-1] if error.get('loc') else 'unknown'
            message = error.get('msg', 'Validation failed')
            value = error.get('input')

            errors.append(ErrorDetails(
                field=str(field),
                message=message,
                value=value
            ))

        # Create validation error response
        problem_details = create_validation_error(
            detail="The request contains invalid data",
            errors=errors,
            instance=str(request.url.path),
            trace_id=trace_id
        )

        logger.warning(f"Validation error: {len(errors)} field(s) failed validation", extra={
            'trace_id': trace_id,
            'errors': [error.dict() for error in errors]
        })

        return JSONResponse(
            status_code=422,
            content=problem_details.dict()
        )

    @staticmethod
    def handle_http_exception(
        request: Request,
        exc: HTTPException,
        trace_id: Optional[str] = None
    ) -> JSONResponse:
        """
        Handle FastAPI HTTP exceptions

        Args:
            request: FastAPI request object
            exc: HTTP exception
            trace_id: Request trace ID for debugging

        Returns:
            JSONResponse with RFC 7807 Problem Details
        """

        # Map HTTP status codes to error codes
        status_to_error = {
            400: ErrorCode.INVALID_INPUT,
            401: ErrorCode.AUTHENTICATION_FAILED,
            403: ErrorCode.ACCESS_DENIED,
            404: ErrorCode.RESOURCE_NOT_FOUND,
            409: ErrorCode.RESOURCE_ALREADY_EXISTS,
            422: ErrorCode.VALIDATION_ERROR,
            500: ErrorCode.INTERNAL_SERVER_ERROR,
            503: ErrorCode.SERVICE_UNAVAILABLE,
        }

        error_code = status_to_error.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)

        problem_details = create_problem_details(
            error_code=error_code,
            detail=exc.detail,
            instance=str(request.url.path),
            trace_id=trace_id
        )

        logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}", extra={
            'trace_id': trace_id,
            'status_code': exc.status_code
        })

        return JSONResponse(
            status_code=exc.status_code,
            content=problem_details.dict()
        )

    @staticmethod
    def handle_general_exception(
        request: Request,
        exc: Exception,
        trace_id: Optional[str] = None
    ) -> JSONResponse:
        """
        Handle general exceptions (unexpected errors)

        Args:
            request: FastAPI request object
            exc: General exception
            trace_id: Request trace ID for debugging

        Returns:
            JSONResponse with RFC 7807 Problem Details
        """

        problem_details = create_problem_details(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
            instance=str(request.url.path),
            trace_id=trace_id
        )

        logger.error(f"Unexpected error: {str(exc)}", extra={
            'trace_id': trace_id,
            'exception_type': type(exc).__name__,
            'exception': str(exc)
        }, exc_info=True)

        return JSONResponse(
            status_code=500,
            content=problem_details.dict()
        )


# Convenience functions for common error scenarios
def handle_validation_error(
    detail: str,
    errors: List[ErrorDetails],
    instance: Optional[str] = None,
    trace_id: Optional[str] = None
) -> ValidationError:
    """Create a validation error response"""
    return create_validation_error(detail, errors, instance, trace_id)


def handle_authentication_error(
    detail: str,
    instance: Optional[str] = None,
    trace_id: Optional[str] = None
) -> ProblemDetails:
    """Create an authentication error response"""
    return create_problem_details(
        ErrorCode.AUTHENTICATION_FAILED,
        detail,
        instance,
        trace_id=trace_id
    )


def handle_resource_not_found(
    detail: str,
    instance: Optional[str] = None,
    trace_id: Optional[str] = None
) -> ProblemDetails:
    """Create a resource not found error response"""
    return create_problem_details(
        ErrorCode.RESOURCE_NOT_FOUND,
        detail,
        instance,
        trace_id=trace_id
    )


def handle_resource_exists(
    detail: str,
    instance: Optional[str] = None,
    trace_id: Optional[str] = None
) -> ProblemDetails:
    """Create a resource already exists error response"""
    return create_problem_details(
        ErrorCode.RESOURCE_ALREADY_EXISTS,
        detail,
        instance,
        trace_id=trace_id
    )


def handle_internal_error(
    detail: str = "An unexpected error occurred",
    instance: Optional[str] = None,
    trace_id: Optional[str] = None
) -> ProblemDetails:
    """Create an internal server error response"""
    return create_problem_details(
        ErrorCode.INTERNAL_SERVER_ERROR,
        detail,
        instance,
        trace_id=trace_id
    )


# FastAPI exception handler registration
def register_exception_handlers(app):
    """
    Register exception handlers with FastAPI app

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(PydanticValidationError)
    async def validation_exception_handler(request: Request, exc: PydanticValidationError):
        return ExceptionHandler.handle_validation_error(request, exc)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return ExceptionHandler.handle_http_exception(request, exc)

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return ExceptionHandler.handle_general_exception(request, exc)