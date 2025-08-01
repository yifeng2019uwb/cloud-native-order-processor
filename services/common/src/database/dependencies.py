"""
Common Database Dependencies

Provides optimized database connection and DAO dependency injection
for all microservices to ensure consistent database access patterns.
"""

import logging
from fastapi import Depends, HTTPException, status

from .dynamodb_connection import dynamodb_manager
from ..dao.user_dao import UserDAO
from ..dao.asset_dao import AssetDAO
from ..dao.order.order_dao import OrderDAO

logger = logging.getLogger(__name__)


def get_user_dao() -> UserDAO:
    """Get UserDAO instance with database connection"""
    return UserDAO(dynamodb_manager.get_connection())


def get_asset_dao() -> AssetDAO:
    """Get AssetDAO instance with database connection"""
    return AssetDAO(dynamodb_manager.get_connection())


def get_order_dao() -> OrderDAO:
    """Get OrderDAO instance with database connection"""
    return OrderDAO(dynamodb_manager.get_connection())


def get_database_health():
    """FastAPI dependency for database health check"""
    return dynamodb_manager.health_check()