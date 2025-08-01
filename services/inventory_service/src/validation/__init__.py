"""
Inventory Service Validation Package

Provides validation logic specific to the inventory service.
Only validates API request fields (GET endpoints only).
"""

from .field_validators import validate_asset_id

__all__ = [
    'validate_asset_id'
]