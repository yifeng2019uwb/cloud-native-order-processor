"""
Portfolio Management Controller
Path: services/order_service/src/controllers/portfolio.py

Handles portfolio management endpoints with calculated market values
- GET /portfolio/{username} - Get user's complete portfolio
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Union
from fastapi import APIRouter, Depends, status, Request
from api_models.asset import GetPortfolioRequest, GetPortfolioResponse, PortfolioAssetData
from api_models.shared.common import ErrorResponse
from common.data.dao.user import BalanceDAO, UserDAO
from common.data.dao.asset import AssetBalanceDAO
from common.data.dao.inventory import AssetDAO
from common.exceptions import CNOPDatabaseOperationException
from common.exceptions.shared_exceptions import (
    CNOPInternalServerException,
    CNOPUserNotFoundException
)
from common.shared.logging import BaseLogger, Loggers, LogActions
from order_exceptions import CNOPOrderValidationException
from controllers.dependencies import (
    get_current_user, get_balance_dao_dependency,
    get_asset_balance_dao_dependency, get_user_dao_dependency,
    get_asset_dao_dependency
)
from validation.business_validators import validate_user_permissions

# Initialize our standardized logger
logger = BaseLogger(Loggers.ORDER)
router = APIRouter(tags=["portfolio"])


@router.get(
    "/portfolio/{username}",
    response_model=Union[GetPortfolioResponse, ErrorResponse],
    responses={
        200: {
            "description": "Portfolio retrieved successfully",
            "model": GetPortfolioResponse
        },
        401: {
            "description": "Unauthorized",
            "model": ErrorResponse
        },
        404: {
            "description": "User not found",
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
def get_user_portfolio(
    username: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
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
    # Log portfolio request
    logger.info(
        action=LogActions.REQUEST_START,
        message=f"Portfolio request from {request.client.host if request.client else 'unknown'}",
        user=current_user["username"],
        extra={
            "requested_username": username,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Business validation (Layer 2)
        validate_user_permissions(
            username=username,
            action="view_portfolio",
            user_dao=user_dao
        )

        # Validate user access (users can only view their own portfolio)
        if current_user["username"] != username:
            logger.warning(
                action=LogActions.ACCESS_DENIED,
                message=f"Unauthorized portfolio access attempt: tried to access {username}'s portfolio",
                user=current_user['username']
            )
            raise CNOPOrderValidationException("You can only view your own portfolio")

        # Get USD balance
        usd_balance = balance_dao.get_balance(username)
        total_usd = usd_balance.current_balance if usd_balance else Decimal('0')

        # Get all asset balances
        asset_balances = asset_balance_dao.get_all_asset_balances(username)

        # Calculate portfolio data
        portfolio_assets = []
        total_asset_value = Decimal('0')

        for asset_balance in asset_balances:
            # Get current market price from real-time service
            from controllers.dependencies import get_current_market_price
            current_price = get_current_market_price(asset_balance.asset_id, asset_dao)

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
            user=username
        )

        return GetPortfolioResponse(
            success=True,
            message="Portfolio retrieved successfully",
            data=portfolio_data,
            timestamp=datetime.utcnow()
        )

    except CNOPOrderValidationException:
        # Re-raise validation exceptions
        raise
    except CNOPDatabaseOperationException as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Database operation failed for portfolio: error={str(e)}",
            user=username
        )
        raise CNOPInternalServerException("Service temporarily unavailable")
    except Exception as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Unexpected error during portfolio retrieval: error={str(e)}",
            user=username
        )
        raise CNOPInternalServerException("Service temporarily unavailable")
