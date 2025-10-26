"""
User Register API Endpoint
Path: services/user_service/src/controllers/auth/register.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Depends, status, Request
from api_models.auth.registration import (
    UserRegistrationRequest,
    RegistrationResponse
)
from common.auth.security.token_manager import TokenManager
from common.auth.security.audit_logger import AuditLogger
from common.data.database.dependencies import get_user_dao, get_balance_dao
from common.data.entities.user import User, Balance
from common.exceptions.shared_exceptions import (
    CNOPUserNotFoundException,
    CNOPInternalServerException
)
from common.shared.logging import BaseLogger, LogAction, LogField, LogDefault, LoggerName
from common.shared.constants.api_constants import ErrorMessages
from api_info_enum import ApiTags, ApiPaths

# Constants for audit reasons
from common.auth.gateway.header_validator import get_request_id_from_request
from user_exceptions.exceptions import (
    CNOPUserAlreadyExistsException,
    CNOPUserValidationException
)
from validation.business_validators import (
    validate_username_uniqueness,
    validate_email_uniqueness,
    validate_age_requirements
)

# Initialize our standardized logger
logger = BaseLogger(LoggerName.USER)
router = APIRouter(tags=[ApiTags.AUTHENTICATION.value])

AUDIT_REASON_USER_ALREADY_EXISTS = "user_already_exists"
AUDIT_REASON_VALIDATION_ERROR = "validation_error"
AUDIT_REASON_UNEXPECTED_ERROR = "unexpected_error"

@router.post(
    ApiPaths.REGISTER.value,
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserRegistrationRequest,
    request: Request,
    user_dao = Depends(get_user_dao),
    balance_dao = Depends(get_balance_dao)
) -> RegistrationResponse:
    """
    Register a new user account with comprehensive validation and security

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (uniqueness, age requirements, etc.)
    """
    # Initialize security managers
    audit_logger = AuditLogger()

    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)

    # Log register attempt (without sensitive data)
    logger.info(
        action=LogAction.REQUEST_START,
        message=f"Register attempt from {request.client.host if request.client else 'unknown'} for username: {user_data.username}, email: {user_data.email}",
        request_id=request_id
    )

    try:
        # Layer 2: Business validation only
        validate_username_uniqueness(user_data.username, user_dao)
        validate_email_uniqueness(user_data.email, user_dao)
        validate_age_requirements(user_data.date_of_birth)

        # Transform API model to User entity - proper field mapping
        user = User(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,           # Will be hashed in DAO
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone
        )

        # Create the user via DAO (sync operation)
        created_user = user_dao.create_user(user)

        # Create initial balance record with 0 balance (sync operation)
        initial_balance = Balance(
            username=created_user.username,
            current_balance=Decimal('0.00')
        )

        balance_dao.create_balance(initial_balance)

        # Log successful registration
        logger.info(action=LogAction.REQUEST_END, message=f"User registered successfully: {user_data.username}", request_id=request_id)

        # Audit log successful registration
        audit_logger.log_security_event(
            LogAction.USER_REGISTRATION_SUCCESS,
            user_data.username,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get(LogField.USER_AGENT, LogDefault.UNKNOWN)
        )

        # Return simple success response - no user data
        return RegistrationResponse()

    except CNOPUserAlreadyExistsException as e:
        # Audit log failed registration due to user already exists
        audit_logger.log_security_event(
            LogAction.USER_REGISTRATION_FAILED,
            user_data.username,
            details={LogField.AUDIT_REASON: AUDIT_REASON_USER_ALREADY_EXISTS},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get(LogField.USER_AGENT, LogDefault.UNKNOWN)
        )
        # Re-raise the exception as it should be handled by the exception mapper
        raise
    except CNOPUserValidationException as e:
        # Audit log failed registration due to validation error
        audit_logger.log_security_event(
            LogAction.USER_REGISTRATION_FAILED,
            user_data.username,
            details={LogField.AUDIT_REASON: AUDIT_REASON_VALIDATION_ERROR},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get(LogField.USER_AGENT, LogDefault.UNKNOWN)
        )
        # Re-raise the exception as it should be handled by the exception mapper
        raise
    except Exception as e:
        # Audit log unexpected error during registration
        audit_logger.log_security_event(
            LogAction.USER_REGISTRATION_FAILED,
            user_data.username,
            details={LogField.AUDIT_REASON: f"{AUDIT_REASON_UNEXPECTED_ERROR}: {str(e)}"},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get(LogField.USER_AGENT, LogDefault.UNKNOWN)
        )
        # Log unexpected errors and convert to internal server exception
        logger.error(action=LogAction.ERROR, message=f"Unexpected error during user registration: {str(e)}", request_id=request_id)
        raise CNOPInternalServerException(f"{ErrorMessages.INTERNAL_SERVER_ERROR} during registration: {str(e)}")