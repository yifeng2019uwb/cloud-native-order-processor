"""
Inventory service API models package
"""

# Asset list models
from .asset_list import (
    AssetListRequest,
    AssetListResponse,
    AssetSummary,
    build_asset_list_response,
    build_asset_summary
)

# Asset response models
from .asset_response import (
    AssetResponse,
    AssetDetailResponse,
    asset_to_response,
    asset_to_detail_response
)

# Asset request models
from .asset_requests import AssetIdRequest

__all__ = [
    # Asset list
    'AssetListRequest',
    'AssetListResponse',
    'AssetSummary',
    'build_asset_list_response',
    'build_asset_summary',

    # Asset responses
    'AssetResponse',
    'AssetDetailResponse',
    'asset_to_response',
    'asset_to_detail_response',

    # Asset requests
    'AssetIdRequest'
]
