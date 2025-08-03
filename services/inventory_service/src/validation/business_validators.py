"""
Inventory Service Business Validators

Provides business logic validation for the inventory service.
Layer 2: Business validation (existence checks, business rules, etc.)
"""

from common.database import get_asset_dao
from exceptions import AssetNotFoundException
from common.exceptions import EntityNotFoundException


def validate_asset_exists(asset_id: str, asset_dao) -> None:
    """
    Layer 2: Business validation - check if asset exists in database

    Args:
        asset_id: The asset ID to validate
        asset_dao: Asset DAO instance

    Raises:
        AssetNotFoundException: If asset doesn't exist
    """
    try:
        asset = asset_dao.get_asset_by_id(asset_id)
        # If we get here, asset exists
        return
    except Exception as e:
        # Check if it's EntityNotFoundException from the DAO
        if isinstance(e, EntityNotFoundException):
            # Convert DAO's EntityNotFoundException to service's AssetNotFoundException
            raise AssetNotFoundException(f"Asset '{asset_id}' not found")
        else:
            # Re-raise other exceptions (DatabaseOperationException, etc.)
            raise e


def validate_asset_is_active(asset_id: str, asset_dao) -> None:
    """
    Layer 2: Business validation - check if asset is active

    Args:
        asset_id: The asset ID to validate
        asset_dao: Asset DAO instance

    Raises:
        AssetNotFoundException: If asset doesn't exist or is inactive
    """
    try:
        asset = asset_dao.get_asset_by_id(asset_id)
        if not asset.is_active:
            raise AssetNotFoundException(f"Asset '{asset_id}' is not active")
    except Exception as e:
        # Check if it's EntityNotFoundException from the DAO
        if isinstance(e, EntityNotFoundException):
            # Convert DAO's EntityNotFoundException to service's AssetNotFoundException
            raise AssetNotFoundException(f"Asset '{asset_id}' not found")
        else:
            # Re-raise other exceptions (DatabaseOperationException, etc.)
            raise e