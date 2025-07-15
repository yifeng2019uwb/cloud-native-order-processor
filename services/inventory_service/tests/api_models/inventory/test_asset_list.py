from inventory_service.src.api_models.inventory.asset_list import AssetListRequest, AssetListResponse

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
        request_params=None,
        available_categories=[],
        filters_applied={}
    )
    assert resp.total_count == 0
    assert resp.assets == []