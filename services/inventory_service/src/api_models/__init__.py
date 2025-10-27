"""
API models package for inventory service
"""
from .list_assets import ListAssetsRequest, ListAssetsResponse
from .get_asset import GetAssetRequest, GetAssetResponse
from .shared.data_models import AssetData, AssetDetailData

__all__ = [
    # List assets
    "ListAssetsRequest",
    "ListAssetsResponse",
    # Get asset
    "GetAssetRequest",
    "GetAssetResponse",
    # Shared data models
    "AssetData",
    "AssetDetailData",
]