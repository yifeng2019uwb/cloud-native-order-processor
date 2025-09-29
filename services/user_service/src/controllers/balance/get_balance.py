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
from common.shared.logging import BaseLogger, Loggers, LogActions
from controllers.auth.dependencies import get_current_user
from controllers.dependencies import get_request_id_from_request

# Initialize our standardized logger
logger = BaseLogger(Loggers.USER)
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
        logger.info(action=LogActions.REQUEST_START, message=f"Balance request for user: {current_user.username}", request_id=request_id)

        # Get balance from database
        balance = balance_dao.get_balance(current_user.username)

        logger.info(action=LogActions.REQUEST_END, message=f"Balance retrieved successfully for user: {current_user.username}", request_id=request_id)

        return BalanceResponse(
            current_balance=balance.current_balance,
            updated_at=balance.updated_at
        )

    except CNOPUserNotFoundException:
        raise
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Failed to get balance for user {current_user.username}: {str(e)}", request_id=request_id)
        raise CNOPInternalServerException(f"Failed to get balance: {str(e)}")