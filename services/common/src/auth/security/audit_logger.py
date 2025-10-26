"""
Audit Logger for security event tracking and logging.

This module provides centralized security event logging for audit trails,
compliance requirements, and security monitoring.

Responsibilities:
- Security event logging
- Audit trail management
- Compliance logging
- Security monitoring integration
"""

import json
from datetime import datetime
from enum import Enum
from typing import Optional

from ...shared.logging import BaseLogger, LogAction, LoggerName, LogField

# Create logger instance for security events
logger = BaseLogger(LoggerName.AUDIT, log_to_file=True)


class AuditLogger:
    """
    Centralized audit logging for security events.

    Provides structured logging for security events, audit trails,
    and compliance requirements.
    """

    def __init__(self):
        """Initialize the audit logger."""
        pass

    def log_security_event(self,
                          event_type: str,
                          username: str,
                          details: Optional[str] = None,
                          ip_address: Optional[str] = None,
                          user_agent: Optional[str] = None) -> None:
        """
        Log a security event.

        Args:
            event_type: Type of security event (use LogAction constants)
            username: Username associated with the event
            details: Optional additional event details as structured string
            ip_address: Optional IP address of the user
            user_agent: Optional user agent string
        """
        # Build extra context
        extra = {}
        if ip_address:
            extra[LogField.IP_ADDRESS] = ip_address
        if user_agent:
            extra[LogField.USER_AGENT] = user_agent
        if details:
            extra[LogField.AUDIT_REASON] = details

        # Log with appropriate level based on event type
        extra_str = json.dumps(extra) if extra else None
        if event_type in [LogAction.AUTH_SUCCESS, LogAction.SECURITY_EVENT]:
            logger.info(
                action=event_type,
                message=f"Security event: {event_type} for user {username}",
                user=username,
                extra=extra_str
            )
        elif event_type in [LogAction.AUTH_FAILED, LogAction.ACCESS_DENIED]:
            logger.warning(
                action=event_type,
                message=f"Security warning: {event_type} for user {username}",
                user=username,
                extra=extra_str
            )
        else:
            logger.info(
                action=event_type,
                message=f"Security event: {event_type} for user {username}",
                user=username,
                extra=extra_str
            )

    def log_login_success(self, username: str, ip_address: Optional[str] = None,
                         user_agent: Optional[str] = None) -> None:
        """
        Log successful login event.

        Args:
            username: Username that logged in
            ip_address: Optional IP address
            user_agent: Optional user agent string
        """
        self.log_security_event(
            LogAction.AUTH_SUCCESS,
            username,
            ip_address=ip_address,
            user_agent=user_agent
        )

    def log_login_failure(self, username: str, reason: str, ip_address: Optional[str] = None,
                         user_agent: Optional[str] = None) -> None:
        """
        Log failed login event.

        Args:
            username: Username that failed to login
            reason: Reason for login failure
            ip_address: Optional IP address
            user_agent: Optional user agent string
        """
        self.log_security_event(
            LogAction.AUTH_FAILED,
            username,
            details=f"{LogField.AUDIT_REASON}={reason}",
            ip_address=ip_address,
            user_agent=user_agent
        )

    def log_logout(self, username: str, ip_address: Optional[str] = None) -> None:
        """
        Log logout event.

        Args:
            username: Username that logged out
            ip_address: Optional IP address
        """
        self.log_security_event(
            LogAction.SECURITY_EVENT,  # Use our defined constant
            username,
            ip_address=ip_address
        )

    def log_password_change(self, username: str, ip_address: Optional[str] = None) -> None:
        """
        Log password change event.

        Args:
            username: Username that changed password
            ip_address: Optional IP address
        """
        self.log_security_event(
            LogAction.SECURITY_EVENT,  # Use our defined constant
            username,
            ip_address=ip_address
        )

    def log_token_created(self, username: str, token_type: str, ip_address: Optional[str] = None) -> None:
        """
        Log token creation event.

        Args:
            username: Username for whom token was created
            token_type: Type of token created
            ip_address: Optional IP address
        """
        self.log_security_event(
            LogAction.SECURITY_EVENT,
            username,
            details=f"{LogField.TOKEN_TYPE}={token_type}",
            ip_address=ip_address
        )

    def log_access_denied(self, username: str, resource: str, reason: str,
                         ip_address: Optional[str] = None) -> None:
        """
        Log access denied event.

        Args:
            username: Username that was denied access
            resource: Resource access was denied to
            reason: Reason for access denial
            ip_address: Optional IP address
        """
        self.log_security_event(
            LogAction.ACCESS_DENIED,  # Use our defined constant
            username,
            details=f"{LogField.RESOURCE}={resource}|{LogField.AUDIT_REASON}={reason}",
            ip_address=ip_address
        )