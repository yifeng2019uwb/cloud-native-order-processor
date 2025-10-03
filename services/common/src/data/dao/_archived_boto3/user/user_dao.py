import os
import sys
from datetime import datetime
from typing import Optional

from boto3.dynamodb.conditions import Key

# Path setup for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ....auth.security import PasswordManager
from ....exceptions.shared_exceptions import (CNOPInvalidCredentialsException,
                                              CNOPUserNotFoundException)
from ....shared.logging import BaseLogger, LogActions, Loggers
from ...entities.entity_constants import TimestampFields, UserFields
from ...entities.user import DEFAULT_USER_ROLE, User, UserItem
from ..base_dao import BaseDAO

logger = BaseLogger(Loggers.DATABASE, log_to_file=True)


class UserDAO(BaseDAO):
    """Data Access Object for user operations"""

    def __init__(self, db_connection):
        """Initialize UserDAO with database connection and password manager"""
        super().__init__(db_connection)
        self.password_manager = PasswordManager()
        # Table reference
        self.table = self.db.users_table

    def create_user(self, user: User) -> User:
        """Create a new user"""
        # Hash password
        password_hash = self.password_manager.hash_password(user.password)

        # Convert User to UserItem
        user_item = UserItem.from_user(user)

        # Set the hashed password in the UserItem
        user_item.password_hash = password_hash

        now = datetime.utcnow().isoformat()
        user_item.created_at = now
        user_item.updated_at = now
        # Save to users table
        created_item = self._safe_put_item(self.table, user_item.model_dump())

        logger.info(
            action=LogActions.DB_OPERATION,
            message=f"User created successfully: username={user.username}, email={user.email}"
        )

        # Convert created item back to UserItem then to User
        created_user_item = UserItem(**created_item)
        user = created_user_item.to_user()
        return user

    def get_user_by_username(self, username: str) -> User:
        """Get user by username (Primary Key lookup)"""
        logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Looking up user by username: '{username}'"
        )

        key = UserItem.get_key_for_username(username)

        logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Using key: {key}"
        )

        item = self._safe_get_item(self.table, key)
        logger.info(
            action=LogActions.DB_OPERATION,
            message=f"Database returned item: {item}"
        )

        if not item:
            raise CNOPUserNotFoundException(f"User with username '{username}' not found")

        # Convert dict to UserItem then to User
        user_item = UserItem(**item)
        user = user_item.to_user()
        return user

    def get_user_by_email(self, email: str) -> User:
        """Get user by email (GSI lookup)"""
        items = self._safe_query(
            self.table,
            Key(UserFields.EMAIL).eq(email),
            index_name='EmailIndex'
        )

        if not items:
            raise CNOPUserNotFoundException(f"User with email '{email}' not found")

        # Should only be one user per email
        item = items[0]

        # Convert dict to UserItem then to User
        user_item = UserItem(**item)
        user = user_item.to_user()
        return user

    def authenticate_user(self, username: str, password: str) -> User:
        """Authenticate user with username and password"""
        user = self.get_user_by_username(username)

        # Get the stored password hash
        key = UserItem.get_key_for_username(username)
        item = self._safe_get_item(self.table, key)

        stored_hash = item.get(UserFields.PASSWORD_HASH)
        if not stored_hash:
            logger.error(
                action=LogActions.ERROR,
                message=f"No password hash found for user {username}"
            )
            raise CNOPInvalidCredentialsException(f"Invalid credentials for user '{username}'")

        # Verify password
        if self.password_manager.verify_password(password, stored_hash):
            return user
        else:
            raise CNOPInvalidCredentialsException(f"Invalid credentials for user '{username}'")

    def update_user(self, user: User) -> User:
        """Update user information"""
        # Check if user exists by getting from database directly
        key = UserItem.get_key_for_username(user.username)
        existing_item = self._safe_get_item(self.table, key)
        if not existing_item:
            raise CNOPUserNotFoundException(f"User with username '{user.username}' not found")

        # Build update expression and values
        update_parts = []
        expression_values = {}
        expression_names = {}

        if user.email is not None:
            update_parts.append(f"#{UserFields.EMAIL} = :{UserFields.EMAIL}")
            expression_values[f":{UserFields.EMAIL}"] = user.email
            expression_names[f"#{UserFields.EMAIL}"] = UserFields.EMAIL

        if user.first_name is not None:
            update_parts.append(f"#{UserFields.FIRST_NAME} = :{UserFields.FIRST_NAME}")
            expression_values[f":{UserFields.FIRST_NAME}"] = user.first_name
            expression_names[f"#{UserFields.FIRST_NAME}"] = UserFields.FIRST_NAME

        if user.last_name is not None:
            update_parts.append(f"#{UserFields.LAST_NAME} = :{UserFields.LAST_NAME}")
            expression_values[f":{UserFields.LAST_NAME}"] = user.last_name
            expression_names[f"#{UserFields.LAST_NAME}"] = UserFields.LAST_NAME

        if user.phone is not None:
            update_parts.append(f"#{UserFields.PHONE} = :{UserFields.PHONE}")
            expression_values[f":{UserFields.PHONE}"] = user.phone
            expression_names[f"#{UserFields.PHONE}"] = UserFields.PHONE

        # Always update the updated_at timestamp
        update_parts.append(f"#{TimestampFields.UPDATED_AT} = :{TimestampFields.UPDATED_AT}")
        expression_values[f":{TimestampFields.UPDATED_AT}"] = datetime.utcnow().isoformat()
        expression_names[f"#{TimestampFields.UPDATED_AT}"] = TimestampFields.UPDATED_AT

        if not update_parts:
            logger.warning(
                action=LogActions.ERROR,
                message=f"No fields to update for user {user.username}"
            )
            # Return existing user with hidden password
            existing_user_item = UserItem(**existing_item)
            user = existing_user_item.to_user()
            user.password = UserFields.HASHED_PASSWORD_MARKER
            return user

        update_expression = "SET " + ", ".join(update_parts)

        # Perform the update
        key = UserItem.get_key_for_username(user.username)
        updated_item = self._safe_update_item(
            self.table,
            key,
            update_expression,
            expression_values,
            expression_names
        )

        logger.info(
            action=LogActions.DB_OPERATION,
            message=f"User updated successfully: {user}"
        )

        # Convert updated item to UserItem then to User
        user_item = UserItem(**updated_item)
        user = user_item.to_user()
        return user
