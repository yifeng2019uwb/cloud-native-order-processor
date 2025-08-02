"""
FastAPI dependencies for authentication
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
import logging

from common.entities.user import UserResponse
from common.dao.user import UserDAO
from common.database import get_user_dao as get_common_user_dao
from controllers.token_utilis import verify_access_token

logger = logging.getLogger(__name__)

# Security scheme for JWT Bearer tokens
security = HTTPBearer(auto_error=True)


async def verify_token_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Verify JWT token from Authorization header

    Args:
        credentials: HTTP authorization credentials

    Returns:
        User username from verified token

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        logger.info(f"🔍 DEBUG: Verifying token: {credentials.credentials[:20]}...")

        username = verify_access_token(credentials.credentials)
        logger.info(f"🔍 DEBUG: Token verification returned username: '{username}'")

        if username is None:
            logger.error("❌ DEBUG: Token verification returned None")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
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
    username: str = Depends(verify_token_dependency),
    user_dao: UserDAO = Depends(get_common_user_dao)
) -> UserResponse:
    """
    Get current authenticated user from token

    Args:
        username: User username from verified token
        user_dao: UserDAO instance

    Returns:
        Current user information

    Raises:
        HTTPException: If user not found or database error
    """
    try:
        logger.info(f"🔍 DEBUG: get_current_user called with username: '{username}'")

        user = user_dao.get_user_by_username(username)
        logger.info(f"🔍 DEBUG: user_dao.get_user_by_username returned: {user}")

        if user is None:
            logger.warning(f"❌ DEBUG: User not found for username: '{username}'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return UserResponse(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
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
    user_dao: UserDAO = Depends(get_common_user_dao)
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

        user = user_dao.get_user_by_email(email)
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