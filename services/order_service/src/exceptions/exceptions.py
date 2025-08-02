"""
Order service specific exceptions
Path: services/order_service/src/exceptions/exceptions.py
"""

from common.exceptions import BaseInternalException


class OrderAlreadyExistsException(BaseInternalException):
    """Order already exists exception - order already exists"""
    pass


class OrderStatusException(BaseInternalException):
    """Order status transition failures"""
    pass


class OrderServerException(BaseInternalException):
    """Order service itself has bad function/implementation"""
    pass