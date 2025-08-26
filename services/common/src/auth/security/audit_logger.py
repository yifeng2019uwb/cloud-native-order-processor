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

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SecurityEventType(Enum):
    """Enumeration of security event types."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    TOKEN_CREATED = "token_created"
    TOKEN_REVOKED = "token_revoked"
    ACCESS_DENIED = "access_denied"


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
                          event_type: SecurityEventType,
                          username: str,
                          details: Optional[Dict[str, Any]] = None,
                          ip_address: Optional[str] = None,
                          user_agent: Optional[str] = None) -> None:
        """
        Log a security event.

        Args:
            event_type: Type of security event
            username: Username associated with the event
            details: Optional additional event details
            ip_address: Optional IP address of the user
            user_agent: Optional user agent string
        """
        # Create audit log message
        message = f"SECURITY_AUDIT: {event_type.value} - User: {username}"

        if ip_address:
            message += f" - IP: {ip_address}"

        if details:
            message += f" - Details: {details}"

        # Log with appropriate level based on event type
        if event_type in [SecurityEventType.LOGIN_SUCCESS, SecurityEventType.TOKEN_CREATED]:
            logger.info(message)
        elif event_type in [SecurityEventType.LOGIN_FAILURE, SecurityEventType.ACCESS_DENIED]:
            logger.warning(message)
        else:
            logger.info(message)

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
            SecurityEventType.LOGIN_SUCCESS,
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
            SecurityEventType.LOGIN_FAILURE,
            username,
            details={"reason": reason},
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
            SecurityEventType.LOGOUT,
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
            SecurityEventType.PASSWORD_CHANGE,
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
            SecurityEventType.TOKEN_CREATED,
            username,
            details={"token_type": token_type},
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
            SecurityEventType.ACCESS_DENIED,
            username,
            details={"resource": resource, "reason": reason},
            ip_address=ip_address
        )