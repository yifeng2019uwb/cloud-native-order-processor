"""
Dependencies for Order Service controllers
Path: services/order_service/src/controllers/dependencies.py

Provides dependency injection for:
- Database connections
- Service instances
- Authentication
- Authorization
"""
import logging
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Import common package dependencies
from common.database import get_order_dao, get_balance_dao, get_asset_dao, get_user_dao
from common.database.dynamodb_connection import dynamodb_manager
from common.dao.order.order_dao import OrderDAO
from common.dao.user import UserDAO, BalanceDAO
from common.dao.inventory import AssetDAO
from common.dao.asset import AssetBalanceDAO, AssetTransactionDAO
from common.utils.transaction_manager import TransactionManager

# Import JWT utilities
from common.security import TokenManager

logger = logging.getLogger(__name__)

# Security scheme for JWT tokens
security = HTTPBearer(auto_error=False)

# Initialize TokenManager
token_manager = TokenManager()


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


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    Get current user from JWT token

    This is a simplified version - in production, you'd want to:
    - Validate token signature
    - Check token expiration
    - Verify user exists in database
    - Return proper user entity
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    try:
        # Verify and decode JWT token
        token_data = token_manager.verify_access_token(credentials.credentials)

        # Extract user information from token
        user_info = {
            "user_id": token_data.get("sub"),  # Subject (user ID)
            "username": token_data.get("username"),
            "role": token_data.get("role", "customer")
        }

        logger.info(f"User authenticated: {user_info['username']}")
        return user_info

    except Exception as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
