"""
FastAPI dependencies for authentication
"""
import sys
import os
from typing import Optional

# Add common package to path
common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "common", "src")
sys.path.insert(0, common_path)

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
import logging

from models.user import UserResponse
from database.dao.user_dao import UserDAO
from database.dynamodb_connection import get_dynamodb
from .token_utils import verify_access_token

logger = logging.getLogger(__name__)

# Security scheme for JWT Bearer tokens
security = HTTPBearer(auto_error=True)


async def get_db_connection():
    """
    Get database connection dependency

    Returns:
        DynamoDB connection instance
    """
    try:
        return get_dynamodb()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable"
        )


async def get_user_dao(db_connection=Depends(get_db_connection)) -> UserDAO:
    """
    Get UserDAO instance dependency

    Args:
        db_connection: Database connection from dependency

    Returns:
        UserDAO instance
    """
    return UserDAO(db_connection)


async def verify_token_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Verify JWT token from Authorization header

    Args:
        credentials: HTTP authorization credentials

    Returns:
        User email from verified token

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        email = verify_access_token(credentials.credentials)
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error in token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    email: str = Depends(verify_token_dependency),
    user_dao: UserDAO = Depends(get_user_dao)
) -> UserResponse:
    """
    Get current authenticated user from token

    Args:
        email: User email from verified token
        user_dao: UserDAO instance

    Returns:
        Current user information

    Raises:
        HTTPException: If user not found or database error
    """
    try:
        user = await user_dao.get_user_by_email(email)

        if user is None:
            logger.warning(f"User not found for email: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return UserResponse(
            email=user.email,
            name=user.name,
            phone=user.phone,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    user_dao: UserDAO = Depends(get_user_dao)
) -> Optional[UserResponse]:
    """
    Get current user if token is provided (optional authentication)

    Args:
        credentials: Optional HTTP authorization credentials
        user_dao: UserDAO instance

    Returns:
        Current user information if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        email = verify_access_token(credentials.credentials)
        if email is None:
            return None

        user = await user_dao.get_user_by_email(email)
        if user is None:
            return None

        return UserResponse(
            email=user.email,
            name=user.name,
            phone=user.phone,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    except Exception as e:
        logger.debug(f"Optional authentication failed: {e}")
        return None


def require_admin_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Require admin user (placeholder for future admin functionality)

    Args:
        current_user: Current authenticated user

    Returns:
        Current user if admin

    Raises:
        HTTPException: If user is not admin
    """
    # TODO: Implement admin role checking
    # For now, all authenticated users are considered admins
    # In production, check user.role or user.is_admin

    logger.debug(f"Admin access granted to user: {current_user.email}")
    return current_user