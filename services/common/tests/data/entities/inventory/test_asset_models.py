import pytest
from decimal import Decimal
from src.data.entities.inventory import AssetCreate, AssetUpdate
from pydantic import ValidationError

def test_asset_create_all_fields():
    asset = AssetCreate(
        asset_id="BTC",
        name="Bitcoin",
        description="Digital currency",
        category="major",
        amount=Decimal("10.12345678"),
        price_usd=Decimal("45000.50"),
        symbol="BTC",
        image="https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
        market_cap_rank=1,
        high_24h=68000.0,
        low_24h=66000.0,
        circulating_supply=19400000.0,
        price_change_24h=500.0,
        ath_change_percentage=-2.5,
        market_cap=1300000000000.0
    )
    assert asset.asset_id == "BTC"
    assert asset.name == "Bitcoin"
    assert asset.symbol == "BTC"
    assert asset.image.startswith("https://")
    assert asset.market_cap_rank == 1
    assert asset.high_24h == 68000.0
    assert asset.low_24h == 66000.0
    assert asset.circulating_supply == 19400000.0
    assert asset.price_change_24h == 500.0
    assert asset.ath_change_percentage == -2.5
    assert asset.market_cap == 1300000000000.0

def test_asset_create_missing_required():
    # asset_id is required
    with pytest.raises(ValidationError):
        AssetCreate(
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=Decimal("10.12345678"),
            price_usd=Decimal("45000.50")
        )
    # name is required
    with pytest.raises(ValidationError):
        AssetCreate(
            asset_id="BTC",
            description="Digital currency",
            category="major",
            amount=Decimal("10.12345678"),
            price_usd=Decimal("45000.50")
        )
    # category is required
    with pytest.raises(ValidationError):
        AssetCreate(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            amount=Decimal("10.12345678"),
            price_usd=Decimal("45000.50")
        )
    # amount is required
    with pytest.raises(ValidationError):
        AssetCreate(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            price_usd=Decimal("45000.50")
        )
    # price_usd is required
    with pytest.raises(ValidationError):
        AssetCreate(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=Decimal("10.12345678")
        )

def test_asset_create_trim_whitespace():
    asset = AssetCreate(
        asset_id="  BTC  ",
        name="  Bitcoin  ",
        description="  Digital currency  ",
        category="  major  ",
        amount=Decimal("10.12345678"),
        price_usd=Decimal("45000.50"),
        symbol="  BTC  ",
        image="  https://assets.coingecko.com/coins/images/1/large/bitcoin.png  "
    )
    assert asset.asset_id == "BTC"
    assert asset.name == "Bitcoin"
    assert asset.description == "Digital currency"
    assert asset.category == "major"
    assert asset.symbol == "BTC"
    assert asset.image == "https://assets.coingecko.com/coins/images/1/large/bitcoin.png"

def test_asset_update_trim_whitespace():
    update = AssetUpdate(
        description="  Updated desc  ",
        category="  altcoin  ",
        symbol="  ETH  ",
        image="  https://assets.coingecko.com/coins/images/279/large/ethereum.png  "
    )
    assert update.description == "Updated desc"
    assert update.category == "altcoin"
    assert update.symbol == "ETH"
    assert update.image == "https://assets.coingecko.com/coins/images/279/large/ethereum.png"