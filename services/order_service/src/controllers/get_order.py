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
from controllers.dependencies import (
    get_current_user, get_order_dao_dependency,
    get_user_dao_dependency
)
from common.data.dao.order.order_dao import OrderDAO
from common.data.dao.user import UserDAO

# Import exceptions
from common.exceptions.shared_exceptions import (
    CNOPOrderNotFoundException,
    CNOPInternalServerException
)

# Import business validators
from validation.business_validators import validate_order_retrieval_business_rules

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
def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user),
    order_dao: OrderDAO = Depends(get_order_dao_dependency),
    user_dao: UserDAO = Depends(get_user_dao_dependency)
) -> GetOrderResponse:
    """
    Get order by ID with user authorization
    """
    try:
        # Business validation (Layer 2)
        validate_order_retrieval_business_rules(
            order_id=order_id,
            username=current_user["username"],
            order_dao=order_dao,
            user_dao=user_dao
        )

        # Get order from database
        order = order_dao.get_order(order_id)

        # Check if order belongs to user
        if order.username != current_user["username"]:
            logger.warning(f"Unauthorized access attempt: username={current_user['username']}, order_id={order_id}")
            raise CNOPOrderNotFoundException(f"Order '{order_id}' not found")

        logger.info(f"Order retrieved: user={current_user['username']}, order_id={order_id}")

        # Create response
        order_data_response = OrderData(
            order_id=order.order_id,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            price=order.price,
            created_at=order.created_at
        )

        return GetOrderResponse(
            success=True,
            message="Order retrieved successfully",
            data=order_data_response,
            timestamp=datetime.utcnow()
        )

    except CNOPOrderNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving order: user={current_user['username']}, order_id={order_id}, error={str(e)}", exc_info=True)
        raise CNOPInternalServerException("Service temporarily unavailable")