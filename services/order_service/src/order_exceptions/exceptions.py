"""
Order service specific exceptions
Path: services/order_service/src/exceptions/exceptions.py

These exceptions are for order service business logic validation and are exposed to clients.
"""

from common.exceptions import CNOPClientException


class CNOPOrderAlreadyExistsException(CNOPClientException):
    """Order already exists exception - order already exists"""
    pass


class CNOPOrderServerException(CNOPClientException):
    """Order service itself has bad function/implementation"""
    pass


class CNOPOrderValidationException(CNOPClientException):
    """Order validation exception - business logic validation failures including invalid status"""
    pass