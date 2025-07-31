"""
Assets controller for inventory service
Path: services/inventory-service/src/controllers/assets.py
"""
from fastapi import APIRouter, Depends, Query, status
from typing import Optional
import logging
from datetime import datetime, timezone

# Import API models
from api_models.inventory.asset_response import (
    AssetDetailResponse,
    asset_to_detail_response
)
from api_models.inventory.asset_list import (
    AssetListRequest,
    AssetListResponse,
    build_asset_list_response
)

# Import common DAO
from common.dao.asset_dao import AssetDAO
from common.database import get_asset_dao

# Import internal exceptions
from exceptions import (
    AssetNotFoundException,
    InternalServerException,
    DatabaseOperationException
)

# Import metrics
try:
    from metrics import record_asset_retrieval, record_asset_detail_view, update_asset_counts
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/inventory", tags=["inventory"])





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
async def list_assets(
    active_only: Optional[bool] = Query(
        True,
        description="Show only active assets"
    ),
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description="Maximum number of assets to return (1-100)"
    ),
    asset_dao: AssetDAO = Depends(get_asset_dao)
) -> AssetListResponse:
    """
    List all available assets with optional filtering

    - **active_only**: Filter to show only active assets (default: true)
    - **limit**: Maximum number of results to return (1-100)
    """
    try:
        logger.info(f"Assets list requested - active_only: {active_only}, limit: {limit}")

        # Create request object for validation
        request_params = AssetListRequest(
            active_only=active_only,
            limit=limit
        )

        # Get assets from database
        all_assets = await asset_dao.get_all_assets(active_only=active_only)

        # Apply limit if specified
        if limit:
            assets = all_assets[:limit]
        else:
            assets = all_assets

        # Get total count for metadata
        if active_only:
            total_assets = await asset_dao.get_all_assets(active_only=False)
            total_count = len(total_assets)
        else:
            total_count = len(all_assets)

        logger.info(f"Retrieved {len(assets)} assets (total: {total_count})")

        # Record metrics if available
        if METRICS_AVAILABLE:
            record_asset_retrieval(category="all", active_only=active_only)
            update_asset_counts(total=total_count, active=len(all_assets))

        # Build response using helper function
        return build_asset_list_response(
            assets=assets,
            request_params=request_params,
            total_count=total_count,
            available_categories=[]  # Remove category exposure
        )

    except Exception as e:
        logger.error(f"Failed to list assets: {str(e)}", exc_info=True)
        # Convert to internal server exception for proper handling
        raise InternalServerException(f"Failed to list assets: {str(e)}")


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
        500: {
            "description": "Internal server error"
        }
    }
)
async def get_asset_by_id(
    asset_id: str,
    asset_dao: AssetDAO = Depends(get_asset_dao)
) -> AssetDetailResponse:
    """
    Get detailed information about a specific asset

    - **asset_id**: The asset symbol/identifier (e.g., "BTC", "ETH")
    """
    try:
        logger.info(f"Asset details requested for: {asset_id}")

        # Get asset from database
        asset = await asset_dao.get_asset_by_id(asset_id.upper())

        if not asset:
            logger.warning(f"Asset not found: {asset_id}")
            # Use internal exception for proper handling
            raise AssetNotFoundException(f"Asset '{asset_id}' not found")

        logger.info(f"Asset found: {asset.name} ({asset.asset_id})")

        # Record metrics if available
        if METRICS_AVAILABLE:
            record_asset_detail_view(asset_id=asset_id)

        # Convert to detailed response model
        return asset_to_detail_response(asset)

    except Exception as e:
        logger.error(f"Failed to get asset {asset_id}: {str(e)}", exc_info=True)
        # Convert to internal server exception for proper handling
        raise InternalServerException(f"Failed to get asset {asset_id}: {str(e)}")