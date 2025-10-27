"""
List Orders Controller
Path: services/order_service/src/controllers/list_orders.py

Handles order listing endpoint with business logic directly in controller
- GET /orders - List user orders with filters
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Request
from api_models.list_orders import ListOrdersRequest, ListOrdersResponse
from api_models.shared.data_models import OrderSummary
from common.data.dao.order.order_dao import OrderDAO
from common.exceptions.shared_exceptions import CNOPInternalServerException
from common.shared.logging import BaseLogger, LoggerName, LogAction
from common.shared.constants.api_constants import HTTPStatus
from common.shared.constants.api_constants import APIResponseDescriptions
from api_info_enum import ApiTags, ApiResponseKeys, API_ORDERS_ROOT
from constants import MSG_SUCCESS_ORDERS_LISTED
from common.shared.constants.api_constants import ErrorMessages
from controllers.dependencies import (
    get_current_user, get_order_dao_dependency
)
from common.auth.gateway.header_validator import get_request_id_from_request
from common.auth.security.auth_dependencies import AuthenticatedUser

# Initialize our standardized logger
logger = BaseLogger(LoggerName.ORDER)
router = APIRouter(tags=[ApiTags.ORDERS.value])


@router.get(
    API_ORDERS_ROOT,
    response_model=ListOrdersResponse
)
def list_orders(
    request: Request,
    filter_params: ListOrdersRequest = Depends(),
    current_user: AuthenticatedUser = Depends(get_current_user),
    order_dao: OrderDAO = Depends(get_order_dao_dependency)
    ) -> ListOrdersResponse:
    """
    List user orders with optional filters and pagination
    """
    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)

    try:
        # Get all orders for user
        orders = order_dao.get_orders_by_user(current_user.username)

        # Apply filters
        filtered_orders = []
        for order in orders:
            # Filter by asset_id
            if filter_params.asset_id and order.asset_id != filter_params.asset_id:
                continue

            # Filter by order_type
            if filter_params.order_type and order.order_type != filter_params.order_type:
                continue

            filtered_orders.append(order)

        # Apply pagination
        paginated_orders = filtered_orders[filter_params.offset:filter_params.offset + filter_params.limit]

        logger.info(
            action=LogAction.REQUEST_END,
            message=f"Orders listed: count={len(paginated_orders)}",
            user=current_user.username,
            request_id=request_id
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
        has_more = len(paginated_orders) == filter_params.limit

        return ListOrdersResponse(
            data=order_summaries,
            has_more=has_more
        )

    except Exception as e:
        logger.error(
            action=LogAction.ERROR,
            message=f"Unexpected error listing orders: error={str(e)}",
            user=current_user.username,
            request_id=request_id
        )
        raise CNOPInternalServerException(ErrorMessages.SERVICE_UNAVAILABLE)