"""
User Service Dependencies

This module provides dependency injection functions for the User Service,
including a simplified transaction manager that only uses available DAOs.
"""

from typing import Optional
from fastapi import Header, Request
from common.data.database.dependencies import get_user_dao, get_balance_dao
from common.core.utils import TransactionManager


def get_request_id_from_request(request: Request) -> str:
    """
    Extract request ID from Request object headers for distributed tracing

    Args:
        request: FastAPI Request object

    Returns:
        Request ID string for correlation across services
    """
    return request.headers.get("X-Request-ID") or "no-request-id"


def get_transaction_manager() -> TransactionManager:
    """
    Get TransactionManager instance with User Service available DAOs

    User Service only has access to user_dao and balance_dao,
    so we create a simplified TransactionManager for balance operations.
    """
    return TransactionManager(
        user_dao=get_user_dao(),
        balance_dao=get_balance_dao(),
        order_dao=None,  # Not available in User Service
        asset_dao=None,   # Not available in User Service
        asset_balance_dao=None,  # Not available in User Service
        asset_transaction_dao=None  # Not available in User Service
    )
