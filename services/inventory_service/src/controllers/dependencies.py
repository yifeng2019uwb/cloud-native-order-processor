"""
Dependencies for Inventory Service controllers
Path: services/inventory_service/src/controllers/dependencies.py

Provides dependency injection for:
- Database connections
- Service instances
- No authentication required (public APIs)
"""
from fastapi import Request

from common.data.database.dependencies import get_asset_dao
from common.data.dao.inventory.asset_dao import AssetDAO

from common.shared.logging import BaseLogger, Loggers
from common.shared.constants.api_constants import RequestHeaders, RequestHeaderDefaults


logger = BaseLogger(Loggers.INVENTORY)


def get_request_id_from_request(request: Request) -> str:
    """
    Extract request ID from Request object headers for distributed tracing

    Args:
        request: FastAPI Request object

    Returns:
        Request ID string for correlation across services
    """
    return request.headers.get(RequestHeaders.REQUEST_ID) or RequestHeaderDefaults.REQUEST_ID_DEFAULT


def get_asset_dao_dependency() -> AssetDAO:
    """Get AssetDAO instance"""
    return get_asset_dao()


# Assets are public APIs accessible without user authentication
