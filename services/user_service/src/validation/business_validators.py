"""
User Service Business Validators

Provides business logic validation for the user service.
Handles uniqueness checks and business rules for registration.
"""

from typing import Optional, Any
from datetime import date

# Import proper exceptions
from common.exceptions import (
    UserNotFoundException,
    UserValidationException
)
from user_exceptions import UserAlreadyExistsException


async def validate_username_uniqueness(username: str, user_dao: Any, exclude_user_id: Optional[str] = None) -> bool:
    """
    Validate that username is unique in the system

    Args:
        username: Username to check
        user_dao: User DAO instance
        exclude_user_id: User ID to exclude from check (for updates)

    Returns:
        True if username is unique

    Raises:
        UserAlreadyExistsException: If username already exists
    """
    # Query database for existing username
    existing_user = await user_dao.get_user_by_username(username)

    if existing_user:
        # If we're updating, exclude the current user
        if exclude_user_id and existing_user.id == exclude_user_id:
            return True

        raise UserAlreadyExistsException(f"Username '{username}' already exists")

    return True


async def validate_email_uniqueness(email: str, user_dao: Any, exclude_user_id: Optional[str] = None) -> bool:
    """
    Validate that email is unique in the system

    Args:
        email: Email to check
        user_dao: User DAO instance
        exclude_user_id: User ID to exclude from check (for updates)

    Returns:
        True if email is unique

    Raises:
        UserAlreadyExistsException: If email already exists
    """
    # Query database for existing email
    existing_user = await user_dao.get_user_by_email(email)

    if existing_user:
        # If we're updating, exclude the current user
        if exclude_user_id and existing_user.id == exclude_user_id:
            return True

        raise UserAlreadyExistsException(f"Email '{email}' already exists")

    return True


async def validate_user_exists(user_id: str, user_dao: Any) -> bool:
    """
    Validate that user exists in the system

    Args:
        user_id: User ID to check
        user_dao: User DAO instance

    Returns:
        True if user exists

    Raises:
        UserNotFoundException: If user doesn't exist
    """
    # Query database for user existence
    user = await user_dao.get_user_by_id(user_id)

    if not user:
        raise UserNotFoundException(f"User with ID '{user_id}' not found")

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
        raise UserValidationException("User must be at least 13 years old")

    # Check maximum reasonable age (120 years)
    if age > 120:
        raise UserValidationException("Invalid date of birth")

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