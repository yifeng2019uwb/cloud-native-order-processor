"""
Base Logger for structured JSON logging across microservices.

This module provides a clean, simple logging interface designed for Kubernetes deployment
with structured JSON output, request correlation, and service identification.

Responsibilities:
- Structured JSON logging with consistent format
- Request correlation with unique request IDs
- Service identification and context
- Clean, K8s-focused design (no Lambda remnants)
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

from .log_constants import LogLevel, LogField, LogDefault
from ...auth.security.jwt_constants import RequestDefaults


class LogEntry(BaseModel):
    """Model for structured log entry"""

    timestamp: str = Field(..., description="ISO timestamp")
    level: LogLevel = Field(..., description="Log level")
    service: str = Field(..., description="Service name")
    request_id: str = Field(..., description="Request ID")
    action: str = Field(..., description="Action being logged")
    message: str = Field(..., description="Log message")
    user: str = Field(..., description="Username or service name")
    extra: Optional[str] = Field(None, description="Additional context")


class BaseLogger:
    """
    Base logger class for structured JSON logging across microservices.

    Provides a clean, simple interface for logging with consistent format,
    request correlation, and service identification.
    """

    def __init__(self, service_name: str, log_to_file: bool = True, log_file_path: Optional[str] = None):
        """
        Initialize the base logger.

        Args:
            service_name: Name of the service using this logger
            log_to_file: Whether to write logs to files (default: True, for Promtail collection)
            log_file_path: Custom path for log files (defaults to LOG_FILE_PATH env var)
        """
        self.service_name = service_name
        self.log_to_file = log_to_file
        # stdout if: prod (K8s) OR LOG_TO_STDOUT=1 (local/dev override for Loki without changing ENVIRONMENT)
        env_val = os.getenv(LogDefault.ENVIRONMENT_VAR, "").strip().lower()
        log_stdout = os.getenv(LogDefault.LOG_TO_STDOUT_ENV, "").strip().lower() in ("1", "true", "yes")
        self._use_stdout = (env_val == LogDefault.PRODUCTION_ENV.lower()) or log_stdout

        # Setup file logging only when using file (Docker: file for Promtail)
        if not self._use_stdout and self.log_to_file:
            self._setup_file_logging(log_file_path)

    def _setup_file_logging(self, log_file_path: Optional[str] = None):
        """Setup file logging for Promtail collection."""
        # Use environment variable or default path
        base_path = log_file_path or os.getenv(LogDefault.LOG_FILE_PATH_ENV, LogDefault.LOG_FILE_PATH)
        log_dir = Path(base_path) / LogDefault.SERVICES_DIR / self.service_name
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # If we can't create the directory, fall back to /tmp
            log_dir = Path(LogDefault.TMP_PATH) / LogDefault.LOG_FILE_PATH / LogDefault.SERVICES_DIR / self.service_name
            log_dir.mkdir(parents=True, exist_ok=True)

        # Create log file path
        self.log_file = log_dir / f"{self.service_name}{LogDefault.LOG_FILE_EXTENSION}"

        # Ensure log file exists
        self.log_file.touch(exist_ok=True)

    def _write_to_file(self, log_entry: str):
        """Write log entry to file if file logging is enabled."""
        if self.log_to_file and hasattr(self, LogDefault.LOG_FILE_ATTR):
            with open(self.log_file, LogDefault.FILE_APPEND_MODE, encoding=LogDefault.FILE_ENCODING) as f:
                f.write(log_entry + LogDefault.NEWLINE)

    def _generate_request_id(self) -> str:
        """Generate a unique request ID for correlation using common constants."""
        return f"{RequestDefaults.REQUEST_ID_PREFIX}{uuid.uuid4().hex[:LogDefault.UUID_HEX_LENGTH]}"

    def _format_timestamp(self) -> str:
        """Format timestamp in ISO format with Z suffix."""
        return datetime.now(timezone.utc).isoformat() + LogDefault.TIMESTAMP_SUFFIX

    def log(self, level: str, action: str, message: str, user: Optional[str] = None,
            extra: Optional[str] = None, request_id: Optional[str] = None) -> None:
        """
        Log a message with structured format.

        Args:
            level: Log level (DEBUG, INFO, WARN, ERROR, CRITICAL)
            action: What action/operation is being logged
            message: Human-readable message
            user: Username if available
            extra: Additional context data
            request_id: Custom request ID (auto-generated if not provided)
        """
        # Generate request ID if not provided
        if not request_id:
            request_id = self._generate_request_id()

        # Build log entry using Pydantic model
        log_entry = LogEntry(
            timestamp=self._format_timestamp(),
            level=level,
            service=self.service_name,
            request_id=request_id,
            action=action,
            message=message,
            user=user or self.service_name,  # Use service name as default user
            extra=extra
        )

        # Convert to JSON string
        log_json = log_entry.model_dump_json()

        # Always emit to stdout so Loki/Promtail see backend logs (Docker collects stdout)
        try:
            print(log_json, file=sys.stdout, flush=True)
        except OSError:
            pass

        # When not prod (local/dev): also write to file
        if not self._use_stdout and self.log_to_file and hasattr(self, LogDefault.LOG_FILE_ATTR):
            try:
                self._write_to_file(log_json)
            except OSError:
                pass

    def debug(self, action: str, message: str, **kwargs) -> None:
        """Log debug level message."""
        self.log(LogLevel.DEBUG, action, message, **kwargs)

    def info(self, action: str, message: str, **kwargs) -> None:
        """Log info level message."""
        self.log(LogLevel.INFO, action, message, **kwargs)

    def warning(self, action: str, message: str, **kwargs) -> None:
        """Log warning level message."""
        self.log(LogLevel.WARN, action, message, **kwargs)

    def error(self, action: str, message: str, **kwargs) -> None:
        """Log error level message."""
        self.log(LogLevel.ERROR, action, message, **kwargs)

    def critical(self, action: str, message: str, **kwargs) -> None:
        """Log critical level message."""
        self.log(LogLevel.CRITICAL, action, message, **kwargs)


    def log_security_event(self, action: str, message: str,
                          user: Optional[str] = None, ip_address: Optional[str] = None,
                          extra: Optional[str] = None) -> None:
        """
        Log security-related events.

        Args:
            action: Security action (login, logout, access_denied, etc.)
            message: Security event description
            user: Username if available
            ip_address: IP address if available
            extra: Additional security context
        """
        security_extra = {}
        if ip_address:
            security_extra[LogField.IP_ADDRESS] = ip_address
        if extra:
            security_extra.update(extra)

        self.log(
            level=LogLevel.WARN if LogDefault.FAILED_KEYWORD in action.lower() or LogDefault.DENIED_KEYWORD in action.lower() else LogLevel.INFO,
            action=f"{LogDefault.SECURITY_ACTION_PREFIX}{action}",
            message=message,
            user=user,
            extra=security_extra
        )


# Convenience function to create logger instances
def create_logger(service_name: str, **kwargs) -> BaseLogger:
    """
    Create a logger instance for a service.

    Args:
        service_name: Name of the service
        **kwargs: Additional arguments for BaseLogger

    Returns:
        BaseLogger instance configured for the service
    """
    return BaseLogger(service_name, **kwargs)
