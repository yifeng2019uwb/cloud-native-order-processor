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
from common.database import get_balance_dao
from controllers.auth.dependencies import get_current_user

# Import exceptions
from user_exceptions import (
    UserNotFoundException,
    InternalServerException
)

# Import business validation functions only (Layer 2)
from validation.business_validators import (
    validate_sufficient_balance
)

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
        401: {
            "description": "Unauthorized",
            "model": ErrorResponse
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse
        },
        503: {
            "description": "Service unavailable",
            "model": ErrorResponse
        }
    }
)
async def withdraw_funds(
    withdraw_data: WithdrawRequest,
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    balance_dao = Depends(get_balance_dao)
) -> WithdrawResponse:
    """
    Withdraw funds from user account

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
        # Layer 2: Business validation only
        await validate_sufficient_balance(current_user.user_id, withdraw_data.amount, balance_dao)

        # Create withdrawal transaction
        from common.entities.user import BalanceTransaction, TransactionType, TransactionStatus

        transaction = BalanceTransaction(
            user_id=current_user.user_id,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=-withdraw_data.amount,  # Negative amount for withdrawal
            description="Withdrawal",
            status=TransactionStatus.COMPLETED
        )

        # Save transaction to database
        created_transaction = await balance_dao.create_transaction(transaction)

        logger.info(f"Withdrawal successful for user {current_user.username}: {withdraw_data.amount}")

        return WithdrawResponse(
            success=True,
            message=f"Successfully withdrew ${withdraw_data.amount}",
            transaction_id=str(created_transaction.transaction_id),
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Withdrawal failed for user {current_user.username}: {str(e)}", exc_info=True)
        raise InternalServerException(f"Withdrawal failed: {str(e)}")