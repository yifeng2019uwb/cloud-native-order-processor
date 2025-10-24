"""
Get Balance API Endpoint
Path: services/user_service/src/controllers/balance/get_balance.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from datetime import datetime, timezone
from typing import Union
from fastapi import APIRouter, HTTPException, Depends, status, Request
from api_models.balance import BalanceResponse
from api_models.shared.common import ErrorResponse
from common.data.database.dependencies import get_balance_dao
from common.data.entities.user import User
from common.exceptions.shared_exceptions import CNOPUserNotFoundException, CNOPInternalServerException
from common.shared.logging import BaseLogger, LogAction, LoggerName
from common.shared.constants.api_constants import ErrorMessages
from common.shared.constants.api_constants import APIResponseDescriptions
from common.shared.constants.api_constants import HTTPStatus
from api_info_enum import ApiTags, ApiPaths, ApiResponseKeys
from constants import MSG_SUCCESS_BALANCE_RETRIEVED
from controllers.auth.dependencies import get_current_user
from common.auth.gateway.header_validator import get_request_id_from_request

# Initialize our standardized logger
logger = BaseLogger(LoggerName.USER)
router = APIRouter(tags=[ApiTags.BALANCE.value])


@router.get(
    ApiPaths.BALANCE.value,
    response_model=Union[BalanceResponse, ErrorResponse],
    responses={
        HTTPStatus.OK: {
            ApiResponseKeys.DESCRIPTION.value: MSG_SUCCESS_BALANCE_RETRIEVED,
            ApiResponseKeys.MODEL.value: BalanceResponse
        },
        HTTPStatus.UNAUTHORIZED: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_UNAUTHORIZED,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.NOT_FOUND: {
            ApiResponseKeys.DESCRIPTION.value: ErrorMessages.USER_NOT_FOUND,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.SERVICE_UNAVAILABLE: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_SERVICE_UNAVAILABLE,
            ApiResponseKeys.MODEL.value: ErrorResponse
        }
    }
)
def get_user_balance(
    request: Request,
    current_user: User = Depends(get_current_user),
    balance_dao = Depends(get_balance_dao)
) -> BalanceResponse:
    """
    Get current user balance

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (user authentication, etc.)
    """
    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)

    try:
        logger.info(action=LogAction.REQUEST_START, message=f"Balance request for user: {current_user.username}", request_id=request_id)

        # Get balance from database
        balance = balance_dao.get_balance(current_user.username)

        logger.info(action=LogAction.REQUEST_END, message=f"Balance retrieved successfully for user: {current_user.username}", request_id=request_id)

        return BalanceResponse(
            current_balance=balance.current_balance,
            updated_at=balance.updated_at
        )

    except CNOPUserNotFoundException:
        raise
    except Exception as e:
        logger.error(action=LogAction.ERROR, message=f"Failed to get balance for user {current_user.username}: {str(e)}", request_id=request_id)
        raise CNOPInternalServerException(f"{ErrorMessages.INTERNAL_SERVER_ERROR} while retrieving balance: {str(e)}")