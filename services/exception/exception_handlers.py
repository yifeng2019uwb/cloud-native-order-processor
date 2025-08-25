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
from .error_models import ProblemDetails, create_problem_details
from .exception_mapping import map_service_exception, map_validation_error

logger = logging.getLogger(__name__)


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
    problem_details = map_validation_error(
        exc=exc,
        instance=str(request.url.path),
        trace_id=trace_id
    )

    logger.warning(f"Validation error: {len(exc.errors())} field(s) failed validation", extra={
        'trace_id': trace_id,
        'errors': exc.errors()
    })

    return JSONResponse(
        status_code=problem_details.status,
        content=problem_details.dict()
    )


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
        400: ErrorCode.VALIDATION_ERROR,
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
        status_code=problem_details.status,
        content=problem_details.dict()
    )


def handle_general_exception(
    request: Request,
    exc: Exception,
    trace_id: Optional[str] = None
) -> JSONResponse:
    """
    Handle general exceptions

    Args:
        request: FastAPI request object
        exc: General exception
        trace_id: Request trace ID for debugging

    Returns:
        JSONResponse with RFC 7807 Problem Details
    """
    # Try to map the exception using our exception mapper
    try:
        problem_details = map_service_exception(
            exc=exc,
            instance=str(request.url.path),
            trace_id=trace_id
        )
    except Exception as mapping_error:
        logger.error(f"Exception mapping failed: {mapping_error}")
        # Fall back to generic internal server error
        problem_details = create_problem_details(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
            instance=str(request.url.path),
            trace_id=trace_id
        )

    logger.error(f"General exception: {type(exc).__name__} - {str(exc)}", extra={
        'trace_id': trace_id,
        'exception_type': type(exc).__name__,
        'exception_message': str(exc)
    })

    return JSONResponse(
        status_code=problem_details.status,
        content=problem_details.dict()
    )


def register_exception_handlers(app):
    """
    Register exception handlers with FastAPI app

    Args:
        app: FastAPI application instance
    """
    # Configure service exceptions for mapping
    from .exception_mapping import configure_service_exceptions
    configure_service_exceptions()

    @app.exception_handler(PydanticValidationError)
    def validation_exception_handler(request: Request, exc: PydanticValidationError):
        return handle_validation_error(request, exc)

    @app.exception_handler(HTTPException)
    def http_exception_handler(request: Request, exc: HTTPException):
        return handle_http_exception(request, exc)

    @app.exception_handler(Exception)
    def general_exception_handler(request: Request, exc: Exception):
        return handle_general_exception(request, exc)