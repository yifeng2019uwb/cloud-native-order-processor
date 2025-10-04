"""
Withdraw API Endpoint
Path: services/user_service/src/controllers/balance/withdraw.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from datetime import datetime, timezone
from typing import Union
from fastapi import APIRouter, HTTPException, Depends, status, Request
from api_models.balance import WithdrawRequest, WithdrawResponse
from api_models.shared.common import ErrorResponse
from common.data.entities.user import User
from common.exceptions.shared_exceptions import (
    CNOPUserNotFoundException,
    CNOPInternalServerException
)
from common.exceptions import (
    CNOPDatabaseOperationException,
    CNOPEntityNotFoundException,
    CNOPLockAcquisitionException,
    CNOPInsufficientBalanceException
)
from common.shared.logging import BaseLogger, Loggers, LogActions, LogFields, LogExtraDefaults
from common.shared.constants.error_messages import ErrorMessages
from common.shared.constants.api_responses import APIResponseDescriptions
from common.shared.constants.http_status import HTTPStatus
from api_info_enum import ApiTags, ApiPaths, ApiResponseKeys
from user_exceptions import CNOPUserValidationException
from controllers.dependencies import get_transaction_manager, get_request_id_from_request
from controllers.auth.dependencies import get_current_user
# Local constants for this controller only
MSG_SUCCESS_WITHDRAW = "Withdrawal successful"
MSG_ERROR_INSUFFICIENT_BALANCE = "Bad request - insufficient balance"
MSG_ERROR_OPERATION_BUSY = "Operation is busy - try again"

logger = BaseLogger(Loggers.USER)
router = APIRouter(tags=[ApiTags.BALANCE.value])


@router.post(
    ApiPaths.WITHDRAW.value,
    response_model=Union[WithdrawResponse, ErrorResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        HTTPStatus.CREATED: {
            ApiResponseKeys.DESCRIPTION.value: MSG_SUCCESS_WITHDRAW,
            ApiResponseKeys.MODEL.value: WithdrawResponse
        },
        HTTPStatus.BAD_REQUEST: {
            ApiResponseKeys.DESCRIPTION.value: MSG_ERROR_INSUFFICIENT_BALANCE,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.UNAUTHORIZED: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_UNAUTHORIZED,
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
async def withdraw_funds(
    withdraw_data: WithdrawRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    transaction_manager = Depends(get_transaction_manager)
) -> WithdrawResponse:
    """
    Withdraw funds from user account using transaction manager for atomicity

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (user authentication, etc.)
    """
    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)

    # Log withdrawal attempt (without sensitive data)
    logger.info(
        action=LogActions.REQUEST_START,
        message=f"Withdrawal attempt from {request.client.host if request.client else 'unknown'}",
        user=current_user.username,
        request_id=request_id,
        extra={
            LogFields.AMOUNT: str(withdraw_data.amount),
            LogFields.USER_AGENT: request.headers.get(LogFields.USER_AGENT, LogExtraDefaults.UNKNOWN_USER_AGENT),
            LogFields.TIMESTAMP: datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Use transaction manager for atomic withdrawal operation
        result = await transaction_manager.withdraw_funds(
            username=current_user.username,
            amount=withdraw_data.amount
        )

        logger.info(action=LogActions.REQUEST_END, message=f"Withdrawal successful for user {current_user.username}: {withdraw_data.amount} (lock_duration: {result.lock_duration}s)", user=current_user.username, request_id=request_id)

        return WithdrawResponse(
            success=True,
            message=f"Successfully withdrew ${withdraw_data.amount}",
            transaction_id=str(result.data["transaction"].transaction_id),
            timestamp=datetime.utcnow()
        )

    except CNOPLockAcquisitionException as e:
        logger.warning(action=LogActions.ERROR, message=f"Lock acquisition failed for withdrawal: user={current_user.username}, error={str(e)}", user=current_user.username, request_id=request_id)
        raise CNOPInternalServerException(ErrorMessages.SERVICE_UNAVAILABLE)

    except CNOPInsufficientBalanceException as e:
        logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Insufficient balance for withdrawal: user={current_user.username}, error={str(e)}", user=current_user.username, request_id=request_id)
        # Wrap the exception in CNOPUserValidationException
        raise CNOPUserValidationException(str(e))
    except CNOPUserValidationException as e:
        logger.warning(action=LogActions.VALIDATION_ERROR, message=f"User validation error for withdrawal: user={current_user.username}, error={str(e)}", user=current_user.username, request_id=request_id)
        # Re-raise the original exception without wrapping
        raise
    except CNOPDatabaseOperationException as e:
        if "User balance not found" in str(e):
            logger.error(action=LogActions.ERROR, message=f"System error - user balance not found for withdrawal: user={current_user.username}, error={str(e)}", user=current_user.username, request_id=request_id)
            raise CNOPInternalServerException(ErrorMessages.SERVICE_UNAVAILABLE)
        else:
            logger.error(action=LogActions.ERROR, message=f"Database operation failed for withdrawal: user={current_user.username}, error={str(e)}", user=current_user.username, request_id=request_id)
            raise CNOPInternalServerException(ErrorMessages.SERVICE_UNAVAILABLE)
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Unexpected error during withdrawal: user={current_user.username}, error={str(e)}", user=current_user.username, request_id=request_id)
        raise CNOPInternalServerException(ErrorMessages.SERVICE_UNAVAILABLE)