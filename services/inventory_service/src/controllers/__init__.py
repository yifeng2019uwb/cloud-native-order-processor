"""
Controllers package for inventory service
"""

# Import routers
from .assets import router as assets_router
from .health import router as health_router

__all__ = [
    "assets_router",
    "health_router"
]