"""
Inventory Service Business Validators

Provides business logic validation for the inventory service.
Layer 2: Business validation (existence checks, business rules, etc.)
"""

from common.dao.inventory import AssetDAO
from exceptions import AssetNotFoundException


async def validate_asset_exists(asset_id: str, asset_dao: AssetDAO) -> None:
    """
    Layer 2: Business validation - check if asset exists in database

    Args:
        asset_id: The asset ID to validate
        asset_dao: Asset DAO instance

    Raises:
        AssetNotFoundException: If asset doesn't exist
    """
    asset = await asset_dao.get_asset_by_id(asset_id)
    if not asset:
        raise AssetNotFoundException(f"Asset '{asset_id}' not found")


async def validate_asset_is_active(asset_id: str, asset_dao: AssetDAO) -> None:
    """
    Layer 2: Business validation - check if asset is active

    Args:
        asset_id: The asset ID to validate
        asset_dao: Asset DAO instance

    Raises:
        AssetNotFoundException: If asset doesn't exist or is inactive
    """
    asset = await asset_dao.get_asset_by_id(asset_id)
    if not asset:
        raise AssetNotFoundException(f"Asset '{asset_id}' not found")

    if not asset.is_active:
        raise AssetNotFoundException(f"Asset '{asset_id}' is not active")