"""
Centralized HTTP Status Codes for all services
"""
from enum import IntEnum


class HTTPStatus(IntEnum):
    """HTTP Status Codes - Only what we actually use in the codebase"""

    # Success responses
    OK = 200
    CREATED = 201

    # Client error responses
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422

    # Server error responses
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503
