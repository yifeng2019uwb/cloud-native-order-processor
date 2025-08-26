"""
Database-related exceptions

These exceptions represent database-specific issues that should be handled
internally by services and never exposed to external clients.
"""

from ...exceptions import CNOPInternalException


class CNOPDatabaseConnectionException(CNOPInternalException):
    """Database connection exception - internal system issue (500 error)"""
    pass


class CNOPDatabaseOperationException(CNOPInternalException):
    """Database operation exception - internal system issue (500 error)"""
    pass
