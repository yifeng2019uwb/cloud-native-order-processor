"""
Get Balance API Endpoint
Path: services/user_service/src/controllers/balance/get_balance.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Union
import logging
from datetime import datetime, timezone

# Import user-service API models
from api_models.balance import BalanceResponse
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


@router.get(
    "/balance",
    response_model=Union[BalanceResponse, ErrorResponse],
    responses={
        200: {
            "description": "Balance retrieved successfully",
            "model": BalanceResponse
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
async def get_user_balance(
    current_user: UserResponse = Depends(get_current_user),
    balance_dao = Depends(get_balance_dao)
) -> BalanceResponse:
    """
    Get current user balance

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (user authentication, etc.)
    """
    try:
        logger.info(f"Balance request for user: {current_user.username}")

        # Get balance from database
        balance = balance_dao.get_balance(current_user.username)

        logger.info(f"Balance retrieved successfully for user: {current_user.username}")

        return BalanceResponse(
            current_balance=balance.current_balance,
            updated_at=balance.updated_at
        )

    except UserNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to get balance for user {current_user.username}: {str(e)}", exc_info=True)
        raise InternalServerException(f"Failed to get balance: {str(e)}")