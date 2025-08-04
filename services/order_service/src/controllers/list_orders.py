"""
List Orders Controller
Path: services/order_service/src/controllers/list_orders.py

Handles order listing endpoint with business logic directly in controller
- GET /orders - List user orders with filters
"""
import logging
from datetime import datetime
from typing import Union, Optional
from fastapi import APIRouter, Depends, status, Query

# Import API models
from api_models.order_responses import OrderListResponse, OrderSummary, ErrorResponse

# Import common entities
from common.entities.order.enums import OrderType

# Import dependencies
from controllers.dependencies import get_current_user, get_order_dao_dependency
from common.dao.order.order_dao import OrderDAO

# Import exceptions
from src.exceptions import InternalServerException

logger = logging.getLogger(__name__)
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
async def list_orders(
    asset_id: Optional[str] = Query(None, description="Filter by asset ID"),
    order_type: Optional[OrderType] = Query(None, description="Filter by order type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip"),
    current_user: dict = Depends(get_current_user),
    order_dao: OrderDAO = Depends(get_order_dao_dependency)
) -> OrderListResponse:
    """
    List user orders with optional filters and pagination
    """
    try:
        # Get all orders for user
        orders = order_dao.get_orders_by_user(current_user["user_id"])

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

        logger.info(f"Orders listed: user={current_user['username']}, count={len(paginated_orders)}")

        # Convert to response format
        order_summaries = []
        for order in paginated_orders:
            order_summary = OrderSummary(
                order_id=order.order_id,
                order_type=order.order_type,
                asset_id=order.asset_id,
                quantity=order.quantity,
                order_price=order.order_price,
                total_amount=order.total_amount,
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
        logger.error(f"Unexpected error listing orders: user={current_user['username']}, error={str(e)}", exc_info=True)
        raise InternalServerException("Service temporarily unavailable")