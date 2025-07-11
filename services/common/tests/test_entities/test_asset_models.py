import pytest
from datetime import datetime, timedelta
from src.entities.asset import AssetCreate, Asset, AssetUpdate, AssetResponse, AssetListResponse


def test_asset_create_valid():
    asset = AssetCreate(
        asset_id="BTC",
        name="Bitcoin",
        description="Digital currency",
        category="major",
        amount=10.12345678,
        price_usd=45000.50
    )
    assert asset.asset_id == "BTC"
    assert asset.name == "Bitcoin"
    assert asset.category == "major"
    assert asset.amount == 10.12345678
    assert asset.price_usd == 45000.50


def test_asset_create_invalid_asset_id():
    with pytest.raises(ValueError):
        AssetCreate(
            asset_id="bt",  # too short
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=10,
            price_usd=1000
        )


def test_asset_create_invalid_category():
    with pytest.raises(ValueError):
        AssetCreate(
            asset_id="ETH",
            name="Ethereum",
            description="Smart contracts",
            category="invalid",
            amount=10,
            price_usd=1000
        )


def test_asset_create_negative_amount():
    with pytest.raises(ValueError):
        AssetCreate(
            asset_id="ETH",
            name="Ethereum",
            description="Smart contracts",
            category="major",
            amount=-1,
            price_usd=1000
        )


def test_asset_create_negative_price():
    with pytest.raises(ValueError):
        AssetCreate(
            asset_id="ETH",
            name="Ethereum",
            description="Smart contracts",
            category="major",
            amount=1,
            price_usd=-1000
        )


def test_asset_model_price_active_relationship():
    now = datetime.now()
    # Should raise if price_usd == 0 and is_active is True
    with pytest.raises(ValueError):
        Asset(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=10,
            price_usd=0,
            is_active=True,
            created_at=now,
            updated_at=now
        )
    # Should not raise if is_active is False
    asset = Asset(
        asset_id="BTC",
        name="Bitcoin",
        description="Digital currency",
        category="major",
        amount=10,
        price_usd=0,
        is_active=False,
        created_at=now,
        updated_at=now
    )
    assert asset.is_active is False


def test_asset_update_partial():
    update = AssetUpdate(description="Updated desc", amount=5.5)
    assert update.description == "Updated desc"
    assert update.amount == 5.5


def test_asset_update_invalid_amount():
    with pytest.raises(ValueError):
        AssetUpdate(amount=-10)


def test_asset_response_model():
    now = datetime.now()
    resp = AssetResponse(
        asset_id="ETH",
        name="Ethereum",
        description="Smart contracts",
        category="altcoin",
        amount=100.0,
        price_usd=2000.0,
        is_active=True,
        created_at=now,
        updated_at=now
    )
    assert resp.asset_id == "ETH"
    assert resp.is_active is True
    assert resp.price_usd == 2000.0


def test_asset_list_response():
    now = datetime.now()
    assets = [
        AssetResponse(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=10.0,
            price_usd=45000.0,
            is_active=True,
            created_at=now,
            updated_at=now
        ),
        AssetResponse(
            asset_id="ETH",
            name="Ethereum",
            description="Smart contracts",
            category="altcoin",
            amount=100.0,
            price_usd=2000.0,
            is_active=False,
            created_at=now,
            updated_at=now
        )
    ]
    resp = AssetListResponse(assets=assets, total_count=2, active_count=1)
    assert resp.total_count == 2
    assert resp.active_count == 1
    assert len(resp.assets) == 2
    assert resp.assets[0].asset_id == "BTC"


def test_asset_update_category_validation():
    # Valid category
    update = AssetUpdate(category="major")
    assert update.category == "major"
    # Invalid category
    with pytest.raises(ValueError):
        AssetUpdate(category="invalid")


def test_asset_update_price_active_relationship():
    # Should raise if both price_usd==0 and is_active==True
    with pytest.raises(ValueError):
        AssetUpdate(price_usd=0, is_active=True)
    # Should not raise if is_active is False
    update = AssetUpdate(price_usd=0, is_active=False)
    assert update.is_active is False


def test_asset_update_description_strip():
    update = AssetUpdate(description="   Some desc   ")
    assert update.description == "Some desc"


def test_asset_update_empty_description():
    update = AssetUpdate(description="   ")
    assert update.description == ""


def test_asset_update_rounding():
    update = AssetUpdate(amount=1.123456789, price_usd=123.456)
    assert update.amount == round(1.123456789, 8)
    assert update.price_usd == round(123.456, 2)