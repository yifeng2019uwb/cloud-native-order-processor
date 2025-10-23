"""
FastAPI dependencies for authentication
"""
from typing import Optional
from fastapi import Depends, HTTPException, Request, Header
from common.shared.constants.api_constants import HTTPStatus
from common.shared.constants.api_constants import RequestHeaders
from common.shared.constants.service_names import ServiceValidation
from common.shared.constants.api_constants import ErrorMessages
from common.data.entities.user import User
from common.data.dao.user.user_dao import UserDAO
from common.data.database.dependencies import get_user_dao as get_common_user_dao
from common.shared.logging import BaseLogger, Loggers, LogActions
logger = BaseLogger(Loggers.USER)


def verify_gateway_headers(
    request: Request,
    x_source: Optional[str] = Header(None, alias=RequestHeaders.SOURCE),
    x_auth_service: Optional[str] = Header(None, alias=RequestHeaders.AUTH_SERVICE),
    x_user_id: Optional[str] = Header(None, alias=RequestHeaders.USER_ID),
    x_user_role: Optional[str] = Header(None, alias=RequestHeaders.USER_ROLE)
) -> str:
    """
    Verify Gateway headers for authentication

    Args:
        request: FastAPI request object
        x_source: Source header (should be ServiceValidation.EXPECTED_SOURCE)
        x_auth_service: Auth service header (should be ServiceValidation.EXPECTED_AUTH_SERVICE)
        x_user_id: User ID header from Gateway
        x_user_role: User role header from Gateway

    Returns:
        User username from Gateway headers

    Raises:
        HTTPException: If headers are invalid or missing
    """
    # Validate source headers
    if not x_source or x_source != ServiceValidation.EXPECTED_SOURCE:
        logger.warning(action=LogActions.ACCESS_DENIED, message=f"Invalid source header: {x_source}")
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=ErrorMessages.VALIDATION_ERROR
        )

    if not x_auth_service or x_auth_service != ServiceValidation.EXPECTED_AUTH_SERVICE:
        logger.warning(action=LogActions.ACCESS_DENIED, message=f"Invalid auth service header: {x_auth_service}")
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail=ErrorMessages.VALIDATION_ERROR
        )

    # Extract user information from headers
    if not x_user_id:
        logger.warning(action=LogActions.ACCESS_DENIED, message="Missing user ID header")
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=ErrorMessages.AUTHENTICATION_FAILED
        )

    logger.info(action=LogActions.AUTH_SUCCESS, message=f"Gateway headers verified for user: '{x_user_id}'")
    return x_user_id


def get_current_user(
    username: str = Depends(verify_gateway_headers),
    user_dao: UserDAO = Depends(get_common_user_dao)
) -> User:
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
        logger.info(action=LogActions.REQUEST_START, message=f"get_current_user called with username: '{username}'")

        user = user_dao.get_user_by_username(username)
        logger.info(action=LogActions.AUTH_SUCCESS, message=f"user_dao.get_user_by_username returned: {user}")

        if user is None:
            logger.warning(action=LogActions.AUTH_FAILED, message=f"User not found for username: '{username}'")
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
