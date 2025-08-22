"""
FastAPI dependencies for authentication
"""
from typing import Optional

from fastapi import Depends, HTTPException, status, Request, Header
import logging

from common.entities.user import UserResponse
from common.dao.user import UserDAO
from common.database import get_user_dao as get_common_user_dao

logger = logging.getLogger(__name__)


async def verify_gateway_headers(
    request: Request,
    x_source: Optional[str] = Header(None, alias="X-Source"),
    x_auth_service: Optional[str] = Header(None, alias="X-Auth-Service"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
) -> str:
    """
    Verify Gateway headers for authentication

    Args:
        request: FastAPI request object
        x_source: Source header (should be "gateway")
        x_auth_service: Auth service header (should be "auth-service")
        x_user_id: User ID header from Gateway
        x_user_role: User role header from Gateway

    Returns:
        User username from Gateway headers

    Raises:
        HTTPException: If headers are invalid or missing
    """
    # Validate source headers
    if not x_source or x_source != "gateway":
        logger.warning(f"Invalid source header: {x_source}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid request source"
        )

    if not x_auth_service or x_auth_service != "auth-service":
        logger.warning(f"Invalid auth service header: {x_auth_service}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication service"
        )

    # Extract user information from headers
    if not x_user_id:
        logger.warning("Missing user ID header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )

    logger.info(f"🔍 DEBUG: Gateway headers verified for user: '{x_user_id}'")
    return x_user_id


async def get_current_user(
    username: str = Depends(verify_gateway_headers),
    user_dao: UserDAO = Depends(get_common_user_dao)
) -> UserResponse:
    """
    Get current authenticated user from Gateway headers

    Args:
        username: User username from Gateway headers
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
    request: Request,
    x_source: Optional[str] = Header(None, alias="X-Source"),
    x_auth_service: Optional[str] = Header(None, alias="X-Auth-Service"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    user_dao: UserDAO = Depends(get_common_user_dao)
) -> Optional[UserResponse]:
    """
    Get current user if Gateway headers are provided (optional authentication)

    Args:
        request: FastAPI request object
        x_source: Source header (should be "gateway")
        x_auth_service: Auth service header (should be "auth-service")
        x_user_id: User ID header from Gateway
        x_user_role: User role header from Gateway
        user_dao: UserDAO instance

    Returns:
        Current user information if authenticated, None otherwise
    """
    # Check if all required headers are present
    if not all([x_source, x_auth_service, x_user_id]):
        return None

    try:
        # Verify headers
        if x_source != "gateway" or x_auth_service != "auth-service":
            return None

        user = user_dao.get_user_by_username(x_user_id)
        if user is None:
            return None

        return UserResponse(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role,
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