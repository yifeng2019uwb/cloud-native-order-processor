"""
Asset list request and response models for inventory service API
Path: services/inventory-service/src/api_models/inventory/asset_list.py
"""
from pydantic import BaseModel, Field
from typing import Optional

from .asset_response import AssetResponse


class AssetListRequest(BaseModel):
    """Query parameters for asset list endpoint"""

    active_only: Optional[bool] = Field(
        True,
        description="Show only active assets (default: true)",
        example=True
    )

    limit: Optional[int] = Field(
        None,
        ge=1,
        le=100,
        description="Maximum number of assets to return (1-100)",
        example=20
    )

    class Config:
        json_schema_extra = {
            "example": {
                "active_only": True,
                "limit": 20
            }
        }


class AssetListResponse(BaseModel):
    """Response model for asset list endpoint"""

    assets: list[AssetResponse] = Field(
        ...,
        description="List of assets matching the filter criteria"
    )

    total_count: int = Field(
        ...,
        description="Total number of assets (before filtering)"
    )

    filtered_count: int = Field(
        ...,
        description="Number of assets after applying filters"
    )

    active_count: int = Field(
        ...,
        description="Number of active assets in the filtered results"
    )

    filters_applied: dict = Field(
        ...,
        description="Summary of filters that were applied"
    )

    # available_categories field removed - category filtering not exposed via API

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
                "total_count": 15,
                "filtered_count": 3,
                "active_count": 3,
                "filters_applied": {
                    "active_only": True,
                    "limit": None
                },
                # "available_categories": ["major", "altcoin", "stablecoin"]  # Removed
            }
        }


class AssetSummary(BaseModel):
    """Summary statistics for asset list"""

    total_assets: int = Field(
        ...,
        description="Total number of assets in inventory"
    )

    active_assets: int = Field(
        ...,
        description="Number of currently active assets"
    )

    categories_breakdown: dict[str, int] = Field(
        ...,
        description="Count of assets per category"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_assets": 15,
                "active_assets": 12,
                "categories_breakdown": {
                    "major": 3,
                    "altcoin": 8,
                    "stablecoin": 4
                }
            }
        }


# Helper functions for building responses
def build_asset_list_response(
    assets: list,
    request_params: AssetListRequest,
    total_count: int,
    available_categories: list[str] = None  # Made optional for backward compatibility
) -> AssetListResponse:
    """Build AssetListResponse from DAO results and request parameters"""

    # Convert DAO assets to API response models
    from .asset_response import asset_to_response
    asset_responses = [asset_to_response(asset) for asset in assets]

    # Count active assets in filtered results
    active_count = sum(1 for asset in asset_responses if asset.is_active)

    # Build filters summary
    filters_applied = {
        "active_only": request_params.active_only,
        "limit": request_params.limit
    }

    return AssetListResponse(
        assets=asset_responses,
        total_count=total_count,
        filtered_count=len(asset_responses),
        active_count=active_count,
        filters_applied=filters_applied
        # available_categories field removed
    )


def build_asset_summary(
    total_assets: int,
    active_assets: int,
    categories_breakdown: dict[str, int]
) -> AssetSummary:
    """Build AssetSummary from statistics"""

    return AssetSummary(
        total_assets=total_assets,
        active_assets=active_assets,
        categories_breakdown=categories_breakdown
    )