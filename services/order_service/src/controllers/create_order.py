"""
Create Order Controller
Path: services/order_service/src/controllers/create_order.py

Handles order creation endpoint with atomic operations using TransactionManager
- POST /orders - Create new order with balance validation and asset updates
"""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Union
from fastapi import APIRouter, Depends, status, Request

# Import API models
from api_models.order import OrderCreateRequest, OrderCreateResponse, OrderData
from api_models.shared.common import ErrorResponse

# Import common entities
from common.entities.order.enums import OrderType, OrderStatus

# Import dependencies
from controllers.dependencies import get_current_user, get_transaction_manager
from common.utils.transaction_manager import TransactionManager

# Import exceptions
from common.exceptions import (
    InsufficientBalanceException,
    DatabaseOperationException,
    LockAcquisitionException
)
from src.exceptions import (
    OrderValidationException,
    InternalServerException,
    UserValidationException
)

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
            "description": "Bad request - insufficient balance",
            "model": ErrorResponse
        },
        401: {
            "description": "Unauthorized",
            "model": ErrorResponse
        },
        409: {
            "description": "Operation is busy - try again",
            "model": ErrorResponse
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse
        },
        503: {
            "description": "Service temporarily unavailable",
            "model": ErrorResponse
        }
    }
)
async def create_order(
    order_data: OrderCreateRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
    transaction_manager: TransactionManager = Depends(get_transaction_manager)
) -> OrderCreateResponse:
    """
    Create a new order with atomic operations using TransactionManager

    Supports:
    - Market Buy: Immediate purchase with balance validation
    - Market Sell: Immediate sale with asset balance validation
    - Limit Buy/Sell: Future implementation
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
        # Calculate total amount for the order
        total_amount = Decimal('0')
        if order_data.price:
            total_amount = order_data.quantity * order_data.price
        else:
            # For market orders without price, use a placeholder price
            # In production, this would come from a real-time price feed
            placeholder_price = Decimal('50000')  # Placeholder BTC price
            total_amount = order_data.quantity * placeholder_price

        # Prepare order data for TransactionManager
        order_data_dict = {
            "asset_id": order_data.asset_id,
            "quantity": order_data.quantity,
            "price": order_data.price or placeholder_price,
            "order_type": order_data.order_type
        }

        # Execute order based on type using TransactionManager
        if order_data.order_type in [OrderType.MARKET_BUY, OrderType.LIMIT_BUY]:
            # Buy order - validate USD balance and update asset balance
            result = await transaction_manager.create_buy_order_with_balance_update(
                username=current_user["username"],
                order_data=order_data_dict,
                total_cost=total_amount
            )

            logger.info(f"Buy order executed successfully: user={current_user['username']}, "
                       f"order_id={result.data['order'].order_id}, "
                       f"asset={order_data.asset_id}, quantity={order_data.quantity}, "
                       f"total_cost={total_amount}, lock_duration={result.lock_duration}s")

        elif order_data.order_type in [OrderType.MARKET_SELL, OrderType.LIMIT_SELL]:
            # Sell order - validate asset balance and update USD balance
            result = await transaction_manager.create_sell_order_with_balance_update(
                username=current_user["username"],
                order_data=order_data_dict,
                asset_amount=total_amount
            )

            logger.info(f"Sell order executed successfully: user={current_user['username']}, "
                       f"order_id={result.data['order'].order_id}, "
                       f"asset={order_data.asset_id}, quantity={order_data.quantity}, "
                       f"asset_amount={total_amount}, lock_duration={result.lock_duration}s")

        else:
            raise OrderValidationException(f"Unsupported order type: {order_data.order_type.value}")

        # Extract order from transaction result
        created_order = result.data["order"]

        # Create response data
        order_data_response = OrderData(
            order_id=created_order.order_id,
            order_type=created_order.order_type,
            asset_id=created_order.asset_id,
            quantity=created_order.quantity,
            price=created_order.price,
            created_at=created_order.created_at
        )

        return OrderCreateResponse(
            success=True,
            message=f"{order_data.order_type.value.replace('_', ' ').title()} order created successfully",
            data=order_data_response,
            timestamp=datetime.utcnow()
        )

    except InsufficientBalanceException as e:
        logger.warning(f"Insufficient balance for order: user={current_user['username']}, "
                      f"order_type={order_data.order_type.value}, asset={order_data.asset_id}, "
                      f"quantity={order_data.quantity}, error={str(e)}")
        raise UserValidationException(str(e))

    except LockAcquisitionException as e:
        logger.warning(f"Lock acquisition failed for order: user={current_user['username']}, error={str(e)}")
        raise InternalServerException("Service temporarily unavailable - please try again")

    except DatabaseOperationException as e:
        logger.error(f"Database operation failed for order: user={current_user['username']}, error={str(e)}")
        raise InternalServerException("Service temporarily unavailable")

    except OrderValidationException as e:
        logger.warning(f"Order validation failed: user={current_user['username']}, error={str(e)}")
        raise UserValidationException(str(e))

    except Exception as e:
        logger.error(f"Unexpected error during order creation: user={current_user['username']}, "
                    f"order_type={order_data.order_type.value}, asset={order_data.asset_id}, "
                    f"quantity={order_data.quantity}, error={str(e)}", exc_info=True)
        raise InternalServerException("Service temporarily unavailable")