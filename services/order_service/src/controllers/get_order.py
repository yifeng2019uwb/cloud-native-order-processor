"""
Get Order Controller
Path: services/order_service/src/controllers/get_order.py

Handles order retrieval endpoint with business logic directly in controller
- GET /orders/{order_id} - Get order by ID
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, Path
from api_models.get_order import GetOrderRequest, GetOrderResponse
from api_models.shared.data_models import OrderData
from common.data.dao.order.order_dao import OrderDAO
from common.data.entities.user import User
from common.exceptions.shared_exceptions import (
    CNOPOrderNotFoundException,
    CNOPInternalServerException
)
from order_exceptions.exceptions import CNOPOrderValidationException
from common.shared.logging import BaseLogger, LoggerName, LogAction
from common.shared.constants.api_constants import HTTPStatus
from common.shared.constants.api_constants import APIResponseDescriptions
from api_info_enum import ApiTags, ApiResponseKeys, API_ORDER_BY_ID
from constants import MSG_SUCCESS_ORDER_RETRIEVED, MSG_ERROR_ORDER_NOT_FOUND
from common.shared.constants.api_constants import ErrorMessages
from controllers.dependencies import (
    get_current_user, get_order_dao_dependency,
    get_user_dao_dependency
)
from common.auth.gateway.header_validator import get_request_id_from_request
from src.validation.business_validators import validate_order_retrieval_business_rules

# Initialize our standardized logger
logger = BaseLogger(LoggerName.ORDER)
router = APIRouter(tags=[ApiTags.ORDERS.value])


def get_order_request(order_id: str = Path(..., description="Order ID")) -> GetOrderRequest:
    """Dependency to create and validate GetOrderRequest from path parameter"""
    return GetOrderRequest(order_id=order_id)


@router.get(
    API_ORDER_BY_ID,
    response_model=GetOrderResponse
)
def get_order(
    request: Request,
    order_request: GetOrderRequest = Depends(get_order_request),
    current_user: User = Depends(get_current_user),
    order_dao: OrderDAO = Depends(get_order_dao_dependency)
) -> GetOrderResponse:
    """
    Get order by ID with user authorization
    """
    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)

    try:

        # Get order from database
        order_id = order_request.order_id
        order = order_dao.get_order(order_id)

        # Check if order belongs to user
        if order.username != current_user.username:
            logger.warning(
                action=LogAction.ACCESS_DENIED,
                message=f"Unauthorized access attempt: order_id={order_id}",
                user=current_user.username,
                request_id=request_id
            )
            raise CNOPOrderNotFoundException(f"Order '{order_id}' not found")

        logger.info(
            action=LogAction.REQUEST_END,
            message=f"Order retrieved: order_id={order_id}",
            user=current_user.username,
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

        return GetOrderResponse(data=order_data_response)

    except CNOPOrderNotFoundException:
        raise
    except CNOPOrderValidationException:
        raise
    except Exception as e:
        logger.error(
            action=LogAction.ERROR,
            message=f"Unexpected error retrieving order: order_id={order_id}, error={str(e)}",
            user=current_user.username,
            request_id=request_id
        )
        raise CNOPInternalServerException(ErrorMessages.SERVICE_UNAVAILABLE)