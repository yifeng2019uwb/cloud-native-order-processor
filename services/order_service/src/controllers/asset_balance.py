"""
Asset Balance Controller
Path: services/order_service/src/controllers/asset_balance.py

Handles asset balance management endpoints
- GET /assets/balances - Get all asset balances for user
- GET /assets/{asset_id}/balance - Get specific asset balance
"""
import logging
from datetime import datetime, timezone
from typing import Union
from fastapi import APIRouter, Depends, status, Request

# Import API models
from api_models.asset import (
    GetAssetBalanceRequest, GetAssetBalancesRequest,
    GetAssetBalanceResponse, GetAssetBalancesResponse,
    AssetBalanceData
)
from api_models.shared.common import ErrorResponse

# Import dependencies
from controllers.dependencies import (
    get_current_user, get_asset_balance_dao_dependency,
    get_user_dao_dependency
)
from common.dao.asset import AssetBalanceDAO
from common.dao.user import UserDAO

# Import business validators
from validation.business_validators import validate_user_permissions

# Import exceptions
from common.exceptions import (
    DatabaseOperationException,
    EntityNotFoundException,
    InternalServerException,
    AssetNotFoundException
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["asset-balances"])


@router.get(
    "/assets/balances",
    response_model=Union[GetAssetBalancesResponse, ErrorResponse],
    responses={
        200: {
            "description": "Asset balances retrieved successfully",
            "model": GetAssetBalancesResponse
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
            "description": "Service temporarily unavailable",
            "model": ErrorResponse
        }
    }
)
async def get_user_asset_balances(
    request: Request,
    current_user: dict = Depends(get_current_user),
    asset_balance_dao: AssetBalanceDAO = Depends(get_asset_balance_dao_dependency),
    user_dao: UserDAO = Depends(get_user_dao_dependency)
) -> GetAssetBalancesResponse:
    """
    Get all asset balances for the authenticated user
    """
    # Log request
    logger.info(
        f"Asset balances request from {request.client.host if request.client else 'unknown'}",
        extra={
            "username": current_user["username"],
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Business validation (Layer 2)
        validate_user_permissions(
            username=current_user["username"],
            action="view_asset_balances",
            user_dao=user_dao
        )

        # Get all asset balances for user
        asset_balances = asset_balance_dao.get_all_asset_balances(current_user["username"])

        # Convert to API response format
        balance_data_list = []
        for balance in asset_balances:
            balance_data = AssetBalanceData(
                asset_id=balance.asset_id,
                quantity=balance.quantity,
                created_at=balance.created_at,
                updated_at=balance.updated_at
            )
            balance_data_list.append(balance_data)

        logger.info(f"Asset balances retrieved successfully: user={current_user['username']}, "
                   f"asset_count={len(balance_data_list)}")

        return GetAssetBalancesResponse(
            success=True,
            message="Asset balances retrieved successfully",
            data=balance_data_list,
            timestamp=datetime.utcnow()
        )

    except DatabaseOperationException as e:
        logger.error(f"Database operation failed for asset balances: user={current_user['username']}, error={str(e)}")
        raise InternalServerException("Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error during asset balances retrieval: user={current_user['username']}, error={str(e)}", exc_info=True)
        raise InternalServerException("Service temporarily unavailable")


@router.get(
    "/assets/{asset_id}/balance",
    response_model=Union[GetAssetBalanceResponse, ErrorResponse],
    responses={
        200: {
            "description": "Asset balance retrieved successfully",
            "model": GetAssetBalanceResponse
        },
        401: {
            "description": "Unauthorized",
            "model": ErrorResponse
        },
        404: {
            "description": "Asset balance not found",
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
async def get_user_asset_balance(
    asset_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    asset_balance_dao: AssetBalanceDAO = Depends(get_asset_balance_dao_dependency),
    user_dao: UserDAO = Depends(get_user_dao_dependency)
) -> GetAssetBalanceResponse:
    """
    Get specific asset balance for the authenticated user
    """
    # Log request
    logger.info(
        f"Asset balance request from {request.client.host if request.client else 'unknown'}",
        extra={
            "username": current_user["username"],
            "asset_id": asset_id,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Business validation (Layer 2)
        validate_user_permissions(
            username=current_user["username"],
            action="view_asset_balance",
            user_dao=user_dao
        )

        # Get specific asset balance for user
        asset_balance = asset_balance_dao.get_asset_balance(current_user["username"], asset_id)

        # Convert to API response format
        balance_data = AssetBalanceData(
            asset_id=asset_balance.asset_id,
            quantity=asset_balance.quantity,
            created_at=asset_balance.created_at,
            updated_at=asset_balance.updated_at
        )

        logger.info(f"Asset balance retrieved successfully: user={current_user['username']}, "
                   f"asset={asset_id}, quantity={asset_balance.quantity}")

        return GetAssetBalanceResponse(
            success=True,
            message="Asset balance retrieved successfully",
            data=balance_data,
            timestamp=datetime.utcnow()
        )

    except EntityNotFoundException:
        logger.info(f"Asset balance not found: user={current_user['username']}, asset={asset_id}")
        raise AssetNotFoundException(f"Asset balance for {asset_id} not found")
    except DatabaseOperationException as e:
        logger.error(f"Database operation failed for asset balance: user={current_user['username']}, "
                    f"asset={asset_id}, error={str(e)}")
        raise InternalServerException("Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error during asset balance retrieval: user={current_user['username']}, "
                    f"asset={asset_id}, error={str(e)}", exc_info=True)
        raise InternalServerException("Service temporarily unavailable")
