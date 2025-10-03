"""
Centralized Request Headers for all services
"""
from enum import Enum


class RequestHeaders(str, Enum):
    """Request headers used across all services - standardized from Gateway"""

    # Standard HTTP headers
    CONTENT_TYPE = "Content-Type"
    AUTHORIZATION = "Authorization"
    USER_AGENT = "User-Agent"

    # Custom headers from Gateway
    REQUEST_ID = "X-Request-ID"
    USER_NAME = "X-User-Name"
    USER_ID = "X-User-ID"
    USER_ROLE = "X-User-Role"
    AUTHENTICATED = "X-Authenticated"
    SOURCE = "X-Source"
    AUTH_SERVICE = "X-Auth-Service"
    SESSION_ID = "X-Session-ID"


class RequestHeaderDefaults:
    """Default values for request headers when not provided"""

    # Header default values
    REQUEST_ID_DEFAULT = "no-request-id"
    USERNAME_DEFAULT = "testuser"
    USER_ID_DEFAULT = "1"
    USER_ROLE_DEFAULT = "customer"
    USER_AGENT_DEFAULT = "unknown"
