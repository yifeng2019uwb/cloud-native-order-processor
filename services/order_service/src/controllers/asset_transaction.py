"""
Asset Transaction Controller
Path: services/order_service/src/controllers/asset_transaction.py

Handles asset transaction history endpoints
- GET /assets/{asset_id}/transactions - Get asset transaction history
- GET /assets/transactions/{username}/{asset_id} - Get user's asset transactions
"""
import logging
from datetime import datetime, timezone
from typing import Union
from fastapi import APIRouter, Depends, status, Request

# Import API models
from api_models.asset import (
    GetAssetTransactionsRequest,
    GetAssetTransactionsResponse,
    AssetTransactionData
)
from api_models.shared.common import ErrorResponse

# Import dependencies
from controllers.dependencies import get_current_user, get_asset_transaction_dao_dependency
from common.dao.asset import AssetTransactionDAO

# Import exceptions
from common.exceptions import DatabaseOperationException, EntityNotFoundException
from src.exceptions import InternalServerException, AssetNotFoundException, UserValidationException

logger = logging.getLogger(__name__)
router = APIRouter(tags=["asset-transactions"])


@router.get(
    "/assets/{asset_id}/transactions",
    response_model=Union[GetAssetTransactionsResponse, ErrorResponse],
    responses={
        200: {
            "description": "Asset transactions retrieved successfully",
            "model": GetAssetTransactionsResponse
        },
        401: {
            "description": "Unauthorized",
            "model": ErrorResponse
        },
        404: {
            "description": "Asset not found",
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
async def get_asset_transactions(
    asset_id: str,
    limit: int = 50,
    offset: int = 0,
    request: Request = None,
    current_user: dict = Depends(get_current_user),
    asset_transaction_dao: AssetTransactionDAO = Depends(get_asset_transaction_dao_dependency)
) -> GetAssetTransactionsResponse:
    """
    Get asset transaction history for the authenticated user
    """
    # Log request
    logger.info(
        f"Asset transactions request from {request.client.host if request.client else 'unknown'}",
        extra={
            "username": current_user["username"],
            "asset_id": asset_id,
            "limit": limit,
            "offset": offset,
            "user_agent": request.headers.get("user-agent", "unknown") if request else "unknown",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Get asset transactions for user
        asset_transactions = asset_transaction_dao.get_user_asset_transactions(
            current_user["username"],
            asset_id,
            limit=limit,
            offset=offset
        )

        # Convert to API response format
        transaction_data_list = []
        for transaction in asset_transactions:
            transaction_data = AssetTransactionData(
                asset_id=transaction.asset_id,
                transaction_type=transaction.transaction_type,
                quantity=transaction.quantity,
                price=transaction.price,
                status=transaction.status,
                timestamp=transaction.created_at
            )
            transaction_data_list.append(transaction_data)

        # Determine if there are more transactions
        has_more = len(transaction_data_list) == limit

        logger.info(f"Asset transactions retrieved successfully: user={current_user['username']}, "
                   f"asset={asset_id}, count={len(transaction_data_list)}, has_more={has_more}")

        return GetAssetTransactionsResponse(
            success=True,
            message="Asset transactions retrieved successfully",
            data=transaction_data_list,
            has_more=has_more,
            timestamp=datetime.utcnow()
        )

    except EntityNotFoundException:
        logger.info(f"No asset transactions found: user={current_user['username']}, asset={asset_id}")
        # Return empty list instead of error for no transactions
        return GetAssetTransactionsResponse(
            success=True,
            message="No asset transactions found",
            data=[],
            has_more=False,
            timestamp=datetime.utcnow()
        )
    except DatabaseOperationException as e:
        logger.error(f"Database operation failed for asset transactions: user={current_user['username']}, "
                    f"asset={asset_id}, error={str(e)}")
        raise InternalServerException("Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error during asset transactions retrieval: user={current_user['username']}, "
                    f"asset={asset_id}, error={str(e)}", exc_info=True)
        raise InternalServerException("Service temporarily unavailable")


@router.get(
    "/assets/transactions/{username}/{asset_id}",
    response_model=Union[GetAssetTransactionsResponse, ErrorResponse],
    responses={
        200: {
            "description": "User asset transactions retrieved successfully",
            "model": GetAssetTransactionsResponse
        },
        401: {
            "description": "Unauthorized",
            "model": ErrorResponse
        },
        403: {
            "description": "Forbidden - can only view own transactions",
            "model": ErrorResponse
        },
        404: {
            "description": "Asset not found",
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
async def get_user_asset_transactions(
    username: str,
    asset_id: str,
    limit: int = 50,
    offset: int = 0,
    request: Request = None,
    current_user: dict = Depends(get_current_user),
    asset_transaction_dao: AssetTransactionDAO = Depends(get_asset_transaction_dao_dependency)
) -> GetAssetTransactionsResponse:
    """
    Get specific user's asset transaction history (users can only view their own transactions)
    """
    # Log request
    logger.info(
        f"User asset transactions request from {request.client.host if request.client else 'unknown'}",
        extra={
            "requested_username": username,
            "authenticated_user": current_user["username"],
            "asset_id": asset_id,
            "limit": limit,
            "offset": offset,
            "user_agent": request.headers.get("user-agent", "unknown") if request else "unknown",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Validate user access (users can only view their own transactions)
        if current_user["username"] != username:
            logger.warning(f"Unauthorized transaction access attempt: {current_user['username']} tried to access {username}'s transactions")
            raise UserValidationException("You can only view your own transactions")

        # Get asset transactions for user
        asset_transactions = asset_transaction_dao.get_user_asset_transactions(
            username,
            asset_id,
            limit=limit,
            offset=offset
        )

        # Convert to API response format
        transaction_data_list = []
        for transaction in asset_transactions:
            transaction_data = AssetTransactionData(
                asset_id=transaction.asset_id,
                transaction_type=transaction.transaction_type,
                quantity=transaction.quantity,
                price=transaction.price,
                status=transaction.status,
                timestamp=transaction.created_at
            )
            transaction_data_list.append(transaction_data)

        # Determine if there are more transactions
        has_more = len(transaction_data_list) == limit

        logger.info(f"User asset transactions retrieved successfully: user={username}, "
                   f"asset={asset_id}, count={len(transaction_data_list)}, has_more={has_more}")

        return GetAssetTransactionsResponse(
            success=True,
            message="User asset transactions retrieved successfully",
            data=transaction_data_list,
            has_more=has_more,
            timestamp=datetime.utcnow()
        )

    except UserValidationException:
        # Re-raise validation exceptions
        raise
    except EntityNotFoundException:
        logger.info(f"No user asset transactions found: user={username}, asset={asset_id}")
        # Return empty list instead of error for no transactions
        return GetAssetTransactionsResponse(
            success=True,
            message="No user asset transactions found",
            data=[],
            has_more=False,
            timestamp=datetime.utcnow()
        )
    except DatabaseOperationException as e:
        logger.error(f"Database operation failed for user asset transactions: user={username}, "
                    f"asset={asset_id}, error={str(e)}")
        raise InternalServerException("Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error during user asset transactions retrieval: user={username}, "
                    f"asset={asset_id}, error={str(e)}", exc_info=True)
        raise InternalServerException("Service temporarily unavailable")
