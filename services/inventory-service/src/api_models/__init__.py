# services/inventory-service/src/api_models/__init__.py
"""
API models package for inventory service
"""

# Import inventory models
from .inventory.asset_response import (
    AssetResponse,
    AssetDetailResponse,
    asset_to_response,
    asset_to_detail_response
)
from .inventory.asset_list import (
    AssetListRequest,
    AssetListResponse,
    AssetSummary,
    build_asset_list_response,
    build_asset_summary
)

__all__ = [
    # Asset response models
    "AssetResponse",
    "AssetDetailResponse",
    "asset_to_response",
    "asset_to_detail_response",

    # Asset list models
    "AssetListRequest",
    "AssetListResponse",
    "AssetSummary",
    "build_asset_list_response",
    "build_asset_summary"
]