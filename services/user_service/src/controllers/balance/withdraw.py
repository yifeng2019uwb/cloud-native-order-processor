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
from common.shared.logging import BaseLogger, Loggers, LogActions
from user_exceptions import CNOPUserValidationException
from controllers.dependencies import get_transaction_manager
from controllers.auth.dependencies import get_current_user
logger = BaseLogger(Loggers.USER)
router = APIRouter(tags=["balance"])


@router.post(
    "/balance/withdraw",
    response_model=Union[WithdrawResponse, ErrorResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Withdrawal successful",
            "model": WithdrawResponse
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
    # Log withdrawal attempt (without sensitive data)
    logger.info(
        action=LogActions.REQUEST_START,
        message=f"Withdrawal attempt from {request.client.host if request.client else 'unknown'}",
        user=current_user.username,
        extra={
            "amount": str(withdraw_data.amount),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Use transaction manager for atomic withdrawal operation
        result = await transaction_manager.withdraw_funds(
            username=current_user.username,
            amount=withdraw_data.amount
        )

        logger.info(action=LogActions.REQUEST_END, message=f"Withdrawal successful for user {current_user.username}: {withdraw_data.amount} (lock_duration: {result.lock_duration}s)", user=current_user.username)

        return WithdrawResponse(
            success=True,
            message=f"Successfully withdrew ${withdraw_data.amount}",
            transaction_id=str(result.data["transaction"].transaction_id),
            timestamp=datetime.utcnow()
        )

    except CNOPLockAcquisitionException as e:
        logger.warning(action=LogActions.ERROR, message=f"Lock acquisition failed for withdrawal: user={current_user.username}, error={str(e)}", user=current_user.username)
        raise CNOPInternalServerException("Service temporarily unavailable")

    except CNOPInsufficientBalanceException as e:
        logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Insufficient balance for withdrawal: user={current_user.username}, error={str(e)}", user=current_user.username)
        # Wrap the exception in CNOPUserValidationException
        raise CNOPUserValidationException(str(e))
    except CNOPUserValidationException as e:
        logger.warning(action=LogActions.VALIDATION_ERROR, message=f"User validation error for withdrawal: user={current_user.username}, error={str(e)}", user=current_user.username)
        # Re-raise the original exception without wrapping
        raise
    except CNOPDatabaseOperationException as e:
        if "User balance not found" in str(e):
            logger.error(action=LogActions.ERROR, message=f"System error - user balance not found for withdrawal: user={current_user.username}, error={str(e)}", user=current_user.username)
            raise CNOPInternalServerException("System error - please contact support")
        else:
            logger.error(action=LogActions.ERROR, message=f"Database operation failed for withdrawal: user={current_user.username}, error={str(e)}", user=current_user.username)
            raise CNOPInternalServerException("Service temporarily unavailable")
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Unexpected error during withdrawal: user={current_user.username}, error={str(e)}", user=current_user.username)
        raise CNOPInternalServerException("Service temporarily unavailable")