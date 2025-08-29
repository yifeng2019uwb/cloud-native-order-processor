"""
User Register API Endpoint
Path: services/user_service/src/controllers/auth/register.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Union
from fastapi import APIRouter, HTTPException, Depends, status, Request
from api_models.auth.registration import (
    UserRegistrationRequest,
    RegistrationSuccessResponse,
    RegistrationErrorResponse
)
from api_models.shared.common import ErrorResponse
from common.auth.security import TokenManager, AuditLogger
from common.data.database import get_user_dao, get_balance_dao
from common.data.entities.user import UserCreate, User, Balance, BalanceCreate
from common.exceptions.shared_exceptions import (
    CNOPUserNotFoundException,
    CNOPInternalServerException
)
from common.shared.logging import BaseLogger, Loggers, LogActions
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
logger = BaseLogger(Loggers.USER)
router = APIRouter(tags=["register"])


@router.post(
    "/register",
    response_model=Union[RegistrationSuccessResponse, RegistrationErrorResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "User successfully registered",
            "model": RegistrationSuccessResponse
        },
        409: {
            "description": "User already exists",
            "model": RegistrationErrorResponse
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse
        },
        503: {
            "description": "Service unavailable",
            "model": ErrorResponse
        }
    }
)
def register_user(
    user_data: UserRegistrationRequest,
    request: Request,
    user_dao = Depends(get_user_dao),
    balance_dao = Depends(get_balance_dao)
) -> RegistrationSuccessResponse:
    """
    Register a new user account with comprehensive validation and security

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (uniqueness, age requirements, etc.)
    """
    # Initialize security managers
    audit_logger = AuditLogger()

    # Log register attempt (without sensitive data)
    logger.info(
        action=LogActions.REQUEST_START,
        message=f"Register attempt from {request.client.host if request.client else 'unknown'}",
        extra={
            "username": user_data.username,
            "email": user_data.email,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Layer 2: Business validation only
        validate_username_uniqueness(user_data.username, user_dao)
        validate_email_uniqueness(user_data.email, user_dao)
        validate_age_requirements(user_data.date_of_birth)

        # Transform API model to DAO model - proper field mapping
        user_create = UserCreate(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,           # Will be hashed in DAO
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone
        )

        # Create the user via DAO (sync operation)
        created_user = user_dao.create_user(user_create)

        # Create initial balance record with 0 balance (sync operation)
        balance_create = BalanceCreate(
            username=created_user.username,
            initial_balance=Decimal('0.00')
        )

        balance_dao.create_balance(balance_create)

        # Log successful registration
        logger.info(action=LogActions.REQUEST_END, message=f"User registered successfully: {user_data.username}")

        # Audit log successful registration
        audit_logger.log_security_event(
            "user_registration_success",
            user_data.username,
            {
                "email": user_data.email,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )

        # Return simple success response - no user data
        return RegistrationSuccessResponse(
            message="User registered successfully"
        )

    except CNOPUserAlreadyExistsException as e:
        # Audit log failed registration due to user already exists
        audit_logger.log_security_event(
            "user_registration_failed",
            user_data.username,
            {
                "reason": "user_already_exists",
                "email": user_data.email,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        # Re-raise the exception as it should be handled by the exception mapper
        raise
    except CNOPUserValidationException as e:
        # Audit log failed registration due to validation error
        audit_logger.log_security_event(
            "user_registration_failed",
            user_data.username,
            {
                "reason": "validation_error",
                "email": user_data.email,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        # Re-raise the exception as it should be handled by the exception mapper
        raise
    except Exception as e:
        # Audit log unexpected error during registration
        audit_logger.log_security_event(
            "user_registration_failed",
            user_data.username,
            {
                "reason": "unexpected_error",
                "error": str(e),
                "email": user_data.email,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        # Log unexpected errors and convert to internal server exception
        logger.error(action=LogActions.ERROR, message=f"Unexpected error during user registration: {str(e)}")
        raise CNOPInternalServerException(f"Registration failed: {str(e)}")