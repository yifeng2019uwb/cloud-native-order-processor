"""
Create Order Controller
Path: services/order_service/src/controllers/create_order.py

Handles order creation endpoint with business logic directly in controller
- POST /orders - Create new order
"""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from typing import Union
from fastapi import APIRouter, Depends, status, Request

# Import API models
from api_models.order import OrderCreateRequest, OrderCreateResponse, OrderData
from api_models.shared.common import ErrorResponse

# Import common entities
from common.entities.order import OrderCreate
from common.entities.order.enums import OrderType, OrderStatus

# Import dependencies
from controllers.dependencies import get_current_user, get_order_dao_dependency
from common.dao.order.order_dao import OrderDAO

# Import exceptions
from src.exceptions import OrderValidationException, InternalServerException

logger = logging.getLogger(__name__)
router = APIRouter(tags=["orders"])


@router.post(
    "/",
    response_model=Union[OrderCreateResponse, ErrorResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Order created successfully",
            "model": OrderCreateResponse
        },
        400: {
            "description": "Bad request - invalid data",
            "model": ErrorResponse
        },
        401: {
            "description": "Unauthorized",
            "model": ErrorResponse
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def create_order(
    order_data: OrderCreateRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
    order_dao: OrderDAO = Depends(get_order_dao_dependency)
) -> OrderCreateResponse:
    """
    Create a new order with business logic directly in controller
    """
    # Log order creation attempt
    logger.info(
        f"Order creation attempt from {request.client.host if request.client else 'unknown'}",
        extra={
            "username": current_user["username"],
            "order_type": order_data.order_type.value,
            "asset_id": order_data.asset_id,
            "quantity": str(order_data.quantity),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Generate order ID
        order_id = f"ord_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:12]}"

        # Calculate total amount
        total_amount = Decimal('0')
        if order_data.order_price:
            total_amount = order_data.quantity * order_data.order_price
        else:
            # For market orders, use a placeholder price
            placeholder_price = Decimal('50000')  # Placeholder BTC price
            total_amount = order_data.quantity * placeholder_price

        # Create order entity
        order_create = OrderCreate(
            order_id=order_id,
            user_id=current_user["user_id"],
            asset_id=order_data.asset_id,
            order_type=order_data.order_type,
            quantity=order_data.quantity,
            order_price=order_data.order_price,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
            expires_at=order_data.expires_at
        )

        # Save to database
        order = order_dao.create_order(order_create)

        logger.info(f"Order created successfully: user={current_user['username']}, order_id={order_id}")

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

        return OrderCreateResponse(
            success=True,
            message="Order created successfully",
            data=order_data_response,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Unexpected error during order creation: user={current_user['username']}, error={str(e)}", exc_info=True)
        raise InternalServerException("Service temporarily unavailable")