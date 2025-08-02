"""
Deposit API Endpoint
Path: services/user_service/src/controllers/balance/deposit.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from typing import Union
import logging
from datetime import datetime, timezone

# Import user-service API models
from api_models.balance import DepositRequest, DepositResponse
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



logger = logging.getLogger(__name__)
router = APIRouter(tags=["balance"])


@router.post(
    "/balance/deposit",
    response_model=Union[DepositResponse, ErrorResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Deposit successful",
            "model": DepositResponse
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
async def deposit_funds(
    deposit_data: DepositRequest,
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    balance_dao = Depends(get_balance_dao)
) -> DepositResponse:
    """
    Deposit funds to user account

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (user authentication, etc.)
    """
    # Log deposit attempt (without sensitive data)
    logger.info(
        f"Deposit attempt from {request.client.host if request.client else 'unknown'}",
        extra={
            "username": current_user.username,
            "amount": str(deposit_data.amount),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

        try:
        # Create deposit transaction
        from common.entities.user import BalanceTransaction, TransactionType, TransactionStatus

        transaction = BalanceTransaction(
            user_id=current_user.user_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=deposit_data.amount,
            description="Deposit",
            status=TransactionStatus.COMPLETED
        )

        # Save transaction to database
        created_transaction = await balance_dao.create_transaction(transaction)

        logger.info(f"Deposit successful for user {current_user.username}: {deposit_data.amount}")

        return DepositResponse(
            success=True,
            message=f"Successfully deposited ${deposit_data.amount}",
            transaction_id=str(created_transaction.transaction_id),
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Deposit failed for user {current_user.username}: {str(e)}", exc_info=True)
        raise InternalServerException(f"Deposit failed: {str(e)}")