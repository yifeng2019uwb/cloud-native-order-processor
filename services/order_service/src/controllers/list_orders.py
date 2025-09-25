"""
List Orders Controller
Path: services/order_service/src/controllers/list_orders.py

Handles order listing endpoint with business logic directly in controller
- GET /orders - List user orders with filters
"""
from datetime import datetime
from typing import Union, Optional
from fastapi import APIRouter, Depends, status, Query
from api_models.order import OrderListResponse, OrderSummary
from api_models.shared.common import ErrorResponse
from common.data.entities.order.enums import OrderType
from common.data.dao.order.order_dao import OrderDAO
from common.data.dao.inventory.asset_dao import AssetDAO
from common.data.dao.user.user_dao import UserDAO
from common.exceptions.shared_exceptions import CNOPInternalServerException
from common.shared.logging import BaseLogger, Loggers, LogActions
from controllers.dependencies import (
    get_current_user, get_order_dao_dependency,
    get_asset_dao_dependency, get_user_dao_dependency
)
from validation.business_validators import validate_order_listing_business_rules

# Initialize our standardized logger
logger = BaseLogger(Loggers.ORDER)
router = APIRouter(tags=["orders"])


@router.get(
    "/",
    response_model=Union[OrderListResponse, ErrorResponse],
    responses={
        200: {
            "description": "Orders retrieved successfully",
            "model": OrderListResponse
        },
        401: {
            "description": "Unauthorized",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
def list_orders(
    asset_id: Optional[str] = Query(None, description="Filter by asset ID"),
    order_type: Optional[OrderType] = Query(None, description="Filter by order type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip"),
    current_user: dict = Depends(get_current_user),
    order_dao: OrderDAO = Depends(get_order_dao_dependency),
    asset_dao: AssetDAO = Depends(get_asset_dao_dependency),
    user_dao: UserDAO = Depends(get_user_dao_dependency)
) -> OrderListResponse:
    """
    List user orders with optional filters and pagination
    """
    try:
        # Business validation (Layer 2)
        validate_order_listing_business_rules(
            username=current_user["username"],
            status=None,  # Not implemented yet
            asset_id=asset_id,
            asset_dao=asset_dao,
            user_dao=user_dao
        )

        # Get all orders for user
        orders = order_dao.get_orders_by_user(current_user["username"])  # Use username instead of user_id

        # Apply filters
        filtered_orders = []
        for order in orders:
            # Filter by asset_id
            if asset_id and order.asset_id != asset_id:
                continue

            # Filter by order_type
            if order_type and order.order_type != order_type:
                continue

            filtered_orders.append(order)

        # Apply pagination
        paginated_orders = filtered_orders[offset:offset + limit]

        logger.info(
            action=LogActions.REQUEST_END,
            message=f"Orders listed: count={len(paginated_orders)}",
            user=current_user['username']
        )

        # Convert to response format
        order_summaries = []
        for order in paginated_orders:
            order_summary = OrderSummary(
                order_id=order.order_id,
                order_type=order.order_type,
                asset_id=order.asset_id,
                quantity=order.quantity,
                price=order.price,
                created_at=order.created_at
            )
            order_summaries.append(order_summary)

        # Determine if there are more orders
        has_more = len(paginated_orders) == limit

        return OrderListResponse(
            success=True,
            message="Orders retrieved successfully",
            data=order_summaries,
            has_more=has_more,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Unexpected error listing orders: error={str(e)}",
            user=current_user['username']
        )
        raise CNOPInternalServerException("Service temporarily unavailable")