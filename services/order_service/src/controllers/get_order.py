"""
Get Order Controller
Path: services/order_service/src/controllers/get_order.py

Handles order retrieval endpoint with business logic directly in controller
- GET /orders/{order_id} - Get order by ID
"""
from datetime import datetime
from typing import Union
from fastapi import APIRouter, Depends, status, Request
from api_models.order import GetOrderResponse, OrderData
from api_models.shared.common import ErrorResponse
from common.data.dao.order.order_dao import OrderDAO
from common.data.dao.user.user_dao import UserDAO
from common.exceptions.shared_exceptions import (
    CNOPOrderNotFoundException,
    CNOPInternalServerException
)
from order_exceptions.exceptions import CNOPOrderValidationException
from common.shared.logging import BaseLogger, Loggers, LogActions
from controllers.dependencies import (
    get_current_user, get_order_dao_dependency,
    get_user_dao_dependency, get_request_id_from_request
)
from validation.business_validators import validate_order_retrieval_business_rules

# Initialize our standardized logger
logger = BaseLogger(Loggers.ORDER)
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
    request: Request,
    current_user: dict = Depends(get_current_user),
    order_dao: OrderDAO = Depends(get_order_dao_dependency),
    user_dao: UserDAO = Depends(get_user_dao_dependency)
) -> GetOrderResponse:
    """
    Get order by ID with user authorization
    """
    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)

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
            logger.warning(
                action=LogActions.ACCESS_DENIED,
                message=f"Unauthorized access attempt: order_id={order_id}",
                user=current_user['username'],
                request_id=request_id
            )
            raise CNOPOrderNotFoundException(f"Order '{order_id}' not found")

        logger.info(
            action=LogActions.REQUEST_END,
            message=f"Order retrieved: order_id={order_id}",
            user=current_user['username'],
            request_id=request_id
        )

        # Create response
        order_data_response = OrderData(
            order_id=order.order_id,
            order_type=order.order_type,
            asset_id=order.asset_id,
            quantity=order.quantity,
            price=order.price,
            status=order.status,
            total_amount=order.total_amount,
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
    except CNOPOrderValidationException:
        raise
    except Exception as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Unexpected error retrieving order: order_id={order_id}, error={str(e)}",
            user=current_user['username'],
            request_id=request_id
        )
        raise CNOPInternalServerException("Service temporarily unavailable")