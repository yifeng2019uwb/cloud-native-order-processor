"""
System-related exceptions

These exceptions represent internal system/infrastructure issues that should be handled
internally by services and never exposed to external clients.
"""

from ...exceptions import CNOPInternalException


class CNOPConfigurationException(CNOPInternalException):
    """Configuration loading/parsing exception - internal system issue (500 error)"""
    pass


class CNOPAWSServiceException(CNOPInternalException):
    """AWS service failure exception - internal system issue (500 error)"""
    pass


class CNOPExternalServiceException(CNOPInternalException):
    """External service failure exception - internal system issue (500 error)"""
    pass


class CNOPLockAcquisitionException(CNOPInternalException):
    """Lock acquisition failure exception - internal system issue (500 error)"""
    pass


class CNOPLockTimeoutException(CNOPInternalException):
    """Lock timeout exception - internal system issue (500 error)"""
    pass


class CNOPCommonServerException(CNOPInternalException):
    """Generic common server error exception - internal system issue (500 error)"""
    pass
