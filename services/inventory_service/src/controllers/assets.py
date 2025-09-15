"""
Assets controller for inventory service
Path: services/inventory-service/src/controllers/assets.py
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from api_models.inventory.asset_response import (
    AssetResponse,
    AssetDetailResponse,
    AssetListResponse,
)
from api_models.inventory.asset_requests import AssetIdRequest
from common.data.dao.inventory.asset_dao import AssetDAO
from common.data.database import get_asset_dao
from common.exceptions.shared_exceptions import CNOPAssetNotFoundException
from common.shared.logging import BaseLogger, Loggers, LogActions
from inventory_exceptions import (
    CNOPAssetValidationException,
    CNOPInventoryServerException
)
from validation.business_validators import validate_asset_exists
try:
    from metrics import record_asset_retrieval, record_asset_detail_view, update_asset_counts
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

# Initialize our standardized logger
logger = BaseLogger(Loggers.INVENTORY)
router = APIRouter(prefix="/inventory", tags=["inventory"])

def build_asset_list(assets: list, request_params, total_count: int) -> AssetListResponse:
    """Simple method to convert DAO dict results to AssetListResponse"""
    asset_responses = []
    for item in assets:
        asset_response = AssetResponse(
            asset_id=item.asset_id,
            name=item.name or '',
            description=item.description,
            category=item.category or 'unknown',
            price_usd=float(item.price_usd),
            is_active=item.is_active,
            symbol=item.symbol,
            image=item.image,
            market_cap_rank=item.market_cap_rank,
            price_change_percentage_24h=item.price_change_percentage_24h
        )
        asset_responses.append(asset_response)

    # Count active assets
    active_count = sum(1 for asset in asset_responses if asset.is_active)

    return AssetListResponse(
        assets=asset_responses,
        total_count=total_count,
        active_count=active_count,
        filters={
            "active_only": request_params.active_only,
            "limit": request_params.limit
        }
    )


@router.get(
    "/assets",
    response_model=AssetListResponse,
    responses={
        200: {
            "description": "Assets retrieved successfully",
            "model": AssetListResponse
        },
        422: {
            "description": "Invalid query parameters"
        },
        500: {
            "description": "Internal server error"
        }
    }
)
def list_assets(
    active_only: Optional[bool] = Query(
        True,
        description="Show only active assets"
    ),
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=250,
        description="Maximum number of assets to return (1-250)"
    ),
    asset_dao: AssetDAO = Depends(get_asset_dao)
) -> AssetListResponse:
    """
    List all available assets with optional filtering

    - **active_only**: Filter to show only active assets (default: true)
    - **limit**: Maximum number of results to return (1-250)
    """
    try:
        logger.info(action=LogActions.REQUEST_START, message=f"Assets list requested - active_only: {active_only}, limit: {limit}")

        # Create simple request object for validation
        class RequestParams:
            def __init__(self, active_only, limit):
                self.active_only = active_only
                self.limit = limit

        request_params = RequestParams(active_only=active_only, limit=limit)

        # Get assets from database
        all_assets = asset_dao.get_all_assets(active_only=active_only)

        # Apply limit if specified
        if limit:
            assets = all_assets[:limit]
        else:
            assets = all_assets

        # Get total count for metadata
        if active_only:
            total_assets = asset_dao.get_all_assets(active_only=False)
            total_count = len(total_assets)
        else:
            total_count = len(all_assets)

        logger.info(action=LogActions.REQUEST_END, message=f"Retrieved {len(assets)} assets (total: {total_count})")

        # Record metrics if available
        if METRICS_AVAILABLE:
            record_asset_retrieval(category="all", active_only=active_only)
            update_asset_counts(total=total_count, active=len(all_assets))

        # Build response using simple helper function
        return build_asset_list(
            assets=assets,
            request_params=request_params,
            total_count=total_count
        )

    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Failed to list assets: {str(e)}")
        # Convert to internal server exception for proper handling
        raise CNOPInventoryServerException(f"Failed to list assets: {str(e)}")


@router.get(
    "/assets/{asset_id}",
    response_model=AssetDetailResponse,
    responses={
        200: {
            "description": "Asset retrieved successfully",
            "model": AssetDetailResponse
        },
        404: {
            "description": "Asset not found"
        },
        422: {
            "description": "Validation error"
        },
        500: {
            "description": "Internal server error"
        }
    }
)
def get_asset_by_id(
    asset_id: str,
    asset_dao: AssetDAO = Depends(get_asset_dao)
) -> AssetDetailResponse:
    """
    Get detailed information about a specific asset

    Layer 1: Field validation handled by AssetIdRequest model
    Layer 2: Business validation (existence checks, etc.)

    - **asset_id**: The asset symbol/identifier (e.g., "BTC", "ETH")
    """
    try:
        logger.info(action=LogActions.REQUEST_START, message=f"Asset details requested for: {asset_id}")

        # Layer 1: Field validation using AssetIdRequest model
        try:
            validated_request = AssetIdRequest(asset_id=asset_id)
            validated_asset_id = validated_request.asset_id
        except Exception as validation_error:
            logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Field validation failed for asset_id '{asset_id}': {str(validation_error)}")
            # Re-raise the original validation error without wrapping
            raise

        # Layer 2: Business validation - check if asset exists
        validate_asset_exists(validated_asset_id, asset_dao)

        # Get asset from database (already validated to exist)
        asset = asset_dao.get_asset_by_id(validated_asset_id)

        logger.info(action=LogActions.REQUEST_END, message=f"Asset found: {asset.name} ({asset.asset_id})")

        # Record metrics if available
        if METRICS_AVAILABLE:
            record_asset_detail_view(asset_id=validated_asset_id)

        # Convert to detailed response model with all comprehensive fields
        availability_status = "available" if asset.is_active else "unavailable"
        last_updated = asset.last_updated or datetime.utcnow().isoformat()

        return AssetDetailResponse(
            asset_id=asset.asset_id,
            name=asset.name or '',
            description=asset.description,
            category=asset.category or 'unknown',
            price_usd=float(asset.price_usd),
            is_active=asset.is_active,
            availability_status=availability_status,

            # Enhanced fields for detailed view
            symbol=asset.symbol,
            image=asset.image,
            market_cap_rank=asset.market_cap_rank,

            # Comprehensive market data
            market_cap=asset.market_cap,
            price_change_24h=asset.price_change_24h,
            price_change_percentage_24h=asset.price_change_percentage_24h,
            price_change_percentage_7d=asset.price_change_percentage_7d,
            price_change_percentage_30d=asset.price_change_percentage_30d,

            # Price range analysis
            high_24h=asset.high_24h,
            low_24h=asset.low_24h,

            # Volume and trading metrics
            total_volume_24h=asset.total_volume_24h,

            # Supply analysis
            circulating_supply=asset.circulating_supply,
            total_supply=asset.total_supply,
            max_supply=asset.max_supply,

            # Historical context
            ath=asset.ath,
            ath_change_percentage=asset.ath_change_percentage,
            ath_date=asset.ath_date,
            atl=asset.atl,
            atl_change_percentage=asset.atl_change_percentage,
            atl_date=asset.atl_date,

            # Additional metadata
            last_updated=last_updated
        )

    except CNOPAssetValidationException as e:
        # Handle validation errors (from API model) - re-raise as-is to maintain clean error messages
        logger.warning(action=LogActions.VALIDATION_ERROR, message=f"Validation error for asset_id '{asset_id}': {str(e)}")
        raise
    except CNOPAssetNotFoundException as e:
        # Handle business validation errors (asset not found) - re-raise as-is
        logger.warning(action=LogActions.ERROR, message=f"Asset not found: {asset_id}")
        raise
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Failed to get asset {asset_id}: {str(e)}")
        # Convert to internal server exception for proper handling
        raise CNOPInventoryServerException(f"Failed to get asset {asset_id}: {str(e)}")
