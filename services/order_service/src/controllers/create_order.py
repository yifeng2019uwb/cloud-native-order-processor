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
from api_models.order import OrderCreateRequest, OrderCreateResponse, OrderData
from api_models.shared.common import ErrorResponse
from common.data.entities.order.enums import OrderType, OrderStatus
from common.core.utils.transaction_manager import TransactionManager
from common.data.dao.inventory.asset_dao import AssetDAO
from common.data.dao.user.user_dao import UserDAO
from common.data.dao.user.balance_dao import BalanceDAO
from common.exceptions import (
    CNOPInsufficientBalanceException,
    CNOPDatabaseOperationException,
    CNOPLockAcquisitionException
)
from common.exceptions.shared_exceptions import CNOPInternalServerException
from common.shared.logging import BaseLogger, Loggers, LogActions
from common.shared.constants.http_status import HTTPStatus
from common.shared.constants.api_responses import APIResponseDescriptions
from api_info_enum import ApiTags, ApiPaths, ApiResponseKeys, API_ORDERS_ROOT
from constants import (
    MSG_SUCCESS_ORDER_CREATED, MSG_SUCCESS_MARKET_BUY_ORDER_CREATED, MSG_SUCCESS_MARKET_SELL_ORDER_CREATED,
    MSG_ERROR_INSUFFICIENT_BALANCE, MSG_ERROR_ORDER_VALIDATION_FAILED, MSG_ERROR_ORDER_PROCESSING_FAILED,
    MSG_ERROR_LOCK_ACQUISITION_FAILED, MSG_ERROR_UNEXPECTED_ERROR,
    USER_AGENT_HEADER, UNKNOWN_VALUE
)
from common.shared.constants.error_messages import ErrorMessages
from order_exceptions import CNOPOrderValidationException
from controllers.dependencies import (
    get_current_user, get_transaction_manager,
    get_asset_dao_dependency, get_user_dao_dependency,
    get_balance_dao_dependency,
    get_request_id_from_request
)
from validation.business_validators import validate_order_creation_business_rules

# Initialize our standardized logger
logger = BaseLogger(Loggers.ORDER)
router = APIRouter(tags=[ApiTags.ORDERS.value])


@router.post(
    API_ORDERS_ROOT,
    response_model=Union[OrderCreateResponse, ErrorResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        HTTPStatus.CREATED: {
            ApiResponseKeys.DESCRIPTION.value: MSG_SUCCESS_ORDER_CREATED,
            ApiResponseKeys.MODEL.value: OrderCreateResponse
        },
        HTTPStatus.BAD_REQUEST: {
            ApiResponseKeys.DESCRIPTION.value: MSG_ERROR_INSUFFICIENT_BALANCE,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.UNAUTHORIZED: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_AUTHENTICATION_FAILED,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.CONFLICT: {
            ApiResponseKeys.DESCRIPTION.value: MSG_ERROR_LOCK_ACQUISITION_FAILED,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_VALIDATION,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.SERVICE_UNAVAILABLE: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_SERVICE_UNAVAILABLE,
            ApiResponseKeys.MODEL.value: ErrorResponse
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
) -> OrderCreateResponse:
    """
    Create a new order with atomic operations using TransactionManager

    Supports:
    - Market Buy: Immediate purchase with balance validation
    - Market Sell: Immediate sale with asset balance validation
    - Limit Buy/Sell: Future implementation
    """
    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)

    # Log order creation attempt
    logger.info(
        action=LogActions.REQUEST_START,
        message=f"Order creation attempt from {request.client.host if request.client else 'unknown'}",
        user=current_user["username"],
        request_id=request_id,
        extra={
            "order_type": order_data.order_type.value,
            "asset_id": order_data.asset_id,
            "quantity": str(order_data.quantity),
            "user_agent": request.headers.get(USER_AGENT_HEADER, UNKNOWN_VALUE),
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
                user=current_user['username'],
                request_id=request_id
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
                user=current_user['username'],
                request_id=request_id
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
            status=created_order.status,
            total_amount=created_order.total_amount,
            created_at=created_order.created_at
        )

        # Determine success message based on order type
        if order_data.order_type == OrderType.MARKET_BUY:
            success_message = MSG_SUCCESS_MARKET_BUY_ORDER_CREATED
        elif order_data.order_type == OrderType.MARKET_SELL:
            success_message = MSG_SUCCESS_MARKET_SELL_ORDER_CREATED
        else:
            success_message = MSG_SUCCESS_ORDER_CREATED

        return OrderCreateResponse(
            success=True,
            message=success_message,
            data=order_data_response,
            timestamp=datetime.utcnow()
        )

    except CNOPInsufficientBalanceException as e:
        logger.warning(
            action=LogActions.VALIDATION_ERROR,
            message=f"Insufficient balance for order: order_type={order_data.order_type.value}, "
                   f"asset={order_data.asset_id}, quantity={order_data.quantity}, error={str(e)}",
            user=current_user['username'],
            request_id=request_id
        )
        # Wrap the exception in CNOPOrderValidationException
        raise CNOPOrderValidationException(str(e))

    except CNOPLockAcquisitionException as e:
        logger.warning(
            action=LogActions.ERROR,
            message=f"Lock acquisition failed for order: error={str(e)}",
            user=current_user['username'],
            request_id=request_id
        )
        raise CNOPInternalServerException(ErrorMessages.SERVICE_UNAVAILABLE)

    except CNOPDatabaseOperationException as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Database operation failed for order: error={str(e)}",
            user=current_user['username'],
            request_id=request_id
        )
        raise CNOPInternalServerException(ErrorMessages.SERVICE_UNAVAILABLE)

    except CNOPOrderValidationException as e:
        logger.warning(
            action=LogActions.VALIDATION_ERROR,
            message=f"Order validation failed: error={str(e)}",
            user=current_user['username'],
            request_id=request_id
        )
        # Re-raise the original exception without wrapping
        raise

    except Exception as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Unexpected error during order creation: order_type={order_data.order_type.value}, "
                   f"asset={order_data.asset_id}, quantity={order_data.quantity}, error={str(e)}",
            user=current_user['username'],
            request_id=request_id
        )
        raise CNOPInternalServerException(ErrorMessages.SERVICE_UNAVAILABLE)