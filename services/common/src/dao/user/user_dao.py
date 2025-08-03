import bcrypt
from typing import Optional
from datetime import datetime
import logging
from boto3.dynamodb.conditions import Key
import sys
import os

# Add the src directory to Python path for editor recognition
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ..base_dao import BaseDAO
from ...entities.user import User, UserCreate, UserLogin
from ...entities.user import DEFAULT_USER_ROLE
from ...exceptions import DatabaseOperationException
from ...exceptions.shared_exceptions import EntityNotFoundException, InvalidCredentialsException


logger = logging.getLogger(__name__)


class UserDAO(BaseDAO):
    """Data Access Object for user operations"""

    def _hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user"""
        try:
            # Hash password
            password_hash = self._hash_password(user_create.password)

            # Create user item with new schema
            now = datetime.utcnow().isoformat()
            user_item = {
                'Pk': user_create.username,  # Primary key
                'Sk': 'USER',  # Sort key for user records
                'username': user_create.username,  # For easy access
                'email': user_create.email,
                'password_hash': password_hash,
                'first_name': user_create.first_name,
                'last_name': user_create.last_name,
                'phone': user_create.phone,
                'role': user_create.role,
                'created_at': now,
                'updated_at': now
            }

            # Save to users table
            created_item = self._safe_put_item(self.db.users_table, user_item)

            return User(
                Pk=user_create.username,
                Sk='USER',
                username=user_create.username,
                email=user_create.email,
                first_name=user_create.first_name,
                last_name=user_create.last_name,
                phone=user_create.phone,
                role=user_create.role,
                created_at=datetime.fromisoformat(created_item['created_at']),
                updated_at=datetime.fromisoformat(created_item['updated_at'])
            )

        except Exception as e:
            logger.error(f"Failed to create user '{user_create.username}': {e}")
            raise DatabaseOperationException(f"Database operation failed while creating user '{user_create.username}': {str(e)}")

    def get_user_by_username(self, username: str) -> User:
        """Get user by username (Primary Key lookup)"""
        # Simplified: base_dao._safe_get_item handles all exception cases
        logger.info(f"🔍 DEBUG: Looking up user by username: '{username}'")

        key = {
            'Pk': username,  # Primary key
            'Sk': 'USER'  # Sort key for user records
        }

        logger.info(f"🔍 DEBUG: Using key: {key}")

        item = self._safe_get_item(self.db.users_table, key)
        logger.info(f"🔍 DEBUG: Database returned item: {item}")

        return User(
            Pk=item['Pk'],
            Sk=item['Sk'],
            username=item['username'],
            email=item['email'],
            first_name=item.get('first_name', ''),
            last_name=item.get('last_name', ''),
            phone=item.get('phone'),
            role=item.get('role', DEFAULT_USER_ROLE),
            created_at=datetime.fromisoformat(item['created_at']),
            updated_at=datetime.fromisoformat(item['updated_at'])
        )

    def get_user_by_email(self, email: str) -> User:
        """Get user by email (GSI lookup)"""
        # Simplified: base_dao._safe_query handles database exceptions
        items = self._safe_query(
            self.db.users_table,
            Key('email').eq(email),
            index_name='EmailIndex'
        )

        if not items:
            raise EntityNotFoundException(f"User with email '{email}' not found")

        # Should only be one user per email
        item = items[0]

        return User(
            Pk=item['Pk'],
            Sk=item['Sk'],
            username=item['username'],
            email=item['email'],
            first_name=item.get('first_name', ''),
            last_name=item.get('last_name', ''),
            phone=item.get('phone'),
            role=item.get('role', DEFAULT_USER_ROLE),
            created_at=datetime.fromisoformat(item['created_at']),
            updated_at=datetime.fromisoformat(item['updated_at'])
        )

    def authenticate_user(self, username: str, password: str) -> User:
        """Authenticate user with username and password"""
        # Simplified: base_dao._safe_get_item handles database exceptions
        user = self.get_user_by_username(username)

        # Get the stored password hash
        key = {'Pk': username, 'Sk': 'USER'}
        item = self._safe_get_item(self.db.users_table, key)

        stored_hash = item.get('password_hash')
        if not stored_hash:
            logger.error(f"No password hash found for user {username}")
            raise InvalidCredentialsException(f"Invalid credentials for user '{username}'")

        # Verify password
        if self._verify_password(password, stored_hash):
            return user
        else:
            raise InvalidCredentialsException(f"Invalid credentials for user '{username}'")

    def update_user(self, username: str, email: Optional[str] = None,
                    first_name: Optional[str] = None, last_name: Optional[str] = None,  # FIXED: Split parameters
                    phone: Optional[str] = None) -> User:
        """Update user information"""
        # Simplified: base_dao._safe_update_item handles database exceptions
        # Check if user exists
        existing_user = self.get_user_by_username(username)

        # Build update expression and values
        update_parts = []
        expression_values = {}
        expression_names = {}

        if email is not None:
            update_parts.append("#email = :email")
            expression_values[":email"] = email
            expression_names["#email"] = "email"

        if first_name is not None:
            update_parts.append("#first_name = :first_name")
            expression_values[":first_name"] = first_name
            expression_names["#first_name"] = "first_name"

        if last_name is not None:
            update_parts.append("#last_name = :last_name")
            expression_values[":last_name"] = last_name
            expression_names["#last_name"] = "last_name"

        if phone is not None:
            update_parts.append("#phone = :phone")
            expression_values[":phone"] = phone
            expression_names["#phone"] = "phone"

        # Always update the updated_at timestamp
        update_parts.append("#updated_at = :updated_at")
        expression_values[":updated_at"] = datetime.utcnow().isoformat()
        expression_names["#updated_at"] = "updated_at"

        if not update_parts:
            logger.warning(f"No fields to update for user {username}")
            return existing_user

        update_expression = "SET " + ", ".join(update_parts)

        # Perform the update
        key = {'Pk': username, 'Sk': 'USER'}
        updated_item = self._safe_update_item(
            self.db.users_table,
            key,
            update_expression,
            expression_values,
            expression_names
        )

        # Return updated user
        return User(
            Pk=updated_item['Pk'],
            Sk=updated_item['Sk'],
            username=updated_item['username'],
            email=updated_item['email'],
            first_name=updated_item.get('first_name', ''),
            last_name=updated_item.get('last_name', ''),
            phone=updated_item.get('phone'),
            role=updated_item.get('role', DEFAULT_USER_ROLE),
            created_at=datetime.fromisoformat(updated_item['created_at']),
            updated_at=datetime.fromisoformat(updated_item['updated_at'])
        )

    def delete_user(self, username: str) -> bool:
        """Delete a user by username"""
        # Simplified: base_dao._safe_delete_item handles database exceptions
        key = {'Pk': username, 'Sk': 'USER'}
        return self._safe_delete_item(self.db.users_table, key)