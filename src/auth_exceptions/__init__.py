"""
Auth Service exceptions package.

This package contains all exception classes used by the Auth Service.
"""

from .exceptions import (
    BaseInternalException,
    TokenExpiredException,
    TokenInvalidException
)

__all__ = [
    'BaseInternalException',
    'TokenExpiredException',
    'TokenInvalidException'
]
