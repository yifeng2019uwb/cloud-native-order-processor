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
    get_user_dao_dependency, get_asset_dao_dependency
)
from common.data.dao.asset import AssetBalanceDAO
from common.data.dao.user import UserDAO
from common.data.dao.inventory import AssetDAO


# Import business validators
from validation.business_validators import validate_user_permissions

# Import exceptions
from order_exceptions import (
    CNOPOrderValidationException,
)
# Import internal exceptions (from common.exceptions - internal use only)
from common.exceptions import (
    CNOPEntityNotFoundException,
    CNOPDatabaseOperationException,
    CNOPInternalServerException
)
# Import shared external exceptions (from common.exceptions.shared_exceptions - external use)
from common.exceptions.shared_exceptions import (
    CNOPAssetNotFoundException
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["asset-balances"])


def get_real_market_data(asset_dao: AssetDAO, asset_id: str) -> dict:
    """Get real market data (name and price) from database"""
    try:
        asset = asset_dao.get_asset_by_id(asset_id)
        if asset:
            return {
                "asset_name": asset.name,
                "current_price": float(asset.price_usd)
            }
        else:
            # Fallback to asset_id if not found in database
            return {
                "asset_name": asset_id,
                "current_price": 0.0
            }
    except Exception as e:
        logger.warning(f"Failed to fetch market data for {asset_id}: {str(e)}")
        # Fallback to asset_id if database query fails
        return {
            "asset_name": asset_id,
            "current_price": 0.0
        }


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
def get_user_asset_balances(
    request: Request,
    current_user: dict = Depends(get_current_user),
    asset_balance_dao: AssetBalanceDAO = Depends(get_asset_balance_dao_dependency),
    user_dao: UserDAO = Depends(get_user_dao_dependency),
    asset_dao: AssetDAO = Depends(get_asset_dao_dependency)
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

        # Convert to API response format with real market data
        balance_data_list = []
        for balance in asset_balances:
            # Get real market data from database
            market_data = get_real_market_data(asset_dao, balance.asset_id)
            asset_name = market_data["asset_name"]
            current_price = market_data["current_price"]
            total_value = float(balance.quantity) * current_price

            balance_data = AssetBalanceData(
                asset_id=balance.asset_id,
                asset_name=asset_name,
                quantity=balance.quantity,
                current_price=current_price,
                total_value=total_value,
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

    except CNOPDatabaseOperationException as e:
        logger.error(f"Database operation failed for asset balances: user={current_user['username']}, error={str(e)}")
        raise CNOPInternalServerException("Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error during asset balances retrieval: user={current_user['username']}, error={str(e)}", exc_info=True)
        raise CNOPInternalServerException("Service temporarily unavailable")


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
def get_user_asset_balance(
    asset_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    asset_balance_dao: AssetBalanceDAO = Depends(get_asset_balance_dao_dependency),
    user_dao: UserDAO = Depends(get_user_dao_dependency),
    asset_dao: AssetDAO = Depends(get_asset_balance_dao_dependency)
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
        # Layer 1: Field validation using GetAssetBalanceRequest model
        try:
            validated_request = GetAssetBalanceRequest(asset_id=asset_id)
            validated_asset_id = validated_request.asset_id
        except Exception as validation_error:
            logger.warning(f"Field validation failed for asset_id '{asset_id}': {str(validation_error)}")
            # Re-raise the original validation error without wrapping
            raise

        # Business validation (Layer 2)
        validate_user_permissions(
            username=current_user["username"],
            action="view_asset_balance",
            user_dao=user_dao
        )

        # Get specific asset balance for user
        asset_balance = asset_balance_dao.get_asset_balance(current_user["username"], validated_asset_id)

        # Convert to API response format with real market data
        # Get real market data from database
        market_data = get_real_market_data(asset_dao, asset_balance.asset_id)
        asset_name = market_data["asset_name"]
        current_price = market_data["current_price"]
        total_value = float(asset_balance.quantity) * current_price

        balance_data = AssetBalanceData(
            asset_id=asset_balance.asset_id,
            asset_name=asset_name,
            quantity=asset_balance.quantity,
            current_price=current_price,
            total_value=total_value,
            created_at=asset_balance.created_at,
            updated_at=asset_balance.updated_at
        )

        logger.info(f"Asset balance retrieved successfully: user={current_user['username']}, "
                   f"asset={validated_asset_id}, quantity={asset_balance.quantity}")

        return GetAssetBalanceResponse(
            success=True,
            message="Asset balance retrieved successfully",
            data=balance_data,
            timestamp=datetime.utcnow()
        )

    except CNOPOrderValidationException as e:
        # Handle field validation errors - maintain consistent message format
        logger.warning(f"Validation error for asset_id '{asset_id}': {str(e)}")
        raise CNOPOrderValidationException(f"Invalid asset ID: {str(e)}")
    except CNOPEntityNotFoundException:
        logger.info(f"Asset balance not found: user={current_user['username']}, asset={asset_id}")
        raise CNOPAssetNotFoundException(f"Asset balance for {asset_id} not found")
    except CNOPDatabaseOperationException as e:
        logger.error(f"Database operation failed for asset balance: user={current_user['username']}, "
                    f"asset={asset_id}, error={str(e)}")
        raise CNOPInternalServerException("Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error during asset balance retrieval: user={current_user['username']}, "
                    f"asset={asset_id}, error={str(e)}", exc_info=True)
        raise CNOPInternalServerException("Service temporarily unavailable")
