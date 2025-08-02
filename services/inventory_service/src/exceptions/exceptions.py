"""
Inventory service specific exceptions
Path: services/inventory_service/src/exceptions/exceptions.py
"""

from common.exceptions import BaseInternalException


class AssetAlreadyExistsException(BaseInternalException):
    """Asset already exists exception - asset already exists"""
    pass


class InventoryServerException(BaseInternalException):
    """Inventory service itself has bad function/implementation"""
    pass