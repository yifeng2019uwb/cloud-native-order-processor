# services/inventory-service/src/api_models/__init__.py
"""
API models package for inventory service
"""

# Import inventory models
from .inventory.asset_response import (
    AssetResponse,
    AssetDetailResponse,
    AssetListResponse,
)

__all__ = [
    # Asset response models
    "AssetResponse",
    "AssetDetailResponse",
    "AssetListResponse",
]