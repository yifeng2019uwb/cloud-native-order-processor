"""
Portfolio Management Controller
Path: services/user_service/src/controllers/portfolio.py

Handles portfolio management endpoints with calculated market values
- GET /portfolio- Get user's complete portfolio
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Union
from fastapi import APIRouter, Depends, status, Request
from common.data.entities.user import User
from api_models.portfolio.portfolio_models import GetPortfolioRequest, GetPortfolioResponse, PortfolioAssetData
from api_models.shared.common import ErrorResponse
from common.data.dao.user.balance_dao import BalanceDAO
from common.data.dao.user.user_dao import UserDAO
from common.data.dao.asset.asset_balance_dao import AssetBalanceDAO
from common.data.dao.inventory.asset_dao import AssetDAO
from common.exceptions import CNOPDatabaseOperationException
from common.exceptions.shared_exceptions import (
    CNOPInternalServerException,
    CNOPUserNotFoundException
)
from common.shared.logging import BaseLogger, Loggers, LogActions
from user_exceptions import CNOPUserValidationException
from api_info_enum import ApiTags, ApiPaths, ApiResponseKeys
from validation_enums import ValidationActions
from constants import (
    MSG_SUCCESS_PORTFOLIO_RETRIEVED, MSG_SUCCESS_ASSET_BALANCE_RETRIEVED
)
from common.shared.constants.request_headers import RequestHeaders, RequestHeaderDefaults
from common.shared.constants.api_responses import APIResponseDescriptions
from common.shared.constants.http_status import HTTPStatus
from common.shared.constants.error_messages import ErrorMessages
from controllers.auth.dependencies import get_current_user
from controllers.dependencies import (
    get_balance_dao_dependency,
    get_asset_balance_dao_dependency, get_user_dao_dependency,
    get_asset_dao_dependency, get_request_id_from_request
)
from validation.business_validators import validate_user_permissions

# Initialize our standardized logger
logger = BaseLogger(Loggers.USER)
router = APIRouter(tags=[ApiTags.PORTFOLIO.value])


@router.get(
    ApiPaths.PORTFOLIO.value,
    response_model=Union[GetPortfolioResponse, ErrorResponse],
    responses={
        HTTPStatus.OK: {
            ApiResponseKeys.DESCRIPTION.value: MSG_SUCCESS_PORTFOLIO_RETRIEVED,
            ApiResponseKeys.MODEL.value: GetPortfolioResponse
        },
        HTTPStatus.UNAUTHORIZED: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_UNAUTHORIZED,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.NOT_FOUND: {
            ApiResponseKeys.DESCRIPTION.value: ErrorMessages.USER_NOT_FOUND,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_VALIDATION,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.SERVICE_UNAVAILABLE: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_SERVICE_UNAVAILABLE,
            ApiResponseKeys.MODEL.value: ErrorResponse
        }
    }
)
def get_user_portfolio(
    request: Request,
    current_user: User = Depends(get_current_user),
    balance_dao: BalanceDAO = Depends(get_balance_dao_dependency),
    asset_balance_dao: AssetBalanceDAO = Depends(get_asset_balance_dao_dependency),
    user_dao: UserDAO = Depends(get_user_dao_dependency),
    asset_dao: AssetDAO = Depends(get_asset_dao_dependency)
) -> GetPortfolioResponse:
    """
    Get user's complete portfolio with calculated market values

    Calculates:
    - Total portfolio value (USD + assets)
    - Individual asset market values
    - Asset allocation percentages
    """
    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)
    username = current_user.username

    # Log portfolio request
    logger.info(
        action=LogActions.REQUEST_START,
        message=f"Portfolio request from {request.client.host if request.client else 'unknown'}",
        user=username,
        request_id=request_id,
        extra={
            "user_agent": request.headers.get(RequestHeaders.USER_AGENT, RequestHeaderDefaults.USER_AGENT_DEFAULT),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Business validation (Layer 2)
        validate_user_permissions(
            username=username,
            action=ValidationActions.VIEW_PORTFOLIO.value,
            user_dao=user_dao
        )

        # Get USD balance
        usd_balance = balance_dao.get_balance(username)
        total_usd = usd_balance.current_balance if usd_balance else Decimal('0')

        # Get all asset balances
        asset_balances = asset_balance_dao.get_all_asset_balances(username)

        # Batch retrieve all assets for market data
        asset_ids = [balance.asset_id for balance in asset_balances]
        assets = asset_dao.get_assets_by_ids(asset_ids)

        # Calculate portfolio data
        portfolio_assets = []
        total_asset_value = Decimal('0')

        for asset_balance in asset_balances:
            # Get asset data from batch retrieval
            asset = assets.get(asset_balance.asset_id)
            if asset:
                current_price = Decimal(str(asset.price_usd))
            else:
                # Fallback for missing assets
                current_price = Decimal('0')

            # Calculate market value
            market_value = asset_balance.quantity * current_price
            total_asset_value += market_value

            # Create portfolio asset data
            portfolio_asset = PortfolioAssetData(
                asset_id=asset_balance.asset_id,
                quantity=asset_balance.quantity,
                current_price=current_price,
                market_value=market_value,
                percentage=Decimal('0')  # Will calculate after total is known
            )
            portfolio_assets.append(portfolio_asset)

        # Calculate total portfolio value
        total_portfolio_value = total_usd + total_asset_value

        # Calculate percentages for each asset
        if total_portfolio_value > 0:
            for asset in portfolio_assets:
                if asset.market_value:
                    asset.percentage = (asset.market_value / total_portfolio_value) * Decimal('100')

        # Create portfolio response data
        portfolio_data = {
            "username": username,
            "usd_balance": total_usd,
            "total_asset_value": total_asset_value,
            "total_portfolio_value": total_portfolio_value,
            "asset_count": len(portfolio_assets),
            "assets": portfolio_assets
        }

        logger.info(
            action=LogActions.REQUEST_END,
            message=f"Portfolio retrieved successfully: total_value={total_portfolio_value}, asset_count={len(portfolio_assets)}",
            user=username,
            request_id=request_id
        )

        return GetPortfolioResponse(
            success=True,
            message=MSG_SUCCESS_PORTFOLIO_RETRIEVED,
            data=portfolio_data,
            timestamp=datetime.utcnow()
        )

    except CNOPUserValidationException:
        # Re-raise validation exceptions
        raise
    except CNOPDatabaseOperationException as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Database operation failed for portfolio: error={str(e)}",
            user=username,
            request_id=request_id
        )
        raise CNOPInternalServerException(ErrorMessages.SERVICE_UNAVAILABLE)
    except Exception as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Unexpected error during portfolio retrieval: error={str(e)}",
            user=username,
            request_id=request_id
        )
        raise CNOPInternalServerException(ErrorMessages.SERVICE_UNAVAILABLE)
