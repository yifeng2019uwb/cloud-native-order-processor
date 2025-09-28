"""
Dependencies for Inventory Service controllers
Path: services/inventory_service/src/controllers/dependencies.py

Provides dependency injection for:
- Database connections
- Service instances
- No authentication required (public APIs)
"""
from typing import Optional
from fastapi import Depends, Header

from common.data.database.dependencies import get_asset_dao
from common.data.dao.inventory.asset_dao import AssetDAO

from common.shared.logging import BaseLogger, Loggers, LogActions

logger = BaseLogger(Loggers.INVENTORY)


def get_request_id(
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID")
) -> str:
    """
    Extract request ID from Gateway headers for distributed tracing

    Returns:
        Request ID string for correlation across services
    """
    return x_request_id or "no-request-id"


def get_asset_dao_dependency() -> AssetDAO:
    """Get AssetDAO instance"""
    return get_asset_dao()


# Assets are public APIs accessible without user authentication
