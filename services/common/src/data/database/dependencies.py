"""
Database dependencies and connection management.

This module provides centralized database connection management
and dependency injection for all services.
"""


from typing import Any, Optional

from ...shared.logging import BaseLogger, Loggers
from ..dao.asset.asset_balance_dao import AssetBalanceDAO
from ..dao.asset.asset_transaction_dao import AssetTransactionDAO
from ..dao.inventory.asset_dao import AssetDAO
from ..dao.order.order_dao import OrderDAO
from ..dao.user.balance_dao import BalanceDAO
from ..dao.user.user_dao import UserDAO
from .dynamodb_connection import get_dynamodb_manager
from .redis_connection import get_redis_manager

logger = BaseLogger(Loggers.DATABASE, log_to_file=True)

def get_user_dao():
    """Get UserDAO instance with database connection"""
    return UserDAO()


def get_balance_dao():
    """Get BalanceDAO instance with database connection"""
    return BalanceDAO()


def get_asset_dao():
    """Get AssetDAO instance (PynamoDB doesn't need db_connection)"""
    return AssetDAO()


def get_order_dao():
    """Get OrderDAO instance (PynamoDB doesn't need db_connection)"""
    return OrderDAO()


def get_asset_balance_dao():
    """Get AssetBalanceDAO instance (PynamoDB doesn't need db_connection)"""
    return AssetBalanceDAO()


def get_asset_transaction_dao():
    """Get AssetTransactionDAO instance with database connection"""
    return AssetTransactionDAO()


def get_database_health():
    """FastAPI dependency for database health check"""
    return get_dynamodb_manager().health_check()