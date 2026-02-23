"""
User Login API Endpoint
Path: services/user_service/src/controllers/auth/login.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from api_models.auth.login import (
    UserLoginRequest,
    LoginResponse
)
from common.data.entities.user import User
from common.data.database.dependencies import get_user_dao
from common.auth.security.token_manager import TokenManager
from common.auth.security.audit_logger import AuditLogger
from common.auth.security.jwt_constants import JWTConfig
from common.shared.constants.api_constants import ErrorMessages, HTTPStatus, RequestHeaders, RequestHeaderDefaults
from common.exceptions.shared_exceptions import CNOPInvalidCredentialsException, CNOPUserNotFoundException, CNOPInternalServerException
from user_exceptions import CNOPUserValidationException
from common.shared.logging import BaseLogger, LogAction, LoggerName
from common.auth.gateway.header_validator import get_request_id_from_request
from api_info_enum import ApiTags, ApiPaths
from constants import MSG_SUCCESS_LOGIN

# Initialize our standardized logger
logger = BaseLogger(LoggerName.USER)
router = APIRouter(tags=[ApiTags.AUTHENTICATION.value])


@router.post(
    ApiPaths.LOGIN.value,
    response_model=LoginResponse
)
def login_user(
    login_data: UserLoginRequest,
    request: Request,
    user_dao=Depends(get_user_dao)
) -> LoginResponse:
    """
    Authenticate user with username and password

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (authentication, etc.)
    """
    # Initialize security managers
    token_manager = TokenManager()
    audit_logger = AuditLogger()

    # Get client IP and User-Agent for audit logging (align with register.py)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get(RequestHeaders.USER_AGENT, RequestHeaderDefaults.USER_AGENT_DEFAULT)

    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)

    try:
        logger.info(action=LogAction.REQUEST_START, message=f"Login attempt for: {login_data.username}", request_id=request_id)

        # Layer 2: Business validation only
        # Authenticate user using username
        user = user_dao.authenticate_user(login_data.username, login_data.password)
        if not user:
            logger.warning(action=LogAction.AUTH_FAILED, message=f"Authentication failed for: {login_data.username}", request_id=request_id)
            audit_logger.log_login_failure(login_data.username, "Invalid credentials", client_ip, user_agent)
            raise CNOPInvalidCredentialsException(f"Invalid credentials for user '{login_data.username}'")

        logger.info(action=LogAction.USER_LOGIN_SUCCESS, message=f"User authenticated successfully: {login_data.username}", request_id=request_id)

        # Create JWT token using centralized TokenManager
        token_response = token_manager.create_access_token(user.username, user.role)

        # Log successful login and token creation
        audit_logger.log_login_success(user.username, client_ip, user_agent)
        audit_logger.log_token_created(user.username, JWTConfig.ACCESS_TOKEN_TYPE, client_ip)

        # Return success response
        return LoginResponse(
            access_token=token_response.access_token,
            token_type=token_response.token_type,
            expires_in=token_response.expires_in
        )

    except CNOPInvalidCredentialsException:
        # Let the exception bubble up to be handled by RFC 7807 handlers
        raise
    except CNOPUserNotFoundException:
        # Let the exception bubble up to be handled by RFC 7807 handlers
        raise
    except CNOPUserValidationException:
        # Let the exception bubble up to be handled by RFC 7807 handlers
        raise
    except Exception as e:
        # Log unexpected errors and re-raise as internal server error
        logger.error(action=LogAction.ERROR, message=f"Unexpected error during login: {e}", request_id=request_id)
        raise CNOPInternalServerException(f"{ErrorMessages.INTERNAL_SERVER_ERROR} during login: {e}")