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
from common.data.entities.user import UserResponse

# Import dependencies
from common.core.utils import get_transaction_manager
from controllers.auth.dependencies import get_current_user

# Import exceptions
from common.exceptions.shared_exceptions import CNOPUserNotFoundException, CNOPInternalServerException
from common.exceptions import (
    CNOPDatabaseOperationException,
    CNOPEntityNotFoundException,
    CNOPLockAcquisitionException
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
        400: {
            "description": "Bad request - invalid amount",
            "model": ErrorResponse
        },
        401: {
            "description": "Unauthorized",
            "model": ErrorResponse
        },
        404: {
            "description": "User balance not found",
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
async def deposit_funds(
    deposit_data: DepositRequest,
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    transaction_manager = Depends(get_transaction_manager)
) -> DepositResponse:
    """
    Deposit funds to user account using transaction manager for atomicity

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
        # Use transaction manager for atomic deposit operation
        result = await transaction_manager.deposit_funds(
            username=current_user.username,
            amount=deposit_data.amount
        )

        logger.info(f"Deposit successful for user {current_user.username}: {deposit_data.amount} (lock_duration: {result.lock_duration}s)")

        return DepositResponse(
            success=True,
            message=f"Successfully deposited ${deposit_data.amount}",
            transaction_id=str(result.data["transaction"].transaction_id),
            timestamp=datetime.utcnow()
        )

    except CNOPLockAcquisitionException as e:
        logger.warning(f"Lock acquisition failed for deposit: user={current_user.username}, error={str(e)}")
        raise CNOPInternalServerException("Service temporarily unavailable")
    except CNOPEntityNotFoundException as e:
        logger.error(f"User balance not found for deposit: user={current_user.username}, error={str(e)}")
        raise CNOPUserNotFoundException("User balance not found")
    except CNOPDatabaseOperationException as e:
        logger.error(f"Database operation failed for deposit: user={current_user.username}, error={str(e)}")
        raise CNOPInternalServerException("Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error during deposit: user={current_user.username}, error={str(e)}", exc_info=True)
        raise CNOPInternalServerException("Service temporarily unavailable")