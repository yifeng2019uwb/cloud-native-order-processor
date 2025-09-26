"""
Database dependencies and connection management.

This module provides centralized database connection management
and dependency injection for all services.
"""


from ...shared.logging import BaseLogger, Loggers
from typing import Optional, Any
from .dynamodb_connection import get_dynamodb_manager
from .redis_connection import get_redis_manager
from ..dao.inventory.asset_dao import AssetDAO
from ..dao.order.order_dao import OrderDAO
from ..dao.user.user_dao import UserDAO
from ..dao.user.balance_dao import BalanceDAO
from ..dao.asset.asset_balance_dao import AssetBalanceDAO
from ..dao.asset.asset_transaction_dao import AssetTransactionDAO


logger = BaseLogger(Loggers.DATABASE, log_to_file=True)

def get_user_dao():
    """Get UserDAO instance with database connection"""
    return UserDAO(get_dynamodb_manager().get_connection())


def get_balance_dao():
    """Get BalanceDAO instance with database connection"""
    return BalanceDAO(get_dynamodb_manager().get_connection())


def get_asset_dao():
    """Get AssetDAO instance with database connection"""
    return AssetDAO(get_dynamodb_manager().get_connection())


def get_order_dao():
    """Get OrderDAO instance with database connection"""
    return OrderDAO(get_dynamodb_manager().get_connection())


def get_asset_balance_dao():
    """Get AssetBalanceDAO instance with database connection"""
    return AssetBalanceDAO(get_dynamodb_manager().get_connection())


def get_asset_transaction_dao():
    """Get AssetTransactionDAO instance with database connection"""
    return AssetTransactionDAO(get_dynamodb_manager().get_connection())


def get_database_health():
    """FastAPI dependency for database health check"""
    return get_dynamodb_manager().health_check()