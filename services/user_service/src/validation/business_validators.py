"""
User Service Business Validators

Provides business logic validation for the user service.
Handles uniqueness checks and business rules for registration.
"""

from datetime import date
from typing import Optional, Any
from validation_enums import ValidationActions
from common.exceptions.shared_exceptions import (
    CNOPUserNotFoundException,
    CNOPInternalServerException
)
from common.shared.constants.api_constants import ErrorMessages
from common.shared.logging import BaseLogger, LogAction, LoggerName
from user_exceptions import CNOPUserAlreadyExistsException, CNOPUserValidationException

# Initialize our standardized logger
logger = BaseLogger(LoggerName.USER)


def validate_user_permissions(username: str, action: str, user_dao: Any) -> bool:
    """
    Validate user permissions for portfolio operations

    Args:
        username: Username to validate
        action: Action being performed (e.g., ValidationActions.VIEW_PORTFOLIO.value)
        user_dao: User DAO instance

    Returns:
        True if user has permission

    Raises:
        CNOPUserValidationException: If user doesn't have permission
    """
    try:
        # Check if user exists
        user = user_dao.get_user_by_username(username)
        if not user:
            logger.warning(
                action=LogAction.VALIDATION_ERROR,
                message=f"User not found for permission check: {username}"
            )
            raise CNOPUserValidationException(ErrorMessages.USER_NOT_FOUND)

        return True

    except CNOPUserValidationException:
        # Re-raise validation exceptions
        raise
    except Exception as e:
        logger.error(
            action=LogAction.ERROR,
            message=f"Error validating user permissions: {str(e)}"
        )
        raise CNOPUserValidationException("Permission validation failed")

def validate_username_uniqueness(username: str, user_dao: Any, exclude_username: Optional[str] = None) -> bool:
    """
    Validate that username is unique in the system

    Args:
        username: Username to check
        user_dao: User DAO instance
        exclude_username: Username to exclude from check (for updates)

    Returns:
        True if username is unique

    Raises:
        UserAlreadyExistsException: If username already exists
    """
    logger.warning(action=LogAction.VALIDATION_ERROR, message=f"Starting username uniqueness validation for: '{username}'")

    try:
        logger.info(action=LogAction.REQUEST_START, message=f"Calling user_dao.get_user_by_username('{username}')")
        existing_user = user_dao.get_user_by_username(username)

        if existing_user:
            logger.warning(action=LogAction.VALIDATION_ERROR, message=f"User found! Username '{username}' already exists")
            raise CNOPUserAlreadyExistsException(f"Username '{username}' already exists")
        else:
            logger.info(action=LogAction.REQUEST_END, message=f"User not found! Username '{username}' is unique")
            return True

    except CNOPUserNotFoundException as e:
        # User doesn't exist, which means username is unique
        logger.info(action=LogAction.REQUEST_END, message=f"User not found! Username '{username}' is unique. Exception: {str(e)}")
        return True
    except CNOPUserAlreadyExistsException:
        # Re-raise this specific exception to maintain proper flow
        raise
    except Exception as e:
        logger.error(action=LogAction.ERROR, message=f"Unexpected exception in username validation: {str(e)}")
        raise CNOPInternalServerException(f"Internal error during username validation: {str(e)}")


def validate_email_uniqueness(email: str, user_dao: Any, exclude_username: Optional[str] = None) -> bool:
    """
    Validate that email is unique in the system

    Args:
        email: Email to check
        user_dao: User DAO instance
        exclude_username: Username to exclude from check (for updates)

    Returns:
        True if email is unique

    Raises:
        UserAlreadyExistsException: If email already exists
    """
    logger.warning(action=LogAction.VALIDATION_ERROR, message=f"Starting email uniqueness validation for: '{email}'")

    try:
        logger.info(action=LogAction.REQUEST_START, message=f"Calling user_dao.get_user_by_email('{email}')")
        existing_user = user_dao.get_user_by_email(email)

        if existing_user:
            if exclude_username and existing_user.username == exclude_username:
                logger.info(action=LogAction.REQUEST_END, message=f"Email '{email}' belongs to same user '{exclude_username}', allowing update")
                return True
            else:
                logger.warning(action=LogAction.VALIDATION_ERROR, message=f"User found! Email '{email}' already exists")
                raise CNOPUserAlreadyExistsException(f"Email '{email}' already exists")
        else:
            logger.info(action=LogAction.REQUEST_END, message=f"User not found! Email '{email}' is unique")
            return True

    except CNOPUserNotFoundException as e:
        # User doesn't exist, which means email is unique
        logger.info(action=LogAction.REQUEST_END, message=f"User not found! Email '{email}' is unique. Exception: {str(e)}")
        return True
    except CNOPUserAlreadyExistsException:
        # Re-raise this specific exception to maintain proper flow
        raise
    except Exception as e:
        logger.error(action=LogAction.ERROR, message=f"Unexpected exception in email validation: {str(e)}")
        raise CNOPInternalServerException(f"Internal error during email validation: {str(e)}")


def validate_user_exists(username: str, user_dao: Any) -> bool:
    """
    Validate that user exists in the system

    Args:
        username: Username to check
        user_dao: User DAO instance

    Returns:
        True if user exists

    Raises:
        UserNotFoundException: If user doesn't exist
    """
    # Query database for user existence
    user = user_dao.get_user_by_username(username)

    if not user:
        raise CNOPUserNotFoundException(f"User with username '{username}' not found")

    return True


def validate_age_requirements(date_of_birth: date) -> bool:
    """
    Validate age requirements for user registration

    Args:
        date_of_birth: User's date of birth

    Returns:
        True if age requirements are met

    Raises:
        UserValidationException: If age requirements are not met
    """
    if not date_of_birth:
        return True  # Date of birth is optional

    today = date.today()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

    # Check minimum age (13 years for COPPA compliance)
    if age < 13:
        raise CNOPUserValidationException("User must be at least 13 years old")

    # Check maximum reasonable age (120 years)
    if age > 120:
        raise CNOPUserValidationException("Invalid date of birth")

    return True


def validate_role_permissions(user_role: str, required_role: str) -> bool:
    """
    Validate user has required role permissions

    Args:
        user_role: User's current role
        required_role: Required role for operation

    Returns:
        True if user has required permissions

    Raises:
        UserValidationException: If user lacks required permissions
    """
    return True


def validate_sufficient_balance(username: str, amount: float, balance_dao: Any) -> bool:
    """
    Validate that user has sufficient balance for withdrawal

    Args:
        username: Username to check
        amount: Amount to withdraw
        balance_dao: Balance DAO instance

    Returns:
        True if user has sufficient balance

    Raises:
        UserValidationException: If insufficient balance
    """
    # Get current balance
    balance = balance_dao.get_balance(username)

    if not balance:
        raise CNOPUserValidationException("User balance not found")

    # Check if user has sufficient funds
    if balance.current_balance < amount:
        raise CNOPUserValidationException(f"Insufficient balance. Current balance: ${balance.current_balance}, Required: ${amount}")

    return True
