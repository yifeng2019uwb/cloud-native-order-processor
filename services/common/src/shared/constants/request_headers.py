"""
DEPRECATED: Use api_constants.py instead

This file is kept for backward compatibility only.
All request header constants have been moved to api_constants.py

Recommended import:
    from common.shared.constants.api_constants import RequestHeaders, RequestHeaderDefaults, ExtractedUserFields
"""
from .api_constants import RequestHeaders, RequestHeaderDefaults, ExtractedUserFields

__all__ = ['RequestHeaders', 'RequestHeaderDefaults', 'ExtractedUserFields']
