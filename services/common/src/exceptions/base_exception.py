"""
Base exception class with auto-logging for all services
Path: services/common/src/exceptions/base_exception.py
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BaseInternalException(Exception):
    """
    Base exception class for all services with auto-logging, debug info, and audit trail

    Automatically logs exceptions when they are created, providing rich context
    for debugging and audit purposes.
    """

    def __init__(self, message: str, **context):
        """
        Initialize exception with message and context

        Args:
            message: Human-readable error message
            **context: Additional context information for debugging
        """
        self.message = message
        self.context = context or {}
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()

        # Auto-logging: Automatically logs when exception is created
        logger.error(
            f"{self.__class__.__name__}: {self.message}",
            extra={
                "error_id": self.error_id,
                "context": self.context,
                "timestamp": self.timestamp.isoformat(),
                "exception_type": self.__class__.__name__
            }
        )

        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of the exception"""
        return f"{self.__class__.__name__}: {self.message}"

    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return f"{self.__class__.__name__}(message='{self.message}', context={self.context})"

    def get_context(self) -> Dict[str, Any]:
        """Get the context information for debugging"""
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp.isoformat(),
            "exception_type": self.__class__.__name__,
            "message": self.message,
            **self.context
        }