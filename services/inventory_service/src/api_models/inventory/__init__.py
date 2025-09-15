"""
Inventory service API models package
"""


# Asset response models
from .asset_response import (
    AssetResponse,
    AssetDetailResponse,
    AssetListResponse,
)

# Asset request models
from .asset_requests import AssetIdRequest

__all__ = [
    # Asset responses
    'AssetResponse',
    'AssetDetailResponse',
    'AssetListResponse',

    # Asset requests
    'AssetIdRequest'
]
