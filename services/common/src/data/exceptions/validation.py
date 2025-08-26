"""
Validation-related exceptions

This exception represents generic entity validation issues that can occur
during internal data operations. This is for internal data validation only,
not business logic validation.
"""

from ...exceptions import CNOPInternalException


class CNOPEntityValidationException(CNOPInternalException):
    """Generic entity validation exception - internal data validation issue (500 error)"""
    pass
