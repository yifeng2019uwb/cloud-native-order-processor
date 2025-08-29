"""
Dependencies for Order Service controllers
Path: services/order_service/src/controllers/dependencies.py

Provides dependency injection for:
- Database connections
- Service instances
- Gateway Authentication
- Authorization
"""
from decimal import Decimal
from typing import Optional
from fastapi import HTTPException, status, Request, Header
from common.data.database import get_order_dao, get_balance_dao, get_asset_dao, get_user_dao
from common.data.database.dynamodb_connection import dynamodb_manager
from common.data.dao.order.order_dao import OrderDAO
from common.data.dao.user import UserDAO, BalanceDAO
from common.data.dao.inventory import AssetDAO
from common.data.dao.asset import AssetBalanceDAO, AssetTransactionDAO
from common.core.utils.transaction_manager import TransactionManager
from common.shared.logging import BaseLogger, Loggers, LogActions

# Initialize our standardized logger
logger = BaseLogger(Loggers.ORDER)


def get_order_dao_dependency() -> OrderDAO:
    """Get OrderDAO instance"""
    return get_order_dao()


def get_user_dao_dependency() -> UserDAO:
    """Get UserDAO instance for user operations"""
    return get_user_dao()


def get_balance_dao_dependency() -> BalanceDAO:
    """Get BalanceDAO instance for USD balance operations"""
    return get_balance_dao()


def get_asset_dao_dependency() -> AssetDAO:
    """Get AssetDAO instance for asset validation"""
    return get_asset_dao()


def get_asset_balance_dao_dependency() -> AssetBalanceDAO:
    """Get AssetBalanceDAO instance for asset balance operations"""
    return AssetBalanceDAO(dynamodb_manager.get_connection())


def get_asset_transaction_dao_dependency() -> AssetTransactionDAO:
    """Get AssetTransactionDAO instance for asset transaction operations"""
    return AssetTransactionDAO(dynamodb_manager.get_connection())


def get_transaction_manager() -> TransactionManager:
    """
    Get TransactionManager instance with all required DAOs for atomic operations

    Returns:
        TransactionManager: Configured with all required DAOs for order and balance operations
    """
    return TransactionManager(
        user_dao=get_user_dao_dependency(),
        balance_dao=get_balance_dao_dependency(),
        order_dao=get_order_dao_dependency(),
        asset_dao=get_asset_dao_dependency(),
        asset_balance_dao=get_asset_balance_dao_dependency(),
        asset_transaction_dao=get_asset_transaction_dao_dependency()
    )


def get_current_user(
    request: Request,
    x_source: Optional[str] = Header(None, alias="X-Source"),
    x_auth_service: Optional[str] = Header(None, alias="X-Auth-Service"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
) -> dict:
    """
    Get current user from Gateway headers (replaces JWT validation)

    This validates that requests come from the Gateway and extracts user context
    """
    # Validate source headers
    if not x_source or x_source != "gateway":
        logger.warning(action=LogActions.ACCESS_DENIED, message=f"Invalid source header: {x_source}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid request source"
        )

    if not x_auth_service or x_auth_service != "auth-service":
        logger.warning(action=LogActions.ACCESS_DENIED, message=f"Invalid auth service header: {x_auth_service}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication service"
        )

    # Extract user information from headers
    if not x_user_id:
        logger.warning(action=LogActions.ACCESS_DENIED, message="Missing user ID header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )

    # Create user info with username as primary identifier
    user_info = {
        "username": x_user_id,
        "role": x_user_role or "customer"  # Default role if not provided
    }

    logger.info(action=LogActions.AUTH_SUCCESS, message=f"User authenticated via Gateway: {x_user_id}")
    return user_info


def get_current_market_price(asset_id: str, asset_dao: AssetDAO) -> Decimal:
    """
    Get current market price for an asset using AssetDAO

    Args:
        asset_id: Asset ID (e.g., 'BTC', 'ETH', 'XRP')
        asset_dao: Asset DAO instance

    Returns:
        Current market price as Decimal
    """
    asset = asset_dao.get_asset_by_id(asset_id)
    return Decimal(str(asset.price_usd))
