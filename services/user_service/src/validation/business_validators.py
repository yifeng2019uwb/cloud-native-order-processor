"""
User Service Business Validators

Provides business logic validation for the user service.
Handles uniqueness checks and business rules for registration.
"""

from typing import Optional, Any
from datetime import date

# Import proper exceptions
from common.exceptions.shared_exceptions import (
    CNOPUserNotFoundException
)
from user_exceptions import CNOPUserAlreadyExistsException, CNOPUserValidationException


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
    import logging
    logger = logging.getLogger(__name__)

    logger.warning(f"🔍 DEBUG: Starting username uniqueness validation for: '{username}'")

    try:
        # Query database for existing username
        logger.warning(f"🔍 DEBUG: Calling user_dao.get_user_by_username('{username}')")
        existing_user = user_dao.get_user_by_username(username)

        if existing_user:
            logger.warning(f"🔍 DEBUG: User found! Username '{username}' already exists")
            raise CNOPUserAlreadyExistsException(f"Username '{username}' already exists")
        else:
            logger.warning(f"🔍 DEBUG: User not found! Username '{username}' is unique")
            return True

    except CNOPUserNotFoundException as e:
        # User doesn't exist, which means username is unique
        logger.warning(f"🔍 DEBUG: User not found! Username '{username}' is unique. Exception: {str(e)}")
        return True
    except Exception as e:
        # TODO: BACKLOG TASK - This generic exception handler incorrectly catches CNOPUserAlreadyExistsException
        # and converts it to a generic Exception, which then gets caught by the profile controller's
        # generic handler and converted to HTTPException. This breaks the expected exception flow.
        # Consider removing this generic handler or making it more specific.
        logger.warning(f"🔍 DEBUG: Unexpected exception in username validation: {str(e)}")
        raise


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
    import logging
    logger = logging.getLogger(__name__)

    logger.warning(f"🔍 DEBUG: Starting email uniqueness validation for: '{email}'")

    try:
        # Query database for existing email
        logger.warning(f"🔍 DEBUG: Calling user_dao.get_user_by_email('{email}')")
        existing_user = user_dao.get_user_by_email(email)

        if existing_user:
            # TODO: BACKLOG TASK - The exclude_username parameter is not being used!
            # This should check if existing_user.username != exclude_username before raising the exception
            # Currently it raises the exception even when the email belongs to the same user (updating profile)
            logger.warning(f"🔍 DEBUG: User found! Email '{email}' already exists")
            raise CNOPUserAlreadyExistsException(f"Email '{email}' already exists")
        else:
            logger.warning(f"🔍 DEBUG: User not found! Email '{email}' is unique")
            return True

    except CNOPUserNotFoundException as e:
        # User doesn't exist, which means email is unique
        logger.warning(f"🔍 DEBUG: User not found! Email '{email}' is unique. Exception: {str(e)}")
        return True
    except Exception as e:
        # TODO: BACKLOG TASK - This generic exception handler incorrectly catches CNOPUserAlreadyExistsException
        # and converts it to a generic Exception, which then gets caught by the profile controller's
        # generic handler and converted to HTTPException. This breaks the expected exception flow.
        # Consider removing this generic handler or making it more specific.
        logger.warning(f"🔍 DEBUG: Unexpected exception in email validation: {str(e)}")
        raise


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
    # TODO: Implement role permission validation
    # - Check role hierarchy
    # - Return True if authorized, raise UserValidationException if not
    pass


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
