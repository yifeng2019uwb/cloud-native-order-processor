"""
Transactions API Endpoint
Path: services/user_service/src/controllers/balance/transactions.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Union
from datetime import datetime, timezone

# Import user-service API models
from api_models.balance import TransactionListResponse, TransactionResponse
from api_models.shared.common import ErrorResponse

# Import common DAO models
from common.data.entities.user import UserResponse

# Import dependencies
from common.data.database import get_balance_dao
from controllers.auth.dependencies import get_current_user

# Import exceptions
from common.exceptions.shared_exceptions import CNOPInternalServerException

# Import our standardized logger
from common.shared.logging import BaseLogger, Loggers, LogActions

# Initialize our standardized logger
logger = BaseLogger(Loggers.USER)
router = APIRouter(tags=["balance"])


@router.get(
    "/balance/transactions",
    response_model=Union[TransactionListResponse, ErrorResponse],
    responses={
        200: {
            "description": "Transactions retrieved successfully",
            "model": TransactionListResponse
        },
        401: {
            "description": "Unauthorized",
            "model": ErrorResponse
        },
        404: {
            "description": "User not found",
            "model": ErrorResponse
        },
        503: {
            "description": "Service unavailable",
            "model": ErrorResponse
        }
    }
)
def get_user_transactions(
    current_user: UserResponse = Depends(get_current_user),
    balance_dao = Depends(get_balance_dao)
) -> TransactionListResponse:
    """
    Get user transaction history

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (user authentication, etc.)
    """
    try:
        logger.info(action=LogActions.REQUEST_START, message=f"Transaction history request for user: {current_user.username}")

        # Get transactions from database
        transactions, _ = balance_dao.get_user_transactions(current_user.username)

        if transactions is None:
            transactions = []  # Empty list if no transactions



        transaction_responses = []
        for transaction in transactions:
            transaction_responses.append(TransactionResponse(
                transaction_id=str(transaction.transaction_id),
                transaction_type=transaction.transaction_type.value,
                amount=transaction.amount,
                status=transaction.status.value,
                created_at=transaction.created_at
            ))

        logger.info(action=LogActions.REQUEST_END, message=f"Transaction history retrieved successfully for user: {current_user.username}")

        return TransactionListResponse(
            transactions=transaction_responses,
            total_count=len(transaction_responses)
        )

    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Failed to get transactions for user {current_user.username}: {str(e)}")
        raise CNOPInternalServerException(f"Failed to get transactions: {str(e)}")