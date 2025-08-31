from inventory_service.src.api_models.inventory.asset_list import (
    AssetListRequest,
    AssetListResponse,
    build_asset_list_response,
    _build_market_summary,
    _build_display_options,
    _build_comprehensive_market_statistics,
    _build_performance_metrics,
    _build_display_metadata
)
from unittest.mock import MagicMock
from types import SimpleNamespace

def test_asset_list_request_creation():
    req = AssetListRequest(active_only=True, limit=10)
    assert req.active_only is True
    assert req.limit == 10

def test_asset_list_response_creation():
    resp = AssetListResponse(
        assets=[],
        total_count=0,
        filtered_count=0,
        active_count=0,
        filters_applied={}
        # market_summary and display_options are optional, so we don't need to provide them
    )
    assert resp.total_count == 0
    assert resp.assets == []
    assert resp.market_summary is None
    assert resp.display_options is None

def test_asset_list_response_with_enhanced_data():
    resp = AssetListResponse(
        assets=[],
        total_count=0,
        filtered_count=0,
        active_count=0,
        filters_applied={},
        market_summary={
            "total_market_cap": 1000000000,
            "total_volume_24h": 50000000,
            "top_performer_24h": "BTC",
            "top_performer_24h_change": 2.5,
            "worst_performer_24h": "ETH",
            "worst_performer_24h_change": -1.2
        },
        display_options={
            "default_sort": "market_cap_rank",
            "available_sorts": ["market_cap_rank", "price_change_24h"],
            "show_rank": True,
            "show_icon": True,
            "show_market_cap": True,
            "show_volume": True
        }
    )
    assert resp.total_count == 0
    assert resp.assets == []
    assert resp.market_summary is not None
    assert resp.display_options is not None
    assert resp.market_summary["total_market_cap"] == 1000000000
    assert resp.display_options["default_sort"] == "market_cap_rank"


class TestBuildMarketSummary:
    """Test the _build_market_summary function"""

    def test_build_market_summary_empty_assets(self):
        """Test market summary with empty assets list"""
        result = _build_market_summary([])

        assert result["total_market_cap"] == 0
        assert result["total_volume_24h"] == 0
        assert result["top_performer_24h"] is None
        assert result["top_performer_24h_change"] == 0
        assert result["worst_performer_24h"] is None
        assert result["worst_performer_24h_change"] == 0

    def test_build_market_summary_with_assets_no_changes(self):
        """Test market summary with assets but no price changes"""
        assets = [
            SimpleNamespace(
                market_cap=1000000,
                total_volume_24h=50000,
                price_change_percentage_24h=None,
                symbol="BTC"
            ),
            SimpleNamespace(
                market_cap=500000,
                total_volume_24h=25000,
                price_change_percentage_24h=None,
                symbol="ETH"
            )
        ]

        result = _build_market_summary(assets)

        assert result["total_market_cap"] == 1500000
        assert result["total_volume_24h"] == 75000
        assert result["top_performer_24h"] is None
        assert result["top_performer_24h_change"] == 0
        assert result["worst_performer_24h"] is None
        assert result["worst_performer_24h_change"] == 0

    def test_build_market_summary_with_price_changes(self):
        """Test market summary with assets and price changes"""
        assets = [
            SimpleNamespace(
                market_cap=1000000,
                total_volume_24h=50000,
                price_change_percentage_24h=5.0,
                symbol="BTC"
            ),
            SimpleNamespace(
                market_cap=500000,
                total_volume_24h=25000,
                price_change_percentage_24h=-2.0,
                symbol="ETH"
            ),
            SimpleNamespace(
                market_cap=300000,
                total_volume_24h=15000,
                price_change_percentage_24h=1.5,
                symbol="ADA"
            )
        ]

        result = _build_market_summary(assets)

        assert result["total_market_cap"] == 1800000
        assert result["total_volume_24h"] == 90000
        assert result["top_performer_24h"] == "BTC"
        assert result["top_performer_24h_change"] == 5.0
        assert result["worst_performer_24h"] == "ETH"
        assert result["worst_performer_24h_change"] == -2.0

    def test_build_market_summary_with_asset_id_fallback(self):
        """Test market summary when symbol is None, falls back to asset_id"""
        assets = [
            SimpleNamespace(
                market_cap=1000000,
                total_volume_24h=50000,
                price_change_percentage_24h=5.0,
                symbol=None,
                asset_id="bitcoin"
            )
        ]

        result = _build_market_summary(assets)

        assert result["top_performer_24h"] == "bitcoin"
        assert result["top_performer_24h_change"] == 5.0


class TestBuildDisplayOptions:
    """Test the _build_display_options function"""

    def test_build_display_options(self):
        """Test display options creation"""
        result = _build_display_options([])

        assert result["default_sort"] == "market_cap_rank"
        assert "market_cap_rank" in result["available_sorts"]
        assert "price_change_24h" in result["available_sorts"]
        assert "volume_24h" in result["available_sorts"]
        assert "name" in result["available_sorts"]
        assert result["show_rank"] is True
        assert result["show_icon"] is True
        assert result["show_market_cap"] is True
        assert result["show_volume"] is True


class TestBuildComprehensiveMarketStatistics:
    """Test the _build_comprehensive_market_statistics function"""

    def test_build_comprehensive_market_statistics_empty(self):
        """Test with empty assets list"""
        result = _build_comprehensive_market_statistics([])
        assert result == {}

    def test_build_comprehensive_market_statistics_with_data(self):
        """Test with assets data"""
        assets = [
            SimpleNamespace(
                market_cap=1000000,
                total_volume_24h=50000,
                price_change_percentage_24h=5.0,
                symbol="BTC"
            ),
            SimpleNamespace(
                market_cap=500000,
                total_volume_24h=25000,
                price_change_percentage_24h=-2.0,
                symbol="ETH"
            ),
            SimpleNamespace(
                market_cap=300000,
                total_volume_24h=15000,
                price_change_percentage_24h=1.5,
                symbol="ADA"
            )
        ]

        result = _build_comprehensive_market_statistics(assets)

        assert result["total_market_cap"] == 1800000
        assert result["total_volume_24h"] == 90000  # 50000 + 25000 + 15000 = 90000
        assert result["average_price_change_24h"] == 1.5  # (5.0 + -2.0 + 1.5) / 3
        assert result["assets_with_positive_change"] == 2
        assert result["assets_with_negative_change"] == 1
        assert result["top_5_market_cap"] == ["BTC", "ETH", "ADA"]
        assert result["top_5_volume"] == ["BTC", "ETH", "ADA"]

    def test_build_comprehensive_market_statistics_no_price_changes(self):
        """Test with assets but no price changes"""
        assets = [
            SimpleNamespace(
                market_cap=1000000,
                total_volume_24h=50000,
                price_change_percentage_24h=None,
                symbol="BTC"
            )
        ]

        result = _build_comprehensive_market_statistics(assets)

        assert result["average_price_change_24h"] == 0
        assert result["assets_with_positive_change"] == 0
        assert result["assets_with_negative_change"] == 0

    def test_build_comprehensive_market_statistics_with_asset_id_fallback(self):
        """Test when symbol is None, falls back to asset_id"""
        assets = [
            SimpleNamespace(
                market_cap=1000000,
                total_volume_24h=50000,
                price_change_percentage_24h=5.0,
                symbol=None,
                asset_id="bitcoin"
            )
        ]

        result = _build_comprehensive_market_statistics(assets)

        assert result["top_5_market_cap"] == ["bitcoin"]
        assert result["top_5_volume"] == ["bitcoin"]


class TestBuildPerformanceMetrics:
    """Test the _build_performance_metrics function"""

    def test_build_performance_metrics_empty(self):
        """Test with empty assets list"""
        result = _build_performance_metrics([])
        assert result == {}

    def test_build_performance_metrics_with_ranks(self):
        """Test with assets having various ranks"""
        assets = [
            SimpleNamespace(market_cap_rank=5),   # rank 1-10
            SimpleNamespace(market_cap_rank=25),  # rank 11-50
            SimpleNamespace(market_cap_rank=75),  # rank 51-100
            SimpleNamespace(market_cap_rank=150), # rank 101-300
            SimpleNamespace(market_cap_rank=400), # rank 300+
            SimpleNamespace(market_cap_rank=None), # no rank
        ]

        result = _build_performance_metrics(assets)

        assert result["rank_1_10"] == 1
        assert result["rank_11_50"] == 1
        assert result["rank_51_100"] == 1
        assert result["rank_101_300"] == 1
        assert result["rank_300_plus"] == 1
        assert result["assets_with_rank"] == 5
        assert result["assets_without_rank"] == 1

    def test_build_performance_metrics_no_ranks(self):
        """Test with assets having no ranks"""
        assets = [
            SimpleNamespace(market_cap_rank=None),
            SimpleNamespace(market_cap_rank=None)
        ]

        result = _build_performance_metrics(assets)

        assert result["rank_1_10"] == 0
        assert result["rank_11_50"] == 0
        assert result["rank_51_100"] == 0
        assert result["rank_101_300"] == 0
        assert result["rank_300_plus"] == 0
        assert result["assets_with_rank"] == 0
        assert result["assets_without_rank"] == 2


class TestBuildDisplayMetadata:
    """Test the _build_display_metadata function"""

    def test_build_display_metadata_empty(self):
        """Test with empty assets list"""
        result = _build_display_metadata([])
        assert result == {}

    def test_build_display_metadata_with_data(self):
        """Test with assets having various attributes"""
        assets = [
            SimpleNamespace(
                image="https://example.com/btc.png",
                symbol="BTC",
                category="cryptocurrency"
            ),
            SimpleNamespace(
                image="https://example.com/eth.png",
                symbol="ETH",
                category="cryptocurrency"
            ),
            SimpleNamespace(
                image=None,
                symbol=None,
                category="token"
            )
        ]

        result = _build_display_metadata(assets)

        assert result["assets_with_icons"] == 2
        assert result["assets_without_icons"] == 1
        assert result["assets_with_symbols"] == 2
        assert result["assets_without_symbols"] == 1
        assert "cryptocurrency" in result["supported_categories"]
        assert "token" in result["supported_categories"]
        assert result["default_sort_order"] == "market_cap_rank"

    def test_build_display_metadata_no_categories(self):
        """Test with assets having no categories"""
        assets = [
            SimpleNamespace(
                image="https://example.com/btc.png",
                symbol="BTC",
                category=None
            )
        ]

        result = _build_display_metadata(assets)

        assert result["supported_categories"] == []


class TestBuildAssetListResponse:
    """Test the build_asset_list_response function"""

    def test_build_asset_list_response_basic(self):
        """Test basic response building"""
        assets = [
            SimpleNamespace(
                asset_id="bitcoin",
                symbol="BTC",
                name="Bitcoin",
                description="Bitcoin cryptocurrency",
                category="cryptocurrency",
                amount=100,
                price_usd=45000.0,
                is_active=True,
                market_cap=1000000000,
                total_volume_24h=50000,
                price_change_percentage_24h=5.0,
                high_24h=46000.0,
                low_24h=44000.0,
                circulating_supply=19500000,
                updated_at=None
            )
        ]

        request_params = AssetListRequest(active_only=True, limit=10)
        result = build_asset_list_response(assets, request_params, 1)

        assert result.total_count == 1
        assert result.filtered_count == 1
        assert result.active_count == 1
        assert len(result.assets) == 1
        assert result.assets[0].asset_id == "bitcoin"
        assert result.assets[0].symbol == "BTC"

    def test_build_asset_list_response_with_market_summary(self):
        """Test response building with market summary"""
        assets = [
            SimpleNamespace(
                asset_id="bitcoin",
                symbol="BTC",
                name="Bitcoin",
                description="Bitcoin cryptocurrency",
                category="cryptocurrency",
                amount=100,
                price_usd=45000.0,
                is_active=True,
                market_cap=1000000000,
                total_volume_24h=50000,
                price_change_percentage_24h=5.0,
                high_24h=46000.0,
                low_24h=44000.0,
                circulating_supply=19500000,
                updated_at=None
            )
        ]

        request_params = AssetListRequest(active_only=True, limit=10)
        result = build_asset_list_response(assets, request_params, 1)

        assert result.market_summary is not None
        assert result.market_summary["total_market_cap"] == 1000000000
        assert result.market_summary["top_performer_24h"] == "BTC"
        assert result.market_summary["top_performer_24h_change"] == 5.0

    def test_build_asset_list_response_with_display_options(self):
        """Test response building with display options"""
        assets = [
            SimpleNamespace(
                asset_id="bitcoin",
                symbol="BTC",
                name="Bitcoin",
                description="Bitcoin cryptocurrency",
                category="cryptocurrency",
                amount=100,
                price_usd=45000.0,
                is_active=True,
                market_cap=1000000000,
                total_volume_24h=50000,
                price_change_percentage_24h=5.0,
                high_24h=46000.0,
                low_24h=44000.0,
                circulating_supply=19500000,
                updated_at=None
            )
        ]

        request_params = AssetListRequest(active_only=True, limit=10)
        result = build_asset_list_response(assets, request_params, 1)

        assert result.display_options is not None
        assert result.display_options["default_sort"] == "market_cap_rank"
        assert result.display_options["show_rank"] is True