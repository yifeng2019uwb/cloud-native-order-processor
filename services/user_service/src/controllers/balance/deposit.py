"""
Deposit API Endpoint
Path: services/user_service/src/controllers/balance/deposit.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from datetime import datetime, timezone
from typing import Union
from fastapi import APIRouter, HTTPException, Depends, status, Request
from api_models.balance import DepositRequest, DepositResponse
from api_models.shared.common import ErrorResponse
from common.data.entities.user import User
from common.exceptions.shared_exceptions import CNOPUserNotFoundException, CNOPInternalServerException
from common.exceptions import (
    CNOPDatabaseOperationException,
    CNOPEntityNotFoundException,
    CNOPLockAcquisitionException
)
from common.shared.logging import BaseLogger, Loggers, LogActions, LogFields, LogExtraDefaults
from common.shared.constants.api_constants import ErrorMessages
from common.shared.constants.api_constants import APIResponseDescriptions
from common.shared.constants.api_constants import HTTPStatus
from api_info_enum import ApiTags, ApiPaths, ApiResponseKeys
from controllers.dependencies import get_transaction_manager
from common.auth.gateway.header_validator import get_request_id_from_request
from controllers.auth.dependencies import get_current_user
# Local constants for this controller only
MSG_SUCCESS_DEPOSIT = "Deposit successful"
MSG_ERROR_INVALID_AMOUNT = "Bad request - invalid amount"
MSG_ERROR_USER_BALANCE_NOT_FOUND = "User balance not found"
MSG_ERROR_OPERATION_BUSY = "Operation is busy - try again"

logger = BaseLogger(Loggers.USER)
router = APIRouter(tags=[ApiTags.BALANCE.value])


@router.post(
    ApiPaths.DEPOSIT.value,
    response_model=Union[DepositResponse, ErrorResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        HTTPStatus.CREATED: {
            ApiResponseKeys.DESCRIPTION.value: MSG_SUCCESS_DEPOSIT,
            ApiResponseKeys.MODEL.value: DepositResponse
        },
        HTTPStatus.BAD_REQUEST: {
            ApiResponseKeys.DESCRIPTION.value: MSG_ERROR_INVALID_AMOUNT,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.UNAUTHORIZED: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_UNAUTHORIZED,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.NOT_FOUND: {
            ApiResponseKeys.DESCRIPTION.value: MSG_ERROR_USER_BALANCE_NOT_FOUND,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.CONFLICT: {
            ApiResponseKeys.DESCRIPTION.value: MSG_ERROR_OPERATION_BUSY,
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
async def deposit_funds(
    deposit_data: DepositRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    transaction_manager = Depends(get_transaction_manager)
) -> DepositResponse:
    """
    Deposit funds to user account using transaction manager for atomicity

    ASYNC OPERATION: Modifies balance, requires user lock for atomicity.
    Lock timeout: 2 seconds (LOCK_TIMEOUTS['deposit'])

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (user authentication, etc.)
    """
    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)

    # Log deposit attempt (without sensitive data)
    logger.info(
        action=LogActions.REQUEST_START,
        message=f"Deposit attempt from {request.client.host if request.client else 'unknown'}",
        user=current_user.username,
        request_id=request_id,
        extra={
            LogFields.AMOUNT: str(deposit_data.amount),
            LogFields.USER_AGENT: request.headers.get(LogFields.USER_AGENT, LogExtraDefaults.UNKNOWN_USER_AGENT),
            LogFields.TIMESTAMP: datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Use transaction manager for atomic deposit operation
        result = await transaction_manager.deposit_funds(
            username=current_user.username,
            amount=deposit_data.amount
        )

        logger.info(action=LogActions.REQUEST_END, message=f"Deposit successful for user {current_user.username}: {deposit_data.amount}", user=current_user.username, request_id=request_id)

        return DepositResponse(
            success=True,
            message=f"Successfully deposited ${deposit_data.amount}",
            transaction_id=str(result.transaction.transaction_id),
            timestamp=datetime.now(timezone.utc)
        )

    except CNOPLockAcquisitionException as e:
        logger.warning(action=LogActions.ERROR, message=f"Lock acquisition failed for deposit: user={current_user.username}, error={str(e)}", user=current_user.username, request_id=request_id)
        raise CNOPInternalServerException("Service temporarily unavailable")
    except CNOPEntityNotFoundException as e:
        logger.error(action=LogActions.ERROR, message=f"User balance not found for deposit: user={current_user.username}, error={str(e)}", user=current_user.username, request_id=request_id)
        raise CNOPUserNotFoundException("User balance not found")
    except CNOPDatabaseOperationException as e:
        logger.error(action=LogActions.ERROR, message=f"Database operation failed for deposit: user={current_user.username}, error={str(e)}", user=current_user.username, request_id=request_id)
        raise CNOPInternalServerException("Service temporarily unavailable")
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Unexpected error during deposit: user={current_user.username}, error={str(e)}", user=current_user.username, request_id=request_id)
        raise CNOPInternalServerException("Service temporarily unavailable")