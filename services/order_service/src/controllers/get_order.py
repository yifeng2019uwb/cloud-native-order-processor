"""
Get Order Controller
Path: services/order_service/src/controllers/get_order.py

Handles order retrieval endpoint with business logic directly in controller
- GET /orders/{order_id} - Get order by ID
"""
import logging
from datetime import datetime
from typing import Union
from fastapi import APIRouter, Depends, status

# Import API models
from api_models.order import GetOrderResponse, OrderData
from api_models.shared.common import ErrorResponse

# Import dependencies
from controllers.dependencies import get_current_user, get_order_dao_dependency
from common.dao.order.order_dao import OrderDAO

# Import exceptions
from common.exceptions.shared_exceptions import OrderNotFoundException
from src.exceptions import InternalServerException

logger = logging.getLogger(__name__)
router = APIRouter(tags=["orders"])


@router.get(
    "/{order_id}",
    response_model=Union[GetOrderResponse, ErrorResponse],
    responses={
        200: {
            "description": "Order retrieved successfully",
            "model": GetOrderResponse
        },
        401: {
            "description": "Unauthorized",
            "model": ErrorResponse
        },
        404: {
            "description": "Order not found",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user),
    order_dao: OrderDAO = Depends(get_order_dao_dependency)
) -> GetOrderResponse:
    """
    Get order by ID with user authorization
    """
    try:
        # Get order from database
        order = order_dao.get_order(order_id)

        # Check if order belongs to user
        if order.user_id != current_user["user_id"]:
            logger.warning(f"Unauthorized access attempt: user_id={current_user['user_id']}, order_id={order_id}")
            raise OrderNotFoundException(f"Order '{order_id}' not found")

        logger.info(f"Order retrieved: user={current_user['username']}, order_id={order_id}")

        # Create response
        order_data_response = OrderData(
            order_id=order.order_id,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            order_price=order.order_price,
            total_amount=order.total_amount,
            created_at=order.created_at,
            expires_at=order.expires_at
        )

        return GetOrderResponse(
            success=True,
            message="Order retrieved successfully",
            data=order_data_response,
            timestamp=datetime.utcnow()
        )

    except OrderNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving order: user={current_user['username']}, order_id={order_id}, error={str(e)}", exc_info=True)
        raise InternalServerException("Service temporarily unavailable")