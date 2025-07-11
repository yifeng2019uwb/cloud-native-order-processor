import bcrypt
from typing import Optional
from datetime import datetime
import logging
from boto3.dynamodb.conditions import Key
import sys
import os

# Add the src directory to Python path for editor recognition
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from .base_dao import BaseDAO
from src.entities.user import User, UserCreate, UserLogin

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

    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user"""
        try:
            # Check if username already exists
            existing_user_by_username = await self.get_user_by_username(user_create.username)
            if existing_user_by_username:
                raise ValueError(f"User with username {user_create.username} already exists")

            # Check if email already exists
            existing_user_by_email = await self.get_user_by_email(user_create.email)
            if existing_user_by_email:
                raise ValueError(f"User with email {user_create.email} already exists")

            # Hash password
            password_hash = self._hash_password(user_create.password)

            # Create user item with first_name/last_name fields
            now = datetime.utcnow().isoformat()
            user_item = {
                'user_id': user_create.username,  # Primary key
                'username': user_create.username,
                'email': user_create.email,
                'password_hash': password_hash,
                'first_name': user_create.first_name,  # FIXED: Split field
                'last_name': user_create.last_name,    # FIXED: Split field
                'phone': user_create.phone,
                'created_at': now,
                'updated_at': now
            }

            # Save to users table
            created_item = self._safe_put_item(self.db.users_table, user_item)

            return User(
                username=user_create.username,
                email=user_create.email,
                first_name=user_create.first_name,  # FIXED: Split field
                last_name=user_create.last_name,    # FIXED: Split field
                phone=user_create.phone,
                created_at=datetime.fromisoformat(created_item['created_at']),
                updated_at=datetime.fromisoformat(created_item['updated_at'])
            )

        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username (Primary Key lookup)"""
        try:
            logger.info(f"🔍 DEBUG: Looking up user by username: '{username}'")

            key = {
                'user_id': username  # Use single key, not composite
            }

            logger.info(f"🔍 DEBUG: Using key: {key}")

            item = self._safe_get_item(self.db.users_table, key)
            logger.info(f"🔍 DEBUG: Database returned item: {item}")

            if not item:
                logger.warning(f"❌ DEBUG: No user found for username: '{username}'")
                return None

            return User(
                username=item['username'],
                email=item['email'],
                first_name=item.get('first_name', ''),  # FIXED: Split field with fallback
                last_name=item.get('last_name', ''),    # FIXED: Split field with fallback
                phone=item.get('phone'),
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at'])
            )

        except Exception as e:
            logger.error(f"Failed to get user by username {username}: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email (GSI lookup)"""
        try:
            items = self._safe_query(
                self.db.users_table,
                Key('email').eq(email),
                index_name='EmailIndex'
            )

            if not items:
                return None

            # Should only be one user per email
            item = items[0]

            return User(
                username=item['username'],
                email=item['email'],
                first_name=item.get('first_name', ''),  # FIXED: Split field with fallback
                last_name=item.get('last_name', ''),    # FIXED: Split field with fallback
                phone=item.get('phone'),
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at'])
            )

        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            raise

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        try:
            # Determine if identifier is email or username
            user = None

            if '@' in username:
                # Identifier looks like email
                user = await self.get_user_by_email(username)
            else:
                # Identifier looks like username
                user = await self.get_user_by_username(username)

            if not user:
                return None

            # Get the full user record with password hash for verification
            key = {
                'user_id': user.username
            }

            item = self._safe_get_item(self.db.users_table, key)
            if not item:
                return None

            # Verify password
            if not self._verify_password(password, item['password_hash']):
                return None

            return user

        except Exception as e:
            logger.error(f"Failed to authenticate user {username}: {e}")
            raise

    async def update_user(self, username: str, email: Optional[str] = None,
                         first_name: Optional[str] = None, last_name: Optional[str] = None,  # FIXED: Split parameters
                         phone: Optional[str] = None) -> Optional[User]:
        """Update user profile"""
        try:
            updates = {}
            if email is not None:
                # Check if new email already exists (for another user)
                existing_user = await self.get_user_by_email(email)
                if existing_user and existing_user.username != username:
                    raise ValueError(f"Email {email} is already in use by another user")
                updates['email'] = email
            if first_name is not None:  # FIXED: Split field
                updates['first_name'] = first_name
            if last_name is not None:   # FIXED: Split field
                updates['last_name'] = last_name
            if phone is not None:
                updates['phone'] = phone

            if not updates:
                # No updates provided, just return current user
                return await self.get_user_by_username(username)

            # Build update expression
            set_clauses = []
            expression_values = {}

            for field, value in updates.items():
                set_clauses.append(f"{field} = :{field}")
                expression_values[f":{field}"] = value

            # Always update timestamp
            set_clauses.append("updated_at = :updated_at")
            expression_values[":updated_at"] = datetime.utcnow().isoformat()

            update_expression = "SET " + ", ".join(set_clauses)

            key = {
                'user_id': username
            }

            item = self._safe_update_item(
                self.db.users_table,
                key,
                update_expression,
                expression_values
            )

            if not item:
                return None

            return User(
                username=item['username'],
                email=item['email'],
                first_name=item.get('first_name', ''),  # FIXED: Split field with fallback
                last_name=item.get('last_name', ''),    # FIXED: Split field with fallback
                phone=item.get('phone'),
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at'])
            )

        except Exception as e:
            logger.error(f"Failed to update user {username}: {e}")
            raise

    async def delete_user(self, username: str) -> bool:
        """Delete user by username"""
        try:
            key = {
                'user_id': username
            }

            success = self._safe_delete_item(self.db.users_table, key)

            if success:
                logger.info(f"User deleted successfully: {username}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete user {username}: {e}")
            raise