"""
DEPRECATED: Use api_constants.py instead

This file is kept for backward compatibility only.
All HTTP status codes have been moved to api_constants.py

Recommended import:
    from common.shared.constants.api_constants import HTTPStatus
"""
from .api_constants import HTTPStatus

__all__ = ['HTTPStatus']
