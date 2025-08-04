"""
Dependencies for Order Service controllers
Path: services/order_service/src/controllers/dependencies.py

Provides dependency injection for:
- Database connections
- Service instances
- Authentication
- Authorization
"""
import logging
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Import common package dependencies
from common.database import get_order_dao
from common.dao.order.order_dao import OrderDAO

# Order service removed - business logic now in controllers

# Import JWT utilities
from common.security import TokenManager

logger = logging.getLogger(__name__)

# Security scheme for JWT tokens
security = HTTPBearer(auto_error=False)

# Initialize TokenManager
token_manager = TokenManager()


def get_order_dao_dependency() -> OrderDAO:
    """Get OrderDAO instance"""
    return get_order_dao()


# Order service removed - business logic now in controllers


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    Get current user from JWT token

    This is a simplified version - in production, you'd want to:
    - Validate token signature
    - Check token expiration
    - Verify user exists in database
    - Return proper user entity
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    try:
        # Verify and decode JWT token
        token_data = token_manager.verify_access_token(credentials.credentials)

        # Extract user information from token
        user_info = {
            "user_id": token_data.get("sub"),  # Subject (user ID)
            "username": token_data.get("username"),
            "role": token_data.get("role", "customer")
        }

        logger.info(f"User authenticated: {user_info['username']}")
        return user_info

    except Exception as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


def get_transaction_manager():
    """
    Get transaction manager for order operations

    TODO: Implement transaction manager for atomic operations
    For now, return None to indicate no transaction management
    """
    return None
