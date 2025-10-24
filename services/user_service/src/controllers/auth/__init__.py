"""
Authentication routes package
Path: cloud-native-order-processor/services/user-service/src/routes/auth/__init__.py
"""

from fastapi import APIRouter
from common.shared.logging import BaseLogger, LogAction, LoggerName

logger = BaseLogger(LoggerName.USER)

# Create main auth router that combines all auth-related endpoints
router = APIRouter(prefix="/auth", tags=["authentication"])

# Import and include individual route modules
try:
    from .register import router as register_router
    router.include_router(register_router)
    logger.info(action=LogAction.REQUEST_START, message="Registration router included successfully")
except ImportError as e:
    logger.warning(action=LogAction.ERROR, message=f"Could not include registration router: {e}")

# Future: Import other auth routers (login, logout, profile)
try:
    from .login import router as login_router
    router.include_router(login_router)
except ImportError:
    pass

try:
    from .profile import router as profile_router
    router.include_router(profile_router)
except ImportError:
    pass

__all__ = ["router"]