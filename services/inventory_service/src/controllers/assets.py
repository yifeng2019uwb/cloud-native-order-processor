"""
Assets controller for inventory service
Path: services/inventory-service/src/controllers/assets.py
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, Path
from api_models.list_assets import ListAssetsRequest, ListAssetsResponse
from api_models.get_asset import GetAssetRequest, GetAssetResponse
from api_models.shared.data_models import AssetData, AssetDetailData
from common.data.dao.inventory.asset_dao import AssetDAO
from common.data.database.dependencies import get_asset_dao
from controllers.dependencies import get_request_id_from_request
from common.exceptions.shared_exceptions import CNOPAssetNotFoundException
from common.shared.logging import BaseLogger, LoggerName, LogAction
from common.shared.constants.api_constants import HTTPStatus
from api_info_enum import ApiTags, API_INVENTORY_ROOT, API_ASSETS, API_ASSET_BY_ID
from inventory_exceptions import CNOPAssetValidationException, CNOPInventoryServerException

try:
    from metrics import record_asset_retrieval, record_asset_detail_view, update_asset_counts
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

logger = BaseLogger(LoggerName.INVENTORY)
router = APIRouter(prefix=API_INVENTORY_ROOT, tags=[ApiTags.INVENTORY.value])

STATUS_AVAILABLE = "available"
STATUS_UNAVAILABLE = "unavailable"


def get_asset_request(asset_id: str = Path(..., description="Asset ID")) -> GetAssetRequest:
    """Dependency to create and validate GetAssetRequest from path parameter"""
    return GetAssetRequest(asset_id=asset_id)


@router.get(
    API_ASSETS,
    response_model=ListAssetsResponse
)
def list_assets(
    request: Request,
    filter_params: ListAssetsRequest = Depends(),
    asset_dao: AssetDAO = Depends(get_asset_dao)
) -> ListAssetsResponse:
    """List all available assets with optional filtering"""
    request_id = get_request_id_from_request(request)

    logger.info(
        action=LogAction.REQUEST_START,
        message=f"Assets list requested - active_only: {filter_params.active_only}, limit: {filter_params.limit}",
        request_id=request_id
    )

    try:
        # Get assets from database
        all_assets = asset_dao.get_all_assets(active_only=filter_params.active_only)

        # Apply limit if specified
        if filter_params.limit:
            assets = all_assets[:filter_params.limit]
        else:
            assets = all_assets

        # Get total count
        if filter_params.active_only:
            total_assets = asset_dao.get_all_assets(active_only=False)
            total_count = len(total_assets)
        else:
            total_count = len(all_assets)

        # Convert to response models
        asset_data_list = []
        for item in assets:
            asset_data = AssetData(
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
            asset_data_list.append(asset_data)

        active_count = sum(1 for asset in asset_data_list if asset.is_active)

        logger.info(
            action=LogAction.REQUEST_END,
            message=f"Retrieved {len(assets)} assets (total: {total_count})",
            request_id=request_id
        )

        if METRICS_AVAILABLE:
            record_asset_retrieval(category="all", active_only=filter_params.active_only)
            update_asset_counts(total=total_count, active=len(all_assets))

        return ListAssetsResponse(
            data=asset_data_list,
            total_count=total_count,
            active_count=active_count
        )

    except Exception as e:
        logger.error(
            action=LogAction.ERROR,
            message=f"Failed to list assets: {str(e)}",
            request_id=request_id
        )
        raise CNOPInventoryServerException(f"Failed to list assets: {str(e)}")


@router.get(
    API_ASSET_BY_ID,
    response_model=GetAssetResponse
)
def get_asset(
    request: Request,
    asset_request: GetAssetRequest = Depends(get_asset_request),
    asset_dao: AssetDAO = Depends(get_asset_dao)
) -> GetAssetResponse:
    """Get detailed information about a specific asset"""
    request_id = get_request_id_from_request(request)

    logger.info(
        action=LogAction.REQUEST_START,
        message=f"Asset details requested for: {asset_request.asset_id}",
        request_id=request_id
    )

    try:
        asset_id = asset_request.asset_id

        # Get asset from database (will raise CNOPAssetNotFoundException if not found)
        asset = asset_dao.get_asset_by_id(asset_id)

        logger.info(
            action=LogAction.REQUEST_END,
            message=f"Asset found: {asset.name} ({asset.asset_id})",
            request_id=request_id
        )

        if METRICS_AVAILABLE:
            record_asset_detail_view(asset_id=asset_id)

        availability_status = STATUS_AVAILABLE if asset.is_active else STATUS_UNAVAILABLE
        last_updated = asset.last_updated or datetime.now(timezone.utc).isoformat()

        asset_detail_data = AssetDetailData(
            asset_id=asset.asset_id,
            name=asset.name or '',
            description=asset.description,
            category=asset.category or 'unknown',
            price_usd=float(asset.price_usd),
            is_active=asset.is_active,
            availability_status=availability_status,
            symbol=asset.symbol,
            image=asset.image,
            market_cap_rank=asset.market_cap_rank,
            market_cap=asset.market_cap,
            price_change_24h=asset.price_change_24h,
            price_change_percentage_24h=asset.price_change_percentage_24h,
            price_change_percentage_7d=asset.price_change_percentage_7d,
            price_change_percentage_30d=asset.price_change_percentage_30d,
            high_24h=asset.high_24h,
            low_24h=asset.low_24h,
            total_volume_24h=asset.total_volume_24h,
            circulating_supply=asset.circulating_supply,
            total_supply=asset.total_supply,
            max_supply=asset.max_supply,
            ath=asset.ath,
            ath_change_percentage=asset.ath_change_percentage,
            ath_date=asset.ath_date,
            atl=asset.atl,
            atl_change_percentage=asset.atl_change_percentage,
            atl_date=asset.atl_date,
            last_updated=last_updated
        )

        return GetAssetResponse(data=asset_detail_data)

    except CNOPAssetValidationException:
        raise
    except CNOPAssetNotFoundException:
        raise
    except Exception as e:
        logger.error(
            action=LogAction.ERROR,
            message=f"Failed to get asset {asset_id}: {str(e)}",
            request_id=request_id
        )
        raise CNOPInventoryServerException(f"Failed to get asset {asset_id}: {str(e)}")