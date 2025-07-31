"""
Common Database Dependencies

Provides standardized database connection and DAO dependency injection
for all microservices to ensure consistent database access patterns.
"""

import logging
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status

from .dynamodb_connection import dynamodb_manager, get_dynamodb
from ..dao.user_dao import UserDAO
from ..dao.asset_dao import AssetDAO
from ..dao.order.order_dao import OrderDAO

logger = logging.getLogger(__name__)


async def get_user_dao() -> AsyncGenerator[UserDAO, None]:
    """
    Get UserDAO instance with database connection

    Returns:
        UserDAO instance
    """
    async with dynamodb_manager.get_connection() as db_connection:
        yield UserDAO(db_connection)


async def get_asset_dao() -> AsyncGenerator[AssetDAO, None]:
    """
    Get AssetDAO instance with database connection

    Returns:
        AssetDAO instance
    """
    async with dynamodb_manager.get_connection() as db_connection:
        yield AssetDAO(db_connection)


async def get_order_dao() -> AsyncGenerator[OrderDAO, None]:
    """
    Get OrderDAO instance with database connection

    Returns:
        OrderDAO instance
    """
    async with dynamodb_manager.get_connection() as db_connection:
        yield OrderDAO(db_connection)


# Health check dependency
async def get_database_health():
    """
    Get database health status

    Returns:
        bool: True if database is healthy
    """
    try:
        return await dynamodb_manager.health_check()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False