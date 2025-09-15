"""
Database dependencies and connection management.

This module provides centralized database connection management
and dependency injection for all services.
"""


from ...shared.logging import BaseLogger, Loggers
from typing import Optional
from .dynamodb_connection import dynamodb_manager
from .redis_connection import get_redis_manager
from ..dao.user import UserDAO, BalanceDAO
from ..dao.inventory import AssetDAO
from ..dao.order import OrderDAO
from ..dao.asset import AssetBalanceDAO, AssetTransactionDAO

logger = BaseLogger(Loggers.DATABASE, log_to_file=True)


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


def get_asset_balance_dao() -> AssetBalanceDAO:
    """Get AssetBalanceDAO instance with database connection"""
    return AssetBalanceDAO(dynamodb_manager.get_connection())


def get_asset_transaction_dao() -> AssetTransactionDAO:
    """Get AssetTransactionDAO instance with database connection"""
    return AssetTransactionDAO(dynamodb_manager.get_connection())


def get_database_health():
    """FastAPI dependency for database health check"""
    return dynamodb_manager.health_check()