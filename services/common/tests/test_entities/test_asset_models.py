import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from common.entities.asset import AssetCreate, Asset, AssetUpdate, AssetResponse, AssetListResponse
from pydantic import ValidationError


def test_asset_create_valid():
    asset = AssetCreate(
        asset_id="BTC",
        name="Bitcoin",
        description="Digital currency",
        category="major",
        amount=Decimal("10.12345678"),
        price_usd=Decimal("45000.50")
    )
    assert asset.asset_id == "BTC"
    assert asset.name == "Bitcoin"
    assert asset.category == "major"
    assert asset.amount == Decimal("10.12345678")
    assert asset.price_usd == Decimal("45000.50")


def test_asset_create_invalid_asset_id():
    with pytest.raises(ValueError):
        AssetCreate(
            asset_id="bt",  # too short
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=Decimal("10"),
            price_usd=Decimal("1000")
        )


def test_asset_create_invalid_category():
    with pytest.raises(ValueError):
        AssetCreate(
            asset_id="ETH",
            name="Ethereum",
            description="Smart contracts",
            category="invalid",
            amount=Decimal("10"),
            price_usd=Decimal("1000")
        )


def test_asset_create_negative_amount():
    with pytest.raises(ValueError):
        AssetCreate(
            asset_id="ETH",
            name="Ethereum",
            description="Smart contracts",
            category="major",
            amount=Decimal("-1"),
            price_usd=Decimal("1000")
        )


def test_asset_create_negative_price():
    with pytest.raises(ValueError):
        AssetCreate(
            asset_id="ETH",
            name="Ethereum",
            description="Smart contracts",
            category="major",
            amount=Decimal("1"),
            price_usd=Decimal("-1000")
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
            amount=Decimal("10"),
            price_usd=Decimal("0"),
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
        amount=Decimal("10"),
        price_usd=Decimal("0"),
        is_active=False,
        created_at=now,
        updated_at=now
    )
    assert asset.is_active is False


def test_asset_update_partial():
    update = AssetUpdate(description="Updated desc", amount=Decimal("5.5"))
    assert update.description == "Updated desc"
    assert update.amount == Decimal("5.5")


def test_asset_update_invalid_amount():
    with pytest.raises(ValueError):
        AssetUpdate(amount=Decimal("-10"))


def test_asset_response_model():
    now = datetime.now()
    resp = AssetResponse(
        asset_id="ETH",
        name="Ethereum",
        description="Smart contracts",
        category="altcoin",
        amount=Decimal("100.0"),
        price_usd=Decimal("2000.0"),
        is_active=True,
        created_at=now,
        updated_at=now
    )
    assert resp.asset_id == "ETH"
    assert resp.is_active is True
    assert resp.price_usd == Decimal("2000.0")


def test_asset_list_response():
    now = datetime.now()
    assets = [
        AssetResponse(
            asset_id="BTC",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=Decimal("10.0"),
            price_usd=Decimal("45000.0"),
            is_active=True,
            created_at=now,
            updated_at=now
        ),
        AssetResponse(
            asset_id="ETH",
            name="Ethereum",
            description="Smart contracts",
            category="altcoin",
            amount=Decimal("100.0"),
            price_usd=Decimal("2000.0"),
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
        AssetUpdate(price_usd=Decimal("0"), is_active=True)
    # Should not raise if is_active is False
    update = AssetUpdate(price_usd=Decimal("0"), is_active=False)
    assert update.is_active is False


def test_asset_update_description_strip():
    update = AssetUpdate(description="   Some desc   ")
    assert update.description == "Some desc"


def test_asset_update_empty_description():
    update = AssetUpdate(description="   ")
    assert update.description == ""


def test_asset_update_rounding():
    update = AssetUpdate(amount=Decimal("1.123456789"), price_usd=Decimal("123.456"))
    assert update.amount == Decimal("1.12345679")  # Rounded to 8 decimals
    assert update.price_usd == Decimal("123.46")   # Rounded to 2 decimals


# Add only these essential tests to cover missing lines (replace all the previous ones)

def test_asset_create_asset_id_whitespace():
    """Test AssetCreate with whitespace-only asset_id"""
    with pytest.raises(ValidationError, match="Asset ID cannot be empty"):
        AssetCreate(
            asset_id="   ",
            name="Bitcoin",
            description="Digital currency",
            category="major",
            amount=Decimal("10"),
            price_usd=Decimal("1000")
        )

def test_asset_create_name_whitespace():
    """Test AssetCreate with whitespace-only name"""
    with pytest.raises(ValidationError, match="Asset name cannot be empty"):
        AssetCreate(
            asset_id="BTC",
            name="   ",
            description="Digital currency",
            category="major",
            amount=Decimal("10"),
            price_usd=Decimal("1000")
        )

def test_asset_create_name_invalid_chars():
    """Test AssetCreate with invalid characters in name"""
    with pytest.raises(ValidationError, match="Asset name contains invalid characters"):
        AssetCreate(
            asset_id="BTC",
            name="Bitcoin@#$",
            description="Digital currency",
            category="major",
            amount=Decimal("10"),
            price_usd=Decimal("1000")
        )

def test_asset_create_description_long():
    """Test AssetCreate with description exceeding max length"""
    with pytest.raises(ValidationError, match="String should have at most 1000 characters"):
        AssetCreate(
            asset_id="BTC",
            name="Bitcoin",
            description="a" * 1001,
            category="major",
            amount=Decimal("10"),
            price_usd=Decimal("1000")
        )

def test_asset_create_description_empty_strip():
    """Test AssetCreate description becomes empty after stripping"""
    asset = AssetCreate(
        asset_id="BTC",
        name="Bitcoin",
        description="   ",
        category="major",
        amount=Decimal("10"),
        price_usd=Decimal("1000")
    )
    assert asset.description == ""

def test_asset_update_description_strip():
    """Test AssetUpdate description strips whitespace"""
    update = AssetUpdate(description="  test  ")
    assert update.description == "test"

def test_asset_update_description_empty_strip():
    """Test AssetUpdate description becomes empty after stripping"""
    update = AssetUpdate(description="   ")
    assert update.description == ""

def test_asset_update_amount_rounding():
    """Test AssetUpdate amount rounding to 8 decimals"""
    update = AssetUpdate(amount=Decimal("1.123456789"))
    assert update.amount == Decimal("1.12345679")

def test_asset_update_price_rounding():
    """Test AssetUpdate price rounding to 2 decimals"""
    update = AssetUpdate(price_usd=Decimal("123.999"))
    assert update.price_usd == Decimal("124.00")

def test_asset_update_category_none():
    """Test AssetUpdate category can be None"""
    update = AssetUpdate(category=None)
    assert update.category is None

def test_asset_create_name_title_case():
    """Test AssetCreate name converts to title case"""
    asset = AssetCreate(
        asset_id="BTC",
        name="bitcoin",
        description="Digital currency",
        category="major",
        amount=Decimal("10"),
        price_usd=Decimal("1000")
    )
    assert asset.name == "Bitcoin"

def test_asset_create_asset_id_lowercase():
    """Test AssetCreate asset_id converts to uppercase"""
    asset = AssetCreate(
        asset_id="btc",
        name="Bitcoin",
        description="Digital currency",
        category="major",
        amount=Decimal("10"),
        price_usd=Decimal("1000")
    )
    assert asset.asset_id == "BTC"

def test_asset_create_asset_id_regex_fail():
    """Test AssetCreate asset_id regex validation failure - covers line 68"""
    with pytest.raises(ValidationError, match="Asset ID must be 3-6 uppercase letters/numbers only"):
        AssetCreate(
            asset_id="AB@",  # Contains @ symbol - triggers regex validation failure on line 68
            name="Test Asset",
            description="Test description",
            category="major",
            amount=Decimal("10.0"),
            price_usd=Decimal("100.0")
        )
