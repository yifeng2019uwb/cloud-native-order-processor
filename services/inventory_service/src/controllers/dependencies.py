"""
Dependencies for Inventory Service controllers
Path: services/inventory_service/src/controllers/dependencies.py

Provides dependency injection for:
- Database connections
- Service instances
- No authentication required (public APIs)
"""
from typing import Optional
from fastapi import Depends

from common.data.database.dependencies import get_asset_dao
from common.data.dao.inventory import AssetDAO

from common.shared.logging import BaseLogger, Loggers, LogActions

logger = BaseLogger(Loggers.INVENTORY)


def get_asset_dao_dependency() -> AssetDAO:
    """Get AssetDAO instance"""
    return get_asset_dao()


# Assets are public APIs accessible without user authentication
