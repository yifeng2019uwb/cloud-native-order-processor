"""
User Service Dependencies

This module provides dependency injection functions for the User Service,
including a simplified transaction manager that only uses available DAOs.
"""

from typing import Optional
from fastapi import Header, Request, Depends
from common.data.database.dependencies import get_user_dao, get_balance_dao, get_asset_dao, get_asset_balance_dao
from common.data.dao.user.balance_dao import BalanceDAO
from common.data.dao.user.user_dao import UserDAO
from common.data.dao.asset.asset_balance_dao import AssetBalanceDAO
from common.data.dao.inventory.asset_dao import AssetDAO
from common.core.utils import TransactionManager
from common.shared.constants.request_headers import RequestHeaders, RequestHeaderDefaults

def get_request_id_from_request(request: Request) -> str:
    """
    Extract request ID from Request object headers for distributed tracing

    Args:
        request: FastAPI Request object

    Returns:
        Request ID string for correlation across services
    """
    return request.headers.get(RequestHeaders.REQUEST_ID) or RequestHeaderDefaults.REQUEST_ID_DEFAULT


def get_transaction_manager() -> TransactionManager:
    """
    Get TransactionManager instance with User Service available DAOs

    User Service only has access to user_dao and balance_dao,
    so we create a simplified TransactionManager for balance operations.
    """
    return TransactionManager(
        user_dao=get_user_dao(),
        balance_dao=get_balance_dao(),
        order_dao=None,  # Not available in User Service
        asset_dao=get_asset_dao(),  # Available for portfolio operations
        asset_balance_dao=get_asset_balance_dao(),  # Available for portfolio operations
        asset_transaction_dao=None  # Not available in User Service
    )


def get_current_user(request: Request) -> dict:
    """
    Get current user from request headers (simplified for user service)

    Args:
        request: FastAPI Request object

    Returns:
        Dictionary containing user information
    """
    # For user service, we'll extract user info from headers
    # This is a simplified version - in production you'd validate JWT tokens
    username = request.headers.get(HEADER_USER_NAME, DEFAULT_USERNAME)
    user_id = request.headers.get(HEADER_USER_ID, DEFAULT_USER_ID)
    role = request.headers.get(HEADER_USER_ROLE, DEFAULT_USER_ROLE)

    return {
        "username": username,
        "user_id": user_id,
        "role": role
    }


def get_balance_dao_dependency() -> BalanceDAO:
    """Get BalanceDAO instance for balance operations"""
    return get_balance_dao()


def get_asset_balance_dao_dependency() -> AssetBalanceDAO:
    """Get AssetBalanceDAO instance for asset balance operations"""
    return get_asset_balance_dao()


def get_user_dao_dependency() -> UserDAO:
    """Get UserDAO instance for user operations"""
    return get_user_dao()


def get_asset_dao_dependency() -> AssetDAO:
    """Get AssetDAO instance for asset operations"""
    return get_asset_dao()
