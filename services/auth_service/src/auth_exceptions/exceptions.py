"""
Auth Service specific exceptions.

These exceptions are internal to the Auth Service and not exposed to clients.
"""

from typing import Optional
from common.shared.logging import BaseLogger, LoggerName, LogAction

logger = BaseLogger(LoggerName.AUTH)


class BaseInternalException(Exception):
    """
    Base exception class for Auth Service with auto-logging, debug info, and audit trail

    Automatically logs exceptions when they are created, providing rich context
    for debugging and audit purposes.
    """

    def __init__(self, message: str):
        """
        Initialize exception with message

        Args:
            message: Human-readable error message
        """
        self.message = message

        # Auto-logging: Automatically logs when exception is created
        logger.error(
            action=LogAction.ERROR,
            message=f"{self.__class__.__name__}: {self.message}"
        )

        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of the exception"""
        return f"{self.__class__.__name__}: {self.message}"

    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return f"{self.__class__.__name__}(message='{self.message}')"


class TokenExpiredException(BaseInternalException):
    """Token expired exception"""
    pass


class TokenInvalidException(BaseInternalException):
    """Token invalid/malformed exception"""
    pass
