from inventory_service.src.api_models.inventory.asset_response import AssetDetailResponse, asset_to_detail_response, AssetResponse, asset_to_response
import types
from datetime import datetime, timezone

def test_asset_detail_response_creation():
    resp = AssetDetailResponse(
        asset_id='BTC',
        name='Bitcoin',
        description='desc',
        category='crypto',
        price_usd=1.0,
        is_active=True,
        availability_status='available',
        last_updated=datetime.now(timezone.utc)
    )
    assert resp.asset_id == 'BTC'
    assert resp.name == 'Bitcoin'

def test_asset_to_detail_response():
    mock_asset = types.SimpleNamespace(
        asset_id='BTC',
        name='Bitcoin',
        description='desc',
        category='crypto',
        price_usd=1.0,
        is_active=True,
        amount=100.0,
        # Add new CoinGecko fields
        symbol='BTC',
        image='https://assets.coingecko.com/coins/images/1/large/bitcoin.png',
        market_cap_rank=1,
        current_price=1.0,
        high_24h=1.1,
        low_24h=0.9,
        circulating_supply=19500000,
        total_supply=21000000,
        max_supply=21000000,
        price_change_24h=0.1,
        price_change_percentage_24h=10.0,
        price_change_percentage_7d=15.0,
        price_change_percentage_30d=20.0,
        market_cap=1000000000,
        market_cap_change_24h=100000000,
        market_cap_change_percentage_24h=10.0,
        total_volume_24h=50000000,
        volume_change_24h=10000000,
        ath=2.0,
        ath_change_percentage=-50.0,
        ath_date='2021-11-10T14:24:11.849Z',
        atl=0.1,
        atl_change_percentage=900.0,
        atl_date='2013-07-06T00:00:00.000Z',
        last_updated='2025-08-30T21:49:33.955Z',
        sparkline_7d={'prices': [0.9, 1.0, 1.1, 1.0, 0.9, 1.0, 1.0]},
        updated_at=datetime.now(timezone.utc)
    )
    resp = asset_to_detail_response(mock_asset)
    assert resp.asset_id == 'BTC'
    assert resp.name == 'Bitcoin'
    assert resp.symbol == 'BTC'
    assert resp.market_cap_rank == 1

def test_asset_to_response():
    mock_asset = types.SimpleNamespace(
        asset_id='BTC',
        name='Bitcoin',
        description='desc',
        category='crypto',
        price_usd=1.0,
        is_active=True,
        # Add new CoinGecko fields
        symbol='BTC',
        image='https://assets.coingecko.com/coins/images/1/large/bitcoin.png',
        market_cap_rank=1,
        current_price=1.0,
        high_24h=1.1,
        low_24h=0.9,
        circulating_supply=19500000,
        price_change_percentage_24h=10.0,
        market_cap=1000000000,
        total_volume_24h=50000000,
        updated_at=datetime.now(timezone.utc)
    )
    resp = asset_to_response(mock_asset)
    assert resp.asset_id == 'BTC'
    assert resp.name == 'Bitcoin'
    assert resp.symbol == 'BTC'
    assert resp.market_cap_rank == 1
    assert resp.market_cap == 1000000000