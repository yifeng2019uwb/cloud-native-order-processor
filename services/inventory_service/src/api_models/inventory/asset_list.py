"""
Asset list request and response models for inventory service API
Path: services/inventory-service/src/api_models/inventory/asset_list.py
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

from .asset_response import AssetResponse


class AssetListRequest(BaseModel):
    """Query parameters for asset list endpoint

    Layer 1: Field validation (format, sanitization) - handled by Pydantic @field_validator
    Layer 2: Business validation - handled by centralized functions in controllers
    """

    active_only: Optional[bool] = Field(
        True,
        description="Show only active assets (default: true)",
        example=True
    )

    limit: Optional[int] = Field(
        None,
        ge=1,
        le=250,
        description="Maximum number of assets to return (1-250)",
        example=20
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "active_only": True,
                "limit": 20
            }
        }
    )


class AssetListResponse(BaseModel):
    """Enhanced response model for asset list endpoint with comprehensive market data"""

    assets: list[AssetResponse] = Field(
        ...,
        description="List of assets matching the filter criteria, sorted by market cap rank"
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

    # Enhanced metadata for frontend display (optional for backward compatibility)
    market_summary: Optional[dict] = Field(
        None,
        description="Market overview statistics for the returned assets",
        example={
            "total_market_cap": 1250000000000,
            "total_volume_24h": 85000000000,
            "top_performer_24h": "BTC",
            "top_performer_24h_change": 5.2,
            "worst_performer_24h": "ETH",
            "worst_performer_24h_change": -2.1
        }
    )

    display_options: Optional[dict] = Field(
        None,
        description="Frontend display configuration options",
        example={
            "default_sort": "market_cap_rank",
            "available_sorts": ["market_cap_rank", "price_change_24h", "volume_24h", "name"],
            "show_rank": True,
            "show_icon": True,
            "show_market_cap": True,
            "show_volume": True
        }
    )

    # available_categories field removed - category filtering not exposed via API

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "assets": [
                    {
                        "asset_id": "BTC",
                        "name": "Bitcoin",
                        "description": "Digital currency and store of value",
                        "category": "major",
                        "price_usd": 45000.50,
                        "is_active": True,
                        "symbol": "BTC",
                        "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
                        "market_cap_rank": 1,
                        "market_cap": 850000000000,
                        "price_change_percentage_24h": 2.5,
                        "total_volume_24h": 25000000000
                    },
                    {
                        "asset_id": "ETH",
                        "name": "Ethereum",
                        "description": "Decentralized platform for smart contracts",
                        "category": "major",
                        "price_usd": 3000.25,
                        "is_active": True,
                        "symbol": "ETH",
                        "image": "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
                        "market_cap_rank": 2,
                        "market_cap": 350000000000,
                        "price_change_percentage_24h": -1.2,
                        "total_volume_24h": 15000000000
                    }
                ],
                "total_count": 15,
                "filtered_count": 3,
                "active_count": 3,
                "filters_applied": {
                    "active_only": True,
                    "limit": None
                },
                "market_summary": {
                    "total_market_cap": 1200000000000,
                    "total_volume_24h": 40000000000,
                    "top_performer_24h": "BTC",
                    "top_performer_24h_change": 2.5,
                    "worst_performer_24h": "ETH",
                    "worst_performer_24h_change": -1.2
                },
                "display_options": {
                    "default_sort": "market_cap_rank",
                    "available_sorts": ["market_cap_rank", "price_change_24h", "volume_24h", "name"],
                    "show_rank": True,
                    "show_icon": True,
                    "show_market_cap": True,
                    "show_volume": True
                }
            }
        }
    )


class AssetSummary(BaseModel):
    """Enhanced summary statistics for asset list with comprehensive market data"""

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

    # Enhanced market statistics (optional for backward compatibility)
    market_statistics: Optional[dict] = Field(
        None,
        description="Comprehensive market statistics across all assets",
        example={
            "total_market_cap": 2500000000000,
            "total_volume_24h": 150000000000,
            "average_price_change_24h": 1.8,
            "assets_with_positive_change": 45,
            "assets_with_negative_change": 32,
            "top_5_market_cap": ["BTC", "ETH", "BNB", "SOL", "ADA"],
            "top_5_volume": ["BTC", "ETH", "USDT", "BNB", "SOL"]
        }
    )

    # Performance metrics (optional for backward compatibility)
    performance_metrics: Optional[dict] = Field(
        None,
        description="Performance and ranking metrics",
        example={
            "rank_1_10": 10,
            "rank_11_50": 40,
            "rank_51_100": 50,
            "rank_101_300": 200,
            "rank_300_plus": 0,
            "assets_with_rank": 300,
            "assets_without_rank": 0
        }
    )

    # Icon and display metadata (optional for backward compatibility)
    display_metadata: Optional[dict] = Field(
        None,
        description="Metadata for frontend display configuration",
        example={
            "assets_with_icons": 298,
            "assets_without_icons": 2,
            "assets_with_symbols": 300,
            "assets_without_symbols": 0,
            "supported_categories": ["major", "altcoin", "stablecoin", "defi", "gaming"],
            "default_sort_order": "market_cap_rank"
        }
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_assets": 300,
                "active_assets": 298,
                "categories_breakdown": {
                    "major": 5,
                    "altcoin": 250,
                    "stablecoin": 15,
                    "defi": 20,
                    "gaming": 10
                },
                "market_statistics": {
                    "total_market_cap": 2500000000000,
                    "total_volume_24h": 150000000000,
                    "average_price_change_24h": 1.8,
                    "assets_with_positive_change": 45,
                    "assets_with_negative_change": 32,
                    "top_5_market_cap": ["BTC", "ETH", "BNB", "SOL", "ADA"],
                    "top_5_volume": ["BTC", "ETH", "USDT", "BNB", "SOL"]
                },
                "performance_metrics": {
                    "rank_1_10": 10,
                    "rank_11_50": 40,
                    "rank_51_100": 50,
                    "rank_101_300": 200,
                    "rank_300_plus": 0,
                    "assets_with_rank": 300,
                    "assets_without_rank": 0
                },
                "display_metadata": {
                    "assets_with_icons": 298,
                    "assets_without_icons": 2,
                    "assets_with_symbols": 300,
                    "assets_without_symbols": 0,
                    "supported_categories": ["major", "altcoin", "stablecoin", "defi", "gaming"],
                    "default_sort_order": "market_cap_rank"
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
    """Build enhanced AssetListResponse from DAO results and request parameters"""

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

    # Build market summary from returned assets
    market_summary = _build_market_summary(asset_responses)

    # Build display options
    display_options = _build_display_options(asset_responses)

    return AssetListResponse(
        assets=asset_responses,
        total_count=total_count,
        filtered_count=len(asset_responses),
        active_count=active_count,
        filters_applied=filters_applied,
        market_summary=market_summary,
        display_options=display_options
    )


def build_asset_summary(
    total_assets: int,
    active_assets: int,
    categories_breakdown: dict[str, int],
    all_assets: list = None  # Optional: pass all assets for enhanced statistics
) -> AssetSummary:
    """Build enhanced AssetSummary from statistics"""

    # Build enhanced market statistics if assets are provided
    market_statistics = {}
    performance_metrics = {}
    display_metadata = {}

    if all_assets:
        market_statistics = _build_comprehensive_market_statistics(all_assets)
        performance_metrics = _build_performance_metrics(all_assets)
        display_metadata = _build_display_metadata(all_assets)

    return AssetSummary(
        total_assets=total_assets,
        active_assets=active_assets,
        categories_breakdown=categories_breakdown,
        market_statistics=market_statistics,
        performance_metrics=performance_metrics,
        display_metadata=display_metadata
    )


def _build_market_summary(assets: list) -> dict:
    """Build market summary for returned assets"""
    if not assets:
        return {
            "total_market_cap": 0,
            "total_volume_24h": 0,
            "top_performer_24h": None,
            "top_performer_24h_change": 0,
            "worst_performer_24h": None,
            "worst_performer_24h_change": 0
        }

    # Calculate totals
    total_market_cap = sum(asset.market_cap or 0 for asset in assets)
    total_volume_24h = sum(asset.total_volume_24h or 0 for asset in assets)

    # Find top and worst performers
    assets_with_changes = [a for a in assets if a.price_change_percentage_24h is not None]

    if assets_with_changes:
        top_performer = max(assets_with_changes, key=lambda x: x.price_change_percentage_24h or 0)
        worst_performer = min(assets_with_changes, key=lambda x: x.price_change_percentage_24h or 0)

        top_performer_24h = top_performer.symbol or top_performer.asset_id
        top_performer_24h_change = top_performer.price_change_percentage_24h or 0
        worst_performer_24h = worst_performer.symbol or worst_performer.asset_id
        worst_performer_24h_change = worst_performer.price_change_percentage_24h or 0
    else:
        top_performer_24h = None
        top_performer_24h_change = 0
        worst_performer_24h = None
        worst_performer_24h_change = 0

    return {
        "total_market_cap": total_market_cap,
        "total_volume_24h": total_volume_24h,
        "top_performer_24h": top_performer_24h,
        "top_performer_24h_change": top_performer_24h_change,
        "worst_performer_24h": worst_performer_24h,
        "worst_performer_24h_change": worst_performer_24h_change
    }


def _build_display_options(assets: list) -> dict:
    """Build display options for frontend configuration"""
    return {
        "default_sort": "market_cap_rank",
        "available_sorts": ["market_cap_rank", "price_change_24h", "volume_24h", "name"],
        "show_rank": True,
        "show_icon": True,
        "show_market_cap": True,
        "show_volume": True
    }


def _build_comprehensive_market_statistics(all_assets: list) -> dict:
    """Build comprehensive market statistics across all assets"""
    if not all_assets:
        return {}

    # Calculate market totals
    total_market_cap = sum(asset.market_cap or 0 for asset in all_assets)
    total_volume_24h = sum(asset.total_volume_24h or 0 for asset in all_assets)

    # Calculate average price change
    assets_with_changes = [a for a in all_assets if a.price_change_percentage_24h is not None]
    if assets_with_changes:
        avg_change = sum(a.price_change_percentage_24h or 0 for a in assets_with_changes) / len(assets_with_changes)
        positive_count = sum(1 for a in assets_with_changes if (a.price_change_percentage_24h or 0) > 0)
        negative_count = sum(1 for a in assets_with_changes if (a.price_change_percentage_24h or 0) < 0)
    else:
        avg_change = 0
        positive_count = 0
        negative_count = 0

    # Find top 5 by market cap and volume
    top_market_cap = sorted(all_assets, key=lambda x: x.market_cap or 0, reverse=True)[:5]
    top_volume = sorted(all_assets, key=lambda x: x.total_volume_24h or 0, reverse=True)[:5]

    return {
        "total_market_cap": total_market_cap,
        "total_volume_24h": total_volume_24h,
        "average_price_change_24h": round(avg_change, 2),
        "assets_with_positive_change": positive_count,
        "assets_with_negative_change": negative_count,
        "top_5_market_cap": [a.symbol or a.asset_id for a in top_market_cap],
        "top_5_volume": [a.symbol or a.asset_id for a in top_volume]
    }


def _build_performance_metrics(all_assets: list) -> dict:
    """Build performance and ranking metrics"""
    if not all_assets:
        return {}

    # Count assets by rank ranges
    rank_1_10 = sum(1 for a in all_assets if a.market_cap_rank and 1 <= a.market_cap_rank <= 10)
    rank_11_50 = sum(1 for a in all_assets if a.market_cap_rank and 11 <= a.market_cap_rank <= 50)
    rank_51_100 = sum(1 for a in all_assets if a.market_cap_rank and 51 <= a.market_cap_rank <= 100)
    rank_101_300 = sum(1 for a in all_assets if a.market_cap_rank and 101 <= a.market_cap_rank <= 300)
    rank_300_plus = sum(1 for a in all_assets if a.market_cap_rank and a.market_cap_rank > 300)

    assets_with_rank = sum(1 for a in all_assets if a.market_cap_rank is not None)
    assets_without_rank = sum(1 for a in all_assets if a.market_cap_rank is None)

    return {
        "rank_1_10": rank_1_10,
        "rank_11_50": rank_11_50,
        "rank_51_100": rank_51_100,
        "rank_101_300": rank_101_300,
        "rank_300_plus": rank_300_plus,
        "assets_with_rank": assets_with_rank,
        "assets_without_rank": assets_without_rank
    }


def _build_display_metadata(all_assets: list) -> dict:
    """Build metadata for frontend display configuration"""
    if not all_assets:
        return {}

    # Count assets with icons and symbols
    assets_with_icons = sum(1 for a in all_assets if a.image)
    assets_without_icons = sum(1 for a in all_assets if not a.image)
    assets_with_symbols = sum(1 for a in all_assets if a.symbol)
    assets_without_symbols = sum(1 for a in all_assets if not a.symbol)

    # Get unique categories
    categories = list(set(a.category for a in all_assets if a.category))

    return {
        "assets_with_icons": assets_with_icons,
        "assets_without_icons": assets_without_icons,
        "assets_with_symbols": assets_with_symbols,
        "assets_without_symbols": assets_without_symbols,
        "supported_categories": categories,
        "default_sort_order": "market_cap_rank"
    }