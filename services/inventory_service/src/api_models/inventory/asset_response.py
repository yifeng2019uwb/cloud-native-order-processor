"""
Asset response models for inventory service API
Path: services/inventory-service/src/api_models/inventory/asset_response.py
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class AssetResponse(BaseModel):
    """Public asset response model - safe for client consumption"""

    asset_id: str = Field(
        ...,
        description="Asset symbol/identifier",
        example="BTC"
    )

    name: str = Field(
        ...,
        description="Asset display name",
        example="Bitcoin"
    )

    description: Optional[str] = Field(
        None,
        description="Asset description",
        example="Digital currency and store of value"
    )

    category: str = Field(
        ...,
        description="Asset category",
        example="major"
    )

    price_usd: float = Field(
        ...,
        description="Current USD price",
        example=45000.50
    )

    is_active: bool = Field(
        ...,
        description="Whether asset is available for viewing/ordering",
        example=True
    )

    # Note: We exclude 'amount' (inventory quantity) from public response for security
    # Note: We exclude created_at/updated_at as they're not needed for public viewing

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC",
                "name": "Bitcoin",
                "description": "Digital currency and store of value",
                "category": "major",
                "price_usd": 45000.50,
                "is_active": True
            }
        }
    )


class AssetDetailResponse(BaseModel):
    """Detailed asset response for individual asset lookup"""

    asset_id: str = Field(
        ...,
        description="Asset symbol/identifier"
    )

    name: str = Field(
        ...,
        description="Asset display name"
    )

    description: Optional[str] = Field(
        None,
        description="Detailed asset description"
    )

    category: str = Field(
        ...,
        description="Asset category"
    )

    price_usd: float = Field(
        ...,
        description="Current USD price"
    )

    is_active: bool = Field(
        ...,
        description="Whether asset is available"
    )

    # For individual asset view, we can show availability status without exact amounts
    availability_status: str = Field(
        ...,
        description="Human-readable availability status",
        example="Available"
    )

    # Additional metadata for detailed view
    last_updated: datetime = Field(
        ...,
        description="Last time asset data was updated"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "BTC",
                "name": "Bitcoin",
                "description": "Digital currency and store of value",
                "category": "major",
                "price_usd": 45000.50,
                "is_active": True,
                "availability_status": "Available",
                "last_updated": "2025-07-09T10:30:00Z"
            }
        }
    )


class AssetListResponse(BaseModel):
    """Response model for asset list endpoint with metadata"""

    assets: list[AssetResponse] = Field(
        ...,
        description="List of available assets"
    )

    total_count: int = Field(
        ...,
        description="Total number of assets"
    )

    active_count: int = Field(
        ...,
        description="Number of active assets"
    )

    categories: list[str] = Field(
        ...,
        description="Available categories for filtering"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "assets": [
                    {
                        "asset_id": "BTC",
                        "name": "Bitcoin",
                        "description": "Digital currency and store of value",
                        "category": "major",
                        "price_usd": 45000.50,
                        "is_active": True
                    },
                    {
                        "asset_id": "ETH",
                        "name": "Ethereum",
                        "description": "Decentralized platform for smart contracts",
                        "category": "major",
                        "price_usd": 3000.25,
                        "is_active": True
                    }
                ],
                "total_count": 12,
                "active_count": 10,
                "categories": ["major", "altcoin", "stablecoin"]
            }
        }


# Helper function to convert DAO Asset model to API response model
def asset_to_response(asset) -> AssetResponse:
    """Convert common.entities.inventory.Asset to AssetResponse"""
    return AssetResponse(
        asset_id=asset.asset_id,
        name=asset.name,
        description=asset.description,
        category=asset.category,
        price_usd=asset.price_usd,
        is_active=asset.is_active
    )


def asset_to_detail_response(asset) -> AssetDetailResponse:
    """Convert common.entities.inventory.Asset to AssetDetailResponse"""
    # Determine availability status based on amount and active status
    if not asset.is_active:
        availability_status = "unavailable"
    elif asset.amount <= 0:
        availability_status = "out_of_stock"
    elif asset.amount < 10:  # Arbitrary threshold for "limited"
        availability_status = "limited"
    else:
        availability_status = "available"

    # Use current time if asset doesn't have updated_at field
    from datetime import datetime, timezone
    last_updated = getattr(asset, 'updated_at', datetime.now(timezone.utc))

    return AssetDetailResponse(
        asset_id=asset.asset_id,
        name=asset.name,
        description=asset.description,
        category=asset.category,
        price_usd=asset.price_usd,
        is_active=asset.is_active,
        availability_status=availability_status,
        last_updated=last_updated
    )