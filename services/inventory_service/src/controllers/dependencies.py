"""
Dependencies for Inventory Service controllers
Path: services/inventory_service/src/controllers/dependencies.py

Provides dependency injection for:
- Database connections
- Service instances
- No authentication required (public APIs)
"""
import logging
from typing import Optional
from fastapi import Depends

# Import common package dependencies
from common.data.database import get_asset_dao
from common.data.dao.inventory import AssetDAO

logger = logging.getLogger(__name__)


def get_asset_dao_dependency() -> AssetDAO:
    """Get AssetDAO instance"""
    return get_asset_dao()


# Note: No authentication required for inventory service
# Assets are public APIs accessible without user authentication
