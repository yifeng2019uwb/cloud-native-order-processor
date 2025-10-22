"""
DEPRECATED: Use api_constants.py instead

This file is kept for backward compatibility only.
All API response constants have been moved to api_constants.py

Recommended import:
    from common.shared.constants.api_constants import APIResponseDescriptions, APIResponseKeys
"""
from .api_constants import APIResponseDescriptions, APIResponseKeys

__all__ = ['APIResponseDescriptions', 'APIResponseKeys']
