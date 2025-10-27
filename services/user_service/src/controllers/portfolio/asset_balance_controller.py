"""
Asset Balance Controller

Handles single asset balance operations for authenticated users.
Only includes the single asset balance API (GET /balance/asset/{asset_id}).
"""

from datetime import datetime, UTC
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from common.data.entities.user import User
from common.shared.constants.api_constants import HTTPStatus
from common.shared.constants.api_constants import ErrorMessages

from api_models.portfolio.portfolio_models import (
    GetAssetBalanceResponse
)
from controllers.auth.dependencies import get_current_user
from controllers.dependencies import (
    get_user_dao_dependency,
    get_balance_dao_dependency,
    get_asset_balance_dao_dependency,
    get_asset_dao_dependency
)
from validation.business_validators import validate_user_permissions
from common.shared.logging import BaseLogger, LogAction, LoggerName
from user_exceptions import CNOPUserValidationException
from common.exceptions.shared_exceptions import CNOPAssetBalanceNotFoundException
from api_info_enum import ApiTags, ApiPaths
from validation_enums import ValidationActions

# Initialize logger
logger = BaseLogger(LoggerName.USER, log_to_file=True)

# Create router
router = APIRouter(tags=[ApiTags.ASSET_BALANCE.value])

@router.get(ApiPaths.ASSET_BALANCE.value, response_model=GetAssetBalanceResponse)
def get_user_asset_balance(
    current_user: User = Depends(get_current_user),
    user_dao = Depends(get_user_dao_dependency),
    balance_dao = Depends(get_balance_dao_dependency),
    asset_balance_dao = Depends(get_asset_balance_dao_dependency),
    asset_dao = Depends(get_asset_dao_dependency),
    asset_id: str = Path(..., description="Asset identifier", min_length=3)
):
    """
    Get single asset balance for authenticated user

    SYNC OPERATION: Read-only operation, no locks needed.
    FastAPI runs in thread pool automatically.

    Args:
        asset_id: Asset identifier from path
        current_user: Authenticated user data from JWT
        user_dao: User data access object
        balance_dao: Balance data access object
        asset_balance_dao: Asset balance data access object
        asset_dao: Asset data access object

    Returns:
        GetAssetBalanceResponse: Single asset balance data

    Raises:
        HTTPException: If asset not found or validation fails
    """
    try:
        username = current_user.username

        # Validate user permissions
        validate_user_permissions(username, ValidationActions.GET_ASSET_BALANCE.value, user_dao)

        logger.info(
            action=LogAction.REQUEST_START,
            message=f"Getting asset balance for user '{username}', asset '{asset_id}'"
        )

        # Get user's asset balance
        balance = asset_balance_dao.get_asset_balance(username, asset_id)
        if not balance:
            logger.warning(
                action=LogAction.VALIDATION_ERROR,
                message=f"Asset balance not found for user '{username}', asset '{asset_id}'"
            )
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=ErrorMessages.RESOURCE_NOT_FOUND
            )

        # Get current market price for the asset
        try:
            asset = asset_dao.get_asset_by_id(asset_id)
            current_price = float(asset.current_price)
        except Exception as e:
            logger.warning(
                action=LogAction.ERROR,
                message=f"Failed to get current price for asset '{asset_id}': {e}. Using 0.0"
            )
            current_price = 0.0

        # Calculate total value
        total_value = float(balance.quantity) * current_price

        # Create response data
        response = GetAssetBalanceResponse(
            asset_id=balance.asset_id,
            asset_name=asset.name if 'asset' in locals() else balance.asset_id,
            quantity=balance.quantity,
            current_price=current_price,
            total_value=total_value,
            created_at=balance.created_at,
            updated_at=balance.updated_at
        )

        logger.info(
            action=LogAction.REQUEST_END,
            message=f"Successfully retrieved asset balance for user '{username}', asset '{asset_id}'"
        )

        return response

    except CNOPUserValidationException as e:
        logger.warning(
            action=LogAction.VALIDATION_ERROR,
            message=f"Validation error getting asset balance: {e}"
        )
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=str(e)
        )
    except CNOPAssetBalanceNotFoundException as e:
        logger.warning(
            action=LogAction.VALIDATION_ERROR,
            message=f"Asset balance not found for user '{username}', asset '{asset_id}'"
        )
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessages.RESOURCE_NOT_FOUND
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            action=LogAction.ERROR,
            message=f"Unexpected error getting asset balance for user '{username}', asset '{asset_id}': {e}"
        )
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.INTERNAL_SERVER_ERROR
        )
