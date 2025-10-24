"""
FastAPI dependencies for authentication
"""
from fastapi import Depends, HTTPException, Request
from common.shared.constants.api_constants import HTTPStatus, ErrorMessages, RequestHeaders, RequestHeaderDefaults
from common.auth.security.token_manager import TokenManager
from common.auth.security.jwt_constants import JwtFields, JWTConfig, RequestDefaults
from common.auth.gateway.header_validator import get_request_id_from_request
from common.shared.logging import BaseLogger, Loggers, LogActions
from common.data.entities.user import User, DEFAULT_USER_ROLE
from common.data.dao.user.user_dao import UserDAO
from common.data.database.dependencies import get_user_dao as get_common_user_dao
from common.auth.security.auth_dependencies import AuthenticatedUser, get_current_user as get_authenticated_user

logger = BaseLogger(Loggers.USER)


def get_current_user(
    request: Request,
    user_dao: UserDAO = Depends(get_common_user_dao)
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        request: FastAPI request object
        user_dao: UserDAO instance

    Returns:
        Current user information from database

    Raises:
        HTTPException: If authentication fails or user not found
    """
    try:
        # Get authenticated user from JWT token
        authenticated_user = get_authenticated_user(request)

        logger.info(action=LogActions.REQUEST_START,
                   message=f"get_current_user called with username: '{authenticated_user.username}'",
                   request_id=authenticated_user.request_id)

        # Get full user details from database
        user = user_dao.get_user_by_username(authenticated_user.username)
        logger.info(action=LogActions.AUTH_SUCCESS,
                   message=f"user_dao.get_user_by_username returned: {user}",
                   request_id=authenticated_user.request_id)

        if user is None:
            logger.warning(action=LogActions.AUTH_FAILED,
                          message=f"User not found for username: '{authenticated_user.username}'",
                          request_id=authenticated_user.request_id)
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=ErrorMessages.USER_NOT_FOUND
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Error getting current user: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=ErrorMessages.INTERNAL_SERVER_ERROR
        )