"""
User service specific exceptions
Path: services/user_service/src/exceptions/exceptions.py
"""

from common.exceptions import BaseInternalException


class UserAlreadyExistsException(BaseInternalException):
    """User already exists exception - username/email already exists"""
    pass


class UserServerException(BaseInternalException):
    """User service itself has bad function/implementation"""
    pass
