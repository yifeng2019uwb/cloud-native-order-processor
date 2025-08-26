"""
Inventory service specific exceptions
Path: services/inventory_service/src/exceptions/exceptions.py

These exceptions are for inventory service business logic validation and are exposed to clients.
"""

from common.exceptions import CNOPClientException


class CNOPAssetAlreadyExistsException(CNOPClientException):
    """Asset already exists exception - asset already exists"""
    pass


class CNOPInventoryServerException(CNOPClientException):
    """Inventory service itself has bad function/implementation"""
    pass


class CNOPAssetValidationException(CNOPClientException):
    """Asset validation exception - business logic validation failures"""
    pass