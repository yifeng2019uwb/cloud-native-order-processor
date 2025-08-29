"""
Controllers Package for Order Service
Path: services/order_service/src/controllers/__init__.py
"""

from common.shared.logging import BaseLogger, Loggers, LogActions

logger = BaseLogger(Loggers.ORDER)

# Import controllers with error handling to avoid JWT import issues during test collection
try:
    from .create_order import router as create_order_router
    logger.info(action=LogActions.REQUEST_START, message="Create order controller loaded successfully")
except ImportError as e:
    logger.warning(action=LogActions.ERROR, message=f"Create order controller not available: {e}")
    create_order_router = None

try:
    from .get_order import router as get_order_router
    logger.info(action=LogActions.REQUEST_START, message="Get order controller loaded successfully")
except ImportError as e:
    logger.warning(action=LogActions.ERROR, message=f"Get order controller not available: {e}")
    get_order_router = None

try:
    from .list_orders import router as list_orders_router
    logger.info(action=LogActions.REQUEST_START, message="List orders controller loaded successfully")
except ImportError as e:
    logger.warning(action=LogActions.ERROR, message=f"List orders controller not available: {e}")
    list_orders_router = None

try:
    from .portfolio import router as portfolio_router
    logger.info(action=LogActions.REQUEST_START, message="Portfolio controller loaded successfully")
except ImportError as e:
    logger.warning(action=LogActions.ERROR, message=f"Portfolio controller not available: {e}")
    portfolio_router = None

try:
    from .asset_balance import router as asset_balance_router
    logger.info(action=LogActions.REQUEST_START, message="Asset balance controller loaded successfully")
except ImportError as e:
    logger.warning(action=LogActions.ERROR, message=f"Asset balance controller not available: {e}")
    asset_balance_router = None

try:
    from .asset_transaction import router as asset_transaction_router
    logger.info(action=LogActions.REQUEST_START, message="Asset transaction controller loaded successfully")
except ImportError as e:
    logger.warning(action=LogActions.ERROR, message=f"Asset transaction controller not available: {e}")
    asset_transaction_router = None

try:
    from .health import router as health_router
    logger.info(action=LogActions.REQUEST_START, message="Health controller loaded successfully")
except ImportError as e:
    logger.warning(action=LogActions.ERROR, message=f"Health controller not available: {e}")
    health_router = None

__all__ = [
    "create_order_router",
    "get_order_router",
    "list_orders_router",
    "portfolio_router",
    "asset_balance_router",
    "asset_transaction_router",
    "health_router"
]