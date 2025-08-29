"""
Create Order Controller
Path: services/order_service/src/controllers/create_order.py

Handles order creation endpoint with atomic operations using TransactionManager
- POST /orders - Create new order with balance validation and asset updates
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Union
from fastapi import APIRouter, Depends, status, Request

# Import API models
from api_models.order import OrderCreateRequest, OrderCreateResponse, OrderData
from api_models.shared.common import ErrorResponse

# Import common entities
from common.data.entities.order.enums import OrderType, OrderStatus

# Import dependencies
from controllers.dependencies import (
    get_current_user, get_transaction_manager,
    get_asset_dao_dependency, get_user_dao_dependency,
    get_balance_dao_dependency, get_asset_balance_dao_dependency
)
from common.core.utils.transaction_manager import TransactionManager

# Import DAOs
from common.data.dao.inventory import AssetDAO
from common.data.dao.user import UserDAO, BalanceDAO
from common.data.dao.asset import AssetBalanceDAO

# Import exceptions
from common.exceptions import (
    CNOPInsufficientBalanceException,
    CNOPDatabaseOperationException,
    CNOPLockAcquisitionException
)
from common.exceptions.shared_exceptions import CNOPInternalServerException

from order_exceptions import CNOPOrderValidationException

# Import business validators
from validation.business_validators import validate_order_creation_business_rules

# Import our standardized logger
from common.shared.logging import BaseLogger, Loggers, LogActions

# Initialize our standardized logger
logger = BaseLogger(Loggers.ORDER)
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
    transaction_manager: TransactionManager = Depends(get_transaction_manager),
    asset_dao: AssetDAO = Depends(get_asset_dao_dependency),
    user_dao: UserDAO = Depends(get_user_dao_dependency),
    balance_dao: BalanceDAO = Depends(get_balance_dao_dependency),
    asset_balance_dao: AssetBalanceDAO = Depends(get_asset_balance_dao_dependency)
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
        action=LogActions.REQUEST_START,
        message=f"Order creation attempt from {request.client.host if request.client else 'unknown'}",
        user=current_user["username"],
        extra={
            "order_type": order_data.order_type.value,
            "asset_id": order_data.asset_id,
            "quantity": str(order_data.quantity),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Business validation (Layer 2)
        validate_order_creation_business_rules(
            order_type=order_data.order_type,
            asset_id=order_data.asset_id,
            quantity=order_data.quantity,
            order_price=order_data.price,
            expires_at=None,  # Not implemented for market orders yet
            username=current_user["username"],
            asset_dao=asset_dao,
            user_dao=user_dao,
            balance_dao=balance_dao,
            asset_balance_dao=asset_balance_dao
        )

        # Calculate total amount for the order using current market price
        from controllers.dependencies import get_current_market_price
        current_price = get_current_market_price(order_data.asset_id, asset_dao)
        total_amount = order_data.quantity * current_price

        # Execute order based on type using TransactionManager
        if order_data.order_type in [OrderType.MARKET_BUY, OrderType.LIMIT_BUY]:
            # Buy order - validate USD balance and update asset balance
            result = await transaction_manager.create_buy_order_with_balance_update(
                username=current_user["username"],
                asset_id=order_data.asset_id,
                quantity=order_data.quantity,
                price=current_price,
                order_type=order_data.order_type,
                total_cost=total_amount
            )

            logger.info(
                action=LogActions.REQUEST_END,
                message=f"Buy order executed successfully: order_id={result.data['order'].order_id}, "
                       f"asset={order_data.asset_id}, quantity={order_data.quantity}, "
                       f"total_cost={total_amount}, lock_duration={result.lock_duration}s",
                user=current_user['username']
            )

        elif order_data.order_type in [OrderType.MARKET_SELL, OrderType.LIMIT_SELL]:
            # Sell order - validate asset balance and update USD balance
            result = await transaction_manager.create_sell_order_with_balance_update(
                username=current_user["username"],
                asset_id=order_data.asset_id,
                quantity=order_data.quantity,
                price=current_price,
                order_type=order_data.order_type,
                asset_amount=total_amount
            )

            logger.info(
                action=LogActions.REQUEST_END,
                message=f"Sell order executed successfully: order_id={result.data['order'].order_id}, "
                       f"asset={order_data.asset_id}, quantity={order_data.quantity}, "
                       f"asset_amount={total_amount}, lock_duration={result.lock_duration}s",
                user=current_user['username']
            )

        else:
            raise CNOPOrderValidationException(f"Unsupported order type: {order_data.order_type.value}")

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

    except CNOPInsufficientBalanceException as e:
        logger.warning(
            action=LogActions.VALIDATION_ERROR,
            message=f"Insufficient balance for order: order_type={order_data.order_type.value}, "
                   f"asset={order_data.asset_id}, quantity={order_data.quantity}, error={str(e)}",
            user=current_user['username']
        )
        # Wrap the exception in CNOPOrderValidationException
        raise CNOPOrderValidationException(str(e))

    except CNOPLockAcquisitionException as e:
        logger.warning(
            action=LogActions.ERROR,
            message=f"Lock acquisition failed for order: error={str(e)}",
            user=current_user['username']
        )
        raise CNOPInternalServerException("Service temporarily unavailable - please try again")

    except CNOPDatabaseOperationException as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Database operation failed for order: error={str(e)}",
            user=current_user['username']
        )
        raise CNOPInternalServerException("Service temporarily unavailable")

    except CNOPOrderValidationException as e:
        logger.warning(
            action=LogActions.VALIDATION_ERROR,
            message=f"Order validation failed: error={str(e)}",
            user=current_user['username']
        )
        # Re-raise the original exception without wrapping
        raise

    except Exception as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Unexpected error during order creation: order_type={order_data.order_type.value}, "
                   f"asset={order_data.asset_id}, quantity={order_data.quantity}, error={str(e)}",
            user=current_user['username']
        )
        raise CNOPInternalServerException("Service temporarily unavailable")