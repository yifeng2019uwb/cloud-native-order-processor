from inventory_service.src.api_models.inventory.asset_response import AssetDetailResponse, AssetResponse
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
        last_updated='2025-01-01T00:00:00Z'
    )
    assert resp.asset_id == 'BTC'
    assert resp.name == 'Bitcoin'
