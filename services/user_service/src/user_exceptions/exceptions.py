"""
User service specific exceptions
Path: services/user_service/src/user_exceptions/exceptions.py

These exceptions are for user service business logic validation and are exposed to clients.
"""

from common.exceptions.base_exception import CNOPClientException


class CNOPUserAlreadyExistsException(CNOPClientException):
    """User already exists exception - username/email already exists"""
    pass


class CNOPUserServerException(CNOPClientException):
    """User service itself has bad function/implementation"""
    pass


class CNOPUserValidationException(CNOPClientException):
    """User validation exception - business logic validation failures"""
    pass
