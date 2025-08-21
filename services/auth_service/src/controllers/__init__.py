"""
Controllers Package

API endpoint handlers for Auth Service.
"""

from .health import router as health_router
from .validate import router as validate_router

__all__ = [
    "health_router",
    "validate_router",
]
