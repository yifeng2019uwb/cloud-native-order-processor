"""
Base Logger for structured JSON logging across microservices.

This module provides a clean, simple logging interface designed for Kubernetes deployment
with structured JSON output, request correlation, and service identification.

Responsibilities:
- Structured JSON logging with consistent format
- Request correlation with unique request IDs
- Service identification and context
- Performance tracking with duration
- Clean, K8s-focused design (no Lambda remnants)
"""

import json
import os
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, Union
from pathlib import Path


class BaseLogger:
    """
    Base logger class for structured JSON logging across microservices.

    Provides a clean, simple interface for logging with consistent format,
    request correlation, and service identification.
    """

    def __init__(self, service_name: str, log_to_file: bool = False, log_file_path: Optional[str] = None):
        """
        Initialize the base logger.

        Args:
            service_name: Name of the service using this logger
            log_to_file: Whether to write logs to files (for Promtail collection)
            log_file_path: Custom path for log files (defaults to LOG_FILE_PATH env var)
        """
        self.service_name = service_name
        self.log_to_file = log_to_file

        # Setup file logging if enabled
        if self.log_to_file:
            self._setup_file_logging(log_file_path)

    def _setup_file_logging(self, log_file_path: Optional[str] = None):
        """Setup file logging for Promtail collection."""
        # Use environment variable or default path
        base_path = log_file_path or os.getenv("LOG_FILE_PATH", "logs")
        log_dir = Path(base_path) / "services" / self.service_name
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create log file path
        self.log_file = log_dir / f"{self.service_name}.log"

        # Ensure log file exists
        self.log_file.touch(exist_ok=True)

    def _write_to_file(self, log_entry: str):
        """Write log entry to file if file logging is enabled."""
        if self.log_to_file and hasattr(self, 'log_file'):
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry + '\n')
            except Exception:
                # Fallback to console if file writing fails
                pass

    def _generate_request_id(self) -> str:
        """Generate a unique request ID for correlation."""
        return f"req-{uuid.uuid4().hex[:8]}"

    def _format_timestamp(self) -> str:
        """Format timestamp in ISO format with Z suffix."""
        return datetime.utcnow().isoformat() + "Z"

    def log(self, level: str, action: str, message: str,
            user: Optional[str] = None, duration_ms: Optional[int] = None,
            extra: Optional[Dict[str, Any]] = None, request_id: Optional[str] = None) -> None:
        """
        Log a message with structured format.

        Args:
            level: Log level (DEBUG, INFO, WARN, ERROR, CRITICAL)
            action: What action/operation is being logged
            message: Human-readable message
            user: Username if available
            duration_ms: Duration in milliseconds if available
            extra: Additional context data
            request_id: Custom request ID (auto-generated if not provided)
        """
        # Generate request ID if not provided
        if not request_id:
            request_id = self._generate_request_id()

        # Build log entry
        log_entry = {
            "timestamp": self._format_timestamp(),
            "level": level.upper(),
            "service": self.service_name,
            "request_id": request_id,
            "action": action,
            "message": message
        }

        # Add optional fields only if provided
        if user:
            log_entry["user"] = user
        if duration_ms is not None:
            log_entry["duration_ms"] = duration_ms
        if extra:
            log_entry["extra"] = extra

        # Convert to JSON string
        log_json = json.dumps(log_entry, ensure_ascii=False)

        # Output to console (stdout for K8s log collection)
        print(log_json)

        # Write to file if enabled (for Promtail collection)
        if self.log_to_file:
            self._write_to_file(log_json)

    def debug(self, action: str, message: str, **kwargs) -> None:
        """Log debug level message."""
        self.log("DEBUG", action, message, **kwargs)

    def info(self, action: str, message: str, **kwargs) -> None:
        """Log info level message."""
        self.log("INFO", action, message, **kwargs)

    def warn(self, action: str, message: str, **kwargs) -> None:
        """Log warning level message."""
        self.log("WARN", action, message, **kwargs)

    def error(self, action: str, message: str, **kwargs) -> None:
        """Log error level message."""
        self.log("ERROR", action, message, **kwargs)

    def critical(self, action: str, message: str, **kwargs) -> None:
        """Log critical level message."""
        self.log("CRITICAL", action, message, **kwargs)

    def log_request(self, method: str, path: str, status_code: int,
                   user: Optional[str] = None, duration_ms: Optional[int] = None,
                   request_id: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log HTTP request with standard format.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            status_code: HTTP status code
            user: Username if available
            duration_ms: Request duration in milliseconds
            request_id: Request ID for correlation
            extra: Additional request context
        """
        # Determine log level based on status code
        if status_code >= 500:
            level = "ERROR"
        elif status_code >= 400:
            level = "WARN"
        else:
            level = "INFO"

        # Build extra context
        request_extra = {
            "method": method,
            "path": path,
            "status": status_code
        }
        if extra:
            request_extra.update(extra)

        # Log the request
        self.log(
            level=level,
            action=f"{method.lower()}_request",
            message=f"{method} {path} - {status_code}",
            user=user,
            duration_ms=duration_ms,
            request_id=request_id,
            extra=request_extra
        )

    def log_performance(self, action: str, duration_ms: int,
                       user: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log performance metrics.

        Args:
            action: Action being measured
            duration_ms: Duration in milliseconds
            user: Username if available
            extra: Additional performance context
        """
        # Determine level based on duration
        if duration_ms > 5000:  # 5 seconds
            level = "WARN"
        elif duration_ms > 1000:  # 1 second
            level = "INFO"
        else:
            level = "DEBUG"

        self.log(
            level=level,
            action=f"{action}_performance",
            message=f"{action} completed in {duration_ms}ms",
            user=user,
            duration_ms=duration_ms,
            extra=extra
        )

    def log_security_event(self, action: str, message: str,
                          user: Optional[str] = None, ip_address: Optional[str] = None,
                          extra: Optional[Dict[str, Any]] = None) -> None:
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
            security_extra["ip_address"] = ip_address
        if extra:
            security_extra.update(extra)

        self.log(
            level="WARN" if "failed" in action.lower() or "denied" in action.lower() else "INFO",
            action=f"security_{action}",
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
