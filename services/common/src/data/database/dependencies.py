"""
Database dependencies and connection management.

This module provides centralized database connection management
and dependency injection for all services.
"""


from ...shared.logging import BaseLogger, Loggers
from typing import Optional, Any
from .dynamodb_connection import get_dynamodb_manager
from .redis_connection import get_redis_manager


logger = BaseLogger(Loggers.DATABASE, log_to_file=True)

def get_user_dao():
    """Get UserDAO instance with database connection"""
    from ..dao.user import UserDAO
    return UserDAO(get_dynamodb_manager().get_connection())


def get_balance_dao():
    """Get BalanceDAO instance with database connection"""
    from ..dao.user import BalanceDAO
    return BalanceDAO(get_dynamodb_manager().get_connection())


def get_asset_dao():
    """Get AssetDAO instance with database connection"""
    from ..dao.inventory import AssetDAO
    return AssetDAO(get_dynamodb_manager().get_connection())


def get_order_dao():
    """Get OrderDAO instance with database connection"""
    from ..dao.order import OrderDAO
    return OrderDAO(get_dynamodb_manager().get_connection())


def get_asset_balance_dao():
    """Get AssetBalanceDAO instance with database connection"""
    from ..dao.asset import AssetBalanceDAO
    return AssetBalanceDAO(get_dynamodb_manager().get_connection())


def get_asset_transaction_dao():
    """Get AssetTransactionDAO instance with database connection"""
    from ..dao.asset import AssetTransactionDAO
    return AssetTransactionDAO(get_dynamodb_manager().get_connection())


def get_database_health():
    """FastAPI dependency for database health check"""
    return get_dynamodb_manager().health_check()