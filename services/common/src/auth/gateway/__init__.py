"""
Gateway Validation Package

This package contains gateway validation functionality for the CNOP system.
Used by services to validate incoming requests from the API gateway.
"""

from .header_validator import HeaderValidator

__all__ = [
    "HeaderValidator",
]
