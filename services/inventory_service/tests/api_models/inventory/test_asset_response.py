from inventory_service.src.api_models.inventory.asset_response import AssetDetailResponse, asset_to_detail_response
import types

def test_asset_detail_response_creation():
    resp = AssetDetailResponse(
        asset_id='BTC',
        name='Bitcoin',
        description='desc',
        category='crypto',
        price_usd=1.0,
        is_active=True,
        availability_status='available'
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
        amount=100.0
    )
    resp = asset_to_detail_response(mock_asset)
    assert resp.asset_id == 'BTC'
    assert resp.name == 'Bitcoin'