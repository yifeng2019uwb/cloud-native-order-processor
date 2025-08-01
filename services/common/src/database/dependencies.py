"""
Common Database Dependencies

Provides optimized database connection and DAO dependency injection
for all microservices to ensure consistent database access patterns.
"""

import logging
from fastapi import Depends, HTTPException, status

from .dynamodb_connection import dynamodb_manager
from ..dao.user import UserDAO, BalanceDAO
from ..dao.inventory import AssetDAO
from ..dao.order import OrderDAO
from ..utils.transaction_manager import SimpleTransactionManager

logger = logging.getLogger(__name__)


def get_user_dao() -> UserDAO:
    """Get UserDAO instance with database connection"""
    return UserDAO(dynamodb_manager.get_connection())


def get_balance_dao() -> BalanceDAO:
    """Get BalanceDAO instance with database connection"""
    return BalanceDAO(dynamodb_manager.get_connection())


def get_asset_dao() -> AssetDAO:
    """Get AssetDAO instance with database connection"""
    return AssetDAO(dynamodb_manager.get_connection())


def get_order_dao() -> OrderDAO:
    """Get OrderDAO instance with database connection"""
    return OrderDAO(dynamodb_manager.get_connection())


def get_transaction_manager() -> SimpleTransactionManager:
    """Get SimpleTransactionManager instance with all required DAOs"""
    return SimpleTransactionManager(
        user_dao=get_user_dao(),
        balance_dao=get_balance_dao(),
        order_dao=get_order_dao(),
        asset_dao=get_asset_dao()
    )


def get_database_health():
    """FastAPI dependency for database health check"""
    return dynamodb_manager.health_check()