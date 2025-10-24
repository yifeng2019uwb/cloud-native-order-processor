"""User DAO for user operations using PynamoDB"""
import os
import sys

# Path setup for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Ignore warnings
from ....auth.security.password_manager import PasswordManager
from ....exceptions.shared_exceptions import (
    CNOPInvalidCredentialsException,
    CNOPUserNotFoundException
)
from ....shared.logging import BaseLogger, LogAction, LoggerName
from ...entities.entity_constants import UserFields
from ...entities.user import User, UserItem

logger = BaseLogger(LoggerName.DATABASE, log_to_file=True)


class UserDAO:
    """Data Access Object for user operations using PynamoDB"""

    def __init__(self, db_connection=None):
        """Initialize UserDAO with password manager (PynamoDB doesn't need db_connection)"""
        self.password_manager = PasswordManager()

    def create_user(self, user: User) -> User:
        """Create a new user"""
        try:
            # Hash password
            password_hash = self.password_manager.hash_password(user.password)

            # Convert User to UserItem with PynamoDB
            user_item = UserItem.from_user(user)
            user_item.password_hash = password_hash

            # Save using PynamoDB (automatically handles timestamps)
            user_item.save()

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"User created successfully: username={user.username}, email={user.email}"
            )

            # Convert back to User domain model
            return user_item.to_user()

        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to create user {user.username}: {str(e)}"
            )
            raise

    def get_user_by_username(self, username: str) -> User:
        """Get user by username (Primary Key lookup)"""
        try:
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Looking up user by username: '{username}'"
            )

            # Use PynamoDB to get user by primary key
            user_item = UserItem.get(username, UserFields.SK_VALUE)

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"User found: {username}"
            )

            # Convert to User domain model
            return user_item.to_user()

        except UserItem.DoesNotExist:
            logger.warning(
                action=LogAction.DB_OPERATION,
                message=f"User not found: {username}"
            )
            raise CNOPUserNotFoundException(f"User with username '{username}' not found")
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to get user {username}: {str(e)}"
            )
            raise

    def get_user_by_email(self, email: str) -> User:
        """Get user by email (GSI lookup)"""
        try:
            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"Looking up user by email: '{email}'"
            )

            # Use PynamoDB GSI to query by email
            for user_item in UserItem.email_index.query(email):
                logger.info(
                    action=LogAction.DB_OPERATION,
                    message=f"User found by email: {email}"
                )
                return user_item.to_user()

            # No user found
            logger.warning(
                action=LogAction.DB_OPERATION,
                message=f"User not found by email: {email}"
            )
            raise CNOPUserNotFoundException(f"User with email '{email}' not found")

        except CNOPUserNotFoundException:
            raise
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to get user by email {email}: {str(e)}"
            )
            raise

    def authenticate_user(self, username: str, password: str) -> User:
        """Authenticate user with username and password"""
        try:
            # Get user (this will raise CNOPUserNotFoundException if not found)
            user = self.get_user_by_username(username)

            # Get the stored password hash using PynamoDB
            user_item = UserItem.get(username, UserFields.SK_VALUE)
            stored_hash = user_item.password_hash

            if not stored_hash:
                logger.error(
                    action=LogAction.ERROR,
                    message=f"No password hash found for user {username}"
                )
                raise CNOPInvalidCredentialsException(f"Invalid credentials for user '{username}'")

            # Verify password
            if self.password_manager.verify_password(password, stored_hash):
                logger.info(
                    action=LogAction.DB_OPERATION,
                    message=f"User authenticated successfully: {username}"
                )
                return user
            else:
                logger.warning(
                    action=LogAction.ERROR,
                    message=f"Invalid password for user: {username}"
                )
                raise CNOPInvalidCredentialsException(f"Invalid credentials for user '{username}'")

        except CNOPUserNotFoundException:
            raise
        except CNOPInvalidCredentialsException:
            raise
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to authenticate user {username}: {str(e)}"
            )
            raise

    def update_user(self, user: User) -> User:
        """Update user information"""
        try:
            # Get existing user item using PynamoDB
            user_item = UserItem.get(user.username, UserFields.SK_VALUE)

            # Update fields if they are provided (not None)
            if user.email is not None:
                user_item.email = user.email
            if user.first_name is not None:
                user_item.first_name = user.first_name
            if user.last_name is not None:
                user_item.last_name = user.last_name
            if user.phone is not None:
                user_item.phone = user.phone
            if user.date_of_birth is not None:
                user_item.date_of_birth = user.date_of_birth.isoformat() if user.date_of_birth else None
            if user.marketing_emails_consent is not None:
                user_item.marketing_emails_consent = user.marketing_emails_consent
            if user.role is not None:
                user_item.role = user.role

            # Save the updated item (PynamoDB will automatically update updated_at)
            user_item.save()

            logger.info(
                action=LogAction.DB_OPERATION,
                message=f"User updated successfully: {user.username}"
            )

            # Convert back to User domain model
            return user_item.to_user()

        except UserItem.DoesNotExist:
            logger.warning(
                action=LogAction.ERROR,
                message=f"User not found for update: {user.username}"
            )
            raise CNOPUserNotFoundException(f"User with username '{user.username}' not found")
        except Exception as e:
            logger.error(
                action=LogAction.ERROR,
                message=f"Failed to update user {user.username}: {str(e)}"
            )
            raise
