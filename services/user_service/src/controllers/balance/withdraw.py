"""
Withdraw API Endpoint
Path: services/user_service/src/controllers/balance/withdraw.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from typing import Union
import logging
from datetime import datetime, timezone

# Import user-service API models
from api_models.balance import WithdrawRequest, WithdrawResponse
from api_models.shared.common import ErrorResponse

# Import common DAO models
from common.entities.user import UserResponse

# Import dependencies
from common.database import get_transaction_manager
from controllers.auth.dependencies import get_current_user

# Import exceptions
from user_exceptions import (
    UserNotFoundException,
    UserValidationException,
    InternalServerException
)

# Import common exceptions for transaction manager
from common.exceptions import (
    DatabaseOperationException,
    EntityNotFoundException,
    LockAcquisitionException,
    InsufficientBalanceException
)
from common.exceptions.shared_exceptions import UserValidationException as CommonUserValidationException

logger = logging.getLogger(__name__)
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
    current_user: UserResponse = Depends(get_current_user),
    transaction_manager = Depends(get_transaction_manager)
) -> WithdrawResponse:
    """
    Withdraw funds from user account using transaction manager for atomicity

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (user authentication, etc.)
    """
    # Log withdrawal attempt (without sensitive data)
    logger.info(
        f"Withdrawal attempt from {request.client.host if request.client else 'unknown'}",
        extra={
            "username": current_user.username,
            "amount": str(withdraw_data.amount),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Use transaction manager for atomic withdrawal operation
        result = await transaction_manager.withdraw_funds(
            user_id=current_user.username,
            amount=withdraw_data.amount
        )

        logger.info(f"Withdrawal successful for user {current_user.username}: {withdraw_data.amount} (lock_duration: {result.lock_duration}s)")

        return WithdrawResponse(
            success=True,
            message=f"Successfully withdrew ${withdraw_data.amount}",
            transaction_id=str(result.data["transaction"].transaction_id),
            timestamp=datetime.utcnow()
        )

    except LockAcquisitionException as e:
        logger.warning(f"Lock acquisition failed for withdrawal: user={current_user.username}, error={str(e)}")
        raise InternalServerException("Service temporarily unavailable")

    except InsufficientBalanceException as e:
        logger.warning(f"Insufficient balance for withdrawal: user={current_user.username}, error={str(e)}")
        raise UserValidationException(str(e))
    except CommonUserValidationException as e:
        logger.warning(f"User validation error for withdrawal: user={current_user.username}, error={str(e)}")
        raise UserValidationException(str(e))
    except DatabaseOperationException as e:
        if "User balance not found" in str(e):
            logger.error(f"System error - user balance not found for withdrawal: user={current_user.username}, error={str(e)}")
            raise InternalServerException("System error - please contact support")
        else:
            logger.error(f"Database operation failed for withdrawal: user={current_user.username}, error={str(e)}")
            raise InternalServerException("Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error during withdrawal: user={current_user.username}, error={str(e)}", exc_info=True)
        raise InternalServerException("Service temporarily unavailable")