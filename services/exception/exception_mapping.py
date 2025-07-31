"""
Exception Mapping Utilities

Maps internal service-specific exceptions to external standardized exceptions
for consistent error handling across all services.
"""

import logging
import sys
import os
from typing import Dict, Type, Optional, Any
from pydantic import ValidationError as PydanticValidationError

try:
    from .error_codes import ErrorCode
    from .error_models import ProblemDetails, create_problem_details
except ImportError:
    from error_codes import ErrorCode
    from error_models import ProblemDetails, create_problem_details

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
            ValueError: ErrorCode.VALIDATION_ERROR,
            TypeError: ErrorCode.VALIDATION_ERROR,
            KeyError: ErrorCode.VALIDATION_ERROR,
            AttributeError: ErrorCode.VALIDATION_ERROR,

            # Generic fallback
            Exception: ErrorCode.INTERNAL_SERVER_ERROR,
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
                pass

        # Find the best matching exception type
        error_code = self._find_best_match(exception_type)
        detail = self._get_exception_detail(exc, error_code)

        return create_problem_details(
            error_code=error_code,
            detail=detail,
            instance=instance,
            trace_id=trace_id
        )

    def _find_best_match(self, exception_type: Type[Exception]) -> ErrorCode:
        """
        Find the best matching error code for an exception type
        """
        # Direct match
        if exception_type in self._exception_mapping:
            return self._exception_mapping[exception_type]

        # Check parent classes
        for parent in exception_type.__mro__[1:]:  # Skip the class itself
            if parent in self._exception_mapping:
                return self._exception_mapping[parent]

        # Default fallback
        return ErrorCode.INTERNAL_SERVER_ERROR

    def _get_exception_detail(self, exc: Exception, error_code: ErrorCode) -> str:
        """
        Get a user-friendly detail message for the exception
        """
        # Use the exception message if available
        if hasattr(exc, 'message') and exc.message:
            return exc.message

        # Use the exception string representation
        if str(exc):
            return str(exc)

        # Fall back to default error detail
        from .error_codes import get_error_detail
        return get_error_detail(error_code)


# Global exception mapper instance
exception_mapper = ExceptionMapper()


def _get_common_exceptions_path():
    """
    Get the path to common exceptions module
    """
    # Try multiple possible paths
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'common', 'src', 'exceptions'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'common', 'src', 'exceptions'),
        os.path.join(os.path.dirname(__file__), '..', '..', '..', 'common', 'src', 'exceptions'),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def configure_service_exceptions():
    """
    Configure exception mappings for all services

    This function registers mappings for shared exceptions only.
    Common exceptions (database, config, AWS) are handled internally
    and should not be mapped to external error codes.
    """
    common_path = _get_common_exceptions_path()
    if not common_path:
        logger.warning("Could not find common exceptions path")
        return

    # Add common path to sys.path temporarily
    if common_path not in sys.path:
        sys.path.insert(0, common_path)

    try:
        # Import shared exceptions (mapped to external error codes)
        from shared_exceptions import (
            # Authentication exceptions (shared)
            InvalidCredentialsException,
            TokenExpiredException,
            TokenInvalidException,

            # Resource exceptions (shared)
            EntityNotFoundException,
            EntityAlreadyExistsException,
            UserNotFoundException,
            OrderNotFoundException,
            AssetNotFoundException,

            # Validation exceptions (shared)
            EntityValidationException,
            UserValidationException,
            OrderValidationException,
            AssetValidationException,

            # Authorization exceptions (shared)
            AuthorizationException,
            AccessDeniedException,
            InsufficientPermissionsException,

            # Internal server exception (shared)
            InternalServerException,
        )

        # Register authentication exceptions (shared)
        exception_mapper.register_exception_mapping(InvalidCredentialsException, ErrorCode.AUTHENTICATION_FAILED)
        exception_mapper.register_exception_mapping(TokenExpiredException, ErrorCode.AUTHENTICATION_FAILED)
        exception_mapper.register_exception_mapping(TokenInvalidException, ErrorCode.AUTHENTICATION_FAILED)

        # Register authorization exceptions (shared)
        exception_mapper.register_exception_mapping(AuthorizationException, ErrorCode.ACCESS_DENIED)
        exception_mapper.register_exception_mapping(AccessDeniedException, ErrorCode.ACCESS_DENIED)
        exception_mapper.register_exception_mapping(InsufficientPermissionsException, ErrorCode.ACCESS_DENIED)

        # Register resource exceptions (shared)
        exception_mapper.register_exception_mapping(EntityNotFoundException, ErrorCode.RESOURCE_NOT_FOUND)
        exception_mapper.register_exception_mapping(UserNotFoundException, ErrorCode.RESOURCE_NOT_FOUND)
        exception_mapper.register_exception_mapping(OrderNotFoundException, ErrorCode.RESOURCE_NOT_FOUND)
        exception_mapper.register_exception_mapping(AssetNotFoundException, ErrorCode.RESOURCE_NOT_FOUND)

        exception_mapper.register_exception_mapping(EntityAlreadyExistsException, ErrorCode.RESOURCE_ALREADY_EXISTS)

        # Register validation exceptions (shared)
        exception_mapper.register_exception_mapping(EntityValidationException, ErrorCode.VALIDATION_ERROR)
        exception_mapper.register_exception_mapping(UserValidationException, ErrorCode.VALIDATION_ERROR)
        exception_mapper.register_exception_mapping(OrderValidationException, ErrorCode.VALIDATION_ERROR)
        exception_mapper.register_exception_mapping(AssetValidationException, ErrorCode.VALIDATION_ERROR)

        # Register internal server exception (shared)
        exception_mapper.register_exception_mapping(InternalServerException, ErrorCode.INTERNAL_SERVER_ERROR)

        # Common exceptions are NOT mapped - they should be handled internally
        # by each service and converted to InternalServerException

        logger.info("Shared exception mappings configured successfully")

    except ImportError as e:
        logger.warning(f"Could not import shared exceptions: {e}")
        logger.info("Using default exception mappings only")
    finally:
        # Remove the temporary path
        if common_path in sys.path:
            sys.path.remove(common_path)


def map_validation_error(exc: PydanticValidationError, instance: str, trace_id: str, **kwargs) -> ProblemDetails:
    """
    Map Pydantic validation errors to Problem Details
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return create_problem_details(
        error_code=ErrorCode.VALIDATION_ERROR,
        detail="The request contains invalid data",
        instance=instance,
        trace_id=trace_id,
        errors=errors
    )


def map_service_exception(
    exc: Exception,
    instance: Optional[str] = None,
    trace_id: Optional[str] = None,
    **kwargs
) -> ProblemDetails:
    """
    Map a service exception to Problem Details
    """
    return exception_mapper.map_exception(exc, instance, trace_id, **kwargs)