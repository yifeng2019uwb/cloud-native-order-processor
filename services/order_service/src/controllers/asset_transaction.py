"""
Asset Transaction Controller
Path: services/order_service/src/controllers/asset_transaction.py

Handles asset transaction history endpoints
- GET /assets/{asset_id}/transactions - Get asset transaction history
"""
import logging
from datetime import datetime, timezone
from typing import Union
from fastapi import APIRouter, Depends, status, Request

# Import API models
from api_models.asset import (
    GetAssetTransactionsResponse,
    AssetTransactionData
)
from api_models.shared.common import ErrorResponse

# Import dependencies
from controllers.dependencies import (
    get_current_user, get_asset_transaction_dao_dependency,
    get_asset_dao_dependency, get_user_dao_dependency
)
from common.dao.asset import AssetTransactionDAO
from common.dao.inventory import AssetDAO
from common.dao.user import UserDAO

# Import business validators
from validation.business_validators import validate_order_history_business_rules

# Import exceptions
from common.exceptions import (
    DatabaseOperationException,
    EntityNotFoundException,
    InternalServerException,
    AssetNotFoundException,
    UserValidationException
)

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
    asset_transaction_dao: AssetTransactionDAO = Depends(get_asset_transaction_dao_dependency),
    asset_dao: AssetDAO = Depends(get_asset_dao_dependency),
    user_dao: UserDAO = Depends(get_user_dao_dependency)
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
        # Business validation (Layer 2)
        validate_order_history_business_rules(
            asset_id=asset_id,
            username=current_user["username"],
            asset_dao=asset_dao,
            user_dao=user_dao
        )

        # Get asset transactions for user
        asset_transactions = asset_transaction_dao.get_user_asset_transactions(
            current_user["username"],
            asset_id,
            limit=limit
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
