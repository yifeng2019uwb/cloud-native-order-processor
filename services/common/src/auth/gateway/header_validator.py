"""
Request utilities for common operations

This module provides common request utility functions used across services.
"""

from fastapi import Request

from ...shared.constants.api_constants import RequestHeaders, RequestHeaderDefaults


def get_request_id_from_request(request: Request) -> str:
    """
    Extract request ID from Request object headers for distributed tracing

    Args:
        request: FastAPI Request object

    Returns:
        Request ID string for correlation across services
    """
    return request.headers.get(RequestHeaders.REQUEST_ID) or RequestHeaderDefaults.REQUEST_ID_DEFAULT
