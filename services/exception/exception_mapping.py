"""
Exception Mapping Utilities

Maps internal service-specific exceptions to external standardized exceptions
for consistent error handling across all services.
"""

import logging
from typing import Dict, Type, Optional, Any
from pydantic import ValidationError as PydanticValidationError

from .error_codes import ErrorCode
from .error_models import ProblemDetails, create_problem_details

logger = logging.getLogger(__name__)


class ExceptionMapper:
    """
    Maps internal exceptions to external standardized exceptions

    This class provides a centralized way to convert service-specific exceptions
    into standardized error responses that follow RFC 7807.
    """

    def __init__(self):
        # Default mapping of exception types to error codes
        self._exception_mapping: Dict[Type[Exception], ErrorCode] = {
            # Pydantic validation errors
            PydanticValidationError: ErrorCode.VALIDATION_ERROR,

            # Common Python exceptions
            ValueError: ErrorCode.INVALID_INPUT,
            TypeError: ErrorCode.INVALID_INPUT,
            KeyError: ErrorCode.MISSING_REQUIRED_FIELD,
            AttributeError: ErrorCode.INVALID_INPUT,

            # Database exceptions (generic)
            Exception: ErrorCode.INTERNAL_SERVER_ERROR,  # Fallback
        }

        # Custom mapping functions for complex exceptions
        self._custom_mappers: Dict[Type[Exception], callable] = {}

    def register_exception_mapping(
        self,
        exception_type: Type[Exception],
        error_code: ErrorCode
    ) -> None:
        """
        Register a mapping for a specific exception type

        Args:
            exception_type: The exception class to map
            error_code: The standard error code to use
        """
        self._exception_mapping[exception_type] = error_code
        logger.debug(f"Registered exception mapping: {exception_type.__name__} -> {error_code}")

    def register_custom_mapper(
        self,
        exception_type: Type[Exception],
        mapper_func: callable
    ) -> None:
        """
        Register a custom mapping function for complex exceptions

        Args:
            exception_type: The exception class to map
            mapper_func: Function that takes exception and returns ProblemDetails
        """
        self._custom_mappers[exception_type] = mapper_func
        logger.debug(f"Registered custom mapper for: {exception_type.__name__}")

    def map_exception(
        self,
        exc: Exception,
        instance: Optional[str] = None,
        trace_id: Optional[str] = None,
        **kwargs
    ) -> ProblemDetails:
        """
        Map an exception to a standardized Problem Details response

        Args:
            exc: The exception to map
            instance: The endpoint that caused the error
            trace_id: Request trace ID for debugging
            **kwargs: Additional context for custom mappers

        Returns:
            ProblemDetails instance
        """
        exception_type = type(exc)

        # Check for custom mapper first
        if exception_type in self._custom_mappers:
            try:
                return self._custom_mappers[exception_type](exc, instance, trace_id, **kwargs)
            except Exception as mapper_error:
                logger.error(f"Custom mapper failed for {exception_type.__name__}: {mapper_error}")
                # Fall back to default mapping

        # Use registered mapping
        error_code = self._exception_mapping.get(exception_type, ErrorCode.INTERNAL_SERVER_ERROR)

        # Get appropriate detail message
        detail = self._get_exception_detail(exc, error_code)

        return create_problem_details(
            error_code=error_code,
            detail=detail,
            instance=instance,
            trace_id=trace_id
        )

    def _get_exception_detail(self, exc: Exception, error_code: ErrorCode) -> str:
        """Get appropriate detail message for an exception"""

        # Use exception message if available
        if hasattr(exc, 'message'):
            return str(exc.message)
        elif hasattr(exc, 'detail'):
            return str(exc.detail)
        elif str(exc):
            return str(exc)

        # Fallback messages based on error code
        fallback_messages = {
            ErrorCode.VALIDATION_ERROR: "The request contains invalid data",
            ErrorCode.INVALID_INPUT: "Invalid input provided",
            ErrorCode.MISSING_REQUIRED_FIELD: "Required field is missing",
            ErrorCode.AUTHENTICATION_FAILED: "Authentication failed",
            ErrorCode.RESOURCE_NOT_FOUND: "Resource not found",
            ErrorCode.RESOURCE_ALREADY_EXISTS: "Resource already exists",
            ErrorCode.INTERNAL_SERVER_ERROR: "An unexpected error occurred",
        }

        return fallback_messages.get(error_code, "An error occurred")


# Global exception mapper instance
exception_mapper = ExceptionMapper()


# Pre-configured mappings for common service exceptions
def configure_service_exceptions():
    """Configure common exception mappings for services"""

    # User Service specific exceptions
    try:
        from user_service.exceptions import (
            UserNotFoundException,
            UserAlreadyExistsException,
            InvalidCredentialsException,
            UsernameTakenException,
            EmailTakenException
        )

        exception_mapper.register_exception_mapping(UserNotFoundException, ErrorCode.USER_NOT_FOUND)
        exception_mapper.register_exception_mapping(UserAlreadyExistsException, ErrorCode.RESOURCE_ALREADY_EXISTS)
        exception_mapper.register_exception_mapping(InvalidCredentialsException, ErrorCode.INVALID_CREDENTIALS)
        exception_mapper.register_exception_mapping(UsernameTakenException, ErrorCode.USERNAME_TAKEN)
        exception_mapper.register_exception_mapping(EmailTakenException, ErrorCode.EMAIL_TAKEN)

    except ImportError:
        logger.debug("User service exceptions not available")

    # Inventory Service specific exceptions
    try:
        from inventory_service.exceptions import (
            AssetNotFoundException,
            AssetAlreadyExistsException
        )

        exception_mapper.register_exception_mapping(AssetNotFoundException, ErrorCode.ASSET_NOT_FOUND)
        exception_mapper.register_exception_mapping(AssetAlreadyExistsException, ErrorCode.RESOURCE_ALREADY_EXISTS)

    except ImportError:
        logger.debug("Inventory service exceptions not available")


# Custom mappers for complex exceptions
def map_validation_error(exc: PydanticValidationError, instance: str, trace_id: str, **kwargs) -> ProblemDetails:
    """Custom mapper for Pydantic validation errors"""
    from .error_models import ErrorDetails, create_validation_error

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

    return create_validation_error(
        detail="The request contains invalid data",
        errors=errors,
        instance=instance,
        trace_id=trace_id
    )


# Register custom mappers
exception_mapper.register_custom_mapper(PydanticValidationError, map_validation_error)


# Convenience functions for common mapping scenarios
def map_service_exception(
    exc: Exception,
    instance: Optional[str] = None,
    trace_id: Optional[str] = None,
    **kwargs
) -> ProblemDetails:
    """
    Map a service exception to a standardized response

    Args:
        exc: The service exception
        instance: The endpoint that caused the error
        trace_id: Request trace ID for debugging
        **kwargs: Additional context

    Returns:
        ProblemDetails instance
    """
    return exception_mapper.map_exception(exc, instance, trace_id, **kwargs)


def map_database_exception(
    exc: Exception,
    instance: Optional[str] = None,
    trace_id: Optional[str] = None
) -> ProblemDetails:
    """
    Map database exceptions to standardized responses

    Args:
        exc: The database exception
        instance: The endpoint that caused the error
        trace_id: Request trace ID for debugging

    Returns:
        ProblemDetails instance
    """
    # Map common database exceptions
    if "duplicate" in str(exc).lower() or "unique" in str(exc).lower():
        return create_problem_details(
            ErrorCode.RESOURCE_ALREADY_EXISTS,
            "Resource already exists",
            instance,
            trace_id=trace_id
        )
    elif "not found" in str(exc).lower():
        return create_problem_details(
            ErrorCode.RESOURCE_NOT_FOUND,
            "Resource not found",
            instance,
            trace_id=trace_id
        )
    else:
        return create_problem_details(
            ErrorCode.DATABASE_ERROR,
            "Database operation failed",
            instance,
            trace_id=trace_id
        )


# Initialize service exceptions
configure_service_exceptions()