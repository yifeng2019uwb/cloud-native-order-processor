import bcrypt
from typing import Optional
from datetime import datetime
import logging
from boto3.dynamodb.conditions import Key

from .base_dao import BaseDAO
from ..config.dynamodb_connection import DynamoDBConnection
from ...models.user import User, UserCreate

logger = logging.getLogger(__name__)


class UserDAO(BaseDAO):
    """Data Access Object for user operations using DynamoDB single table"""

    def _get_entity_type(self) -> str:
        return "USER"

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
            # Check if user already exists
            existing_user = await self.get_user_by_email(user_create.email)
            if existing_user:
                raise ValueError(f"User with email {user_create.email} already exists")

            # Hash password
            password_hash = self._hash_password(user_create.password)

            # Create user item for DynamoDB single table
            user_item = {
                'PK': self._create_primary_key(user_create.email),
                'SK': 'PROFILE',
                'email': user_create.email,
                'password_hash': password_hash,
                'name': user_create.name,
                'phone': user_create.phone,
                'entity_type': self._get_entity_type()
            }

            # Add timestamps
            self._add_timestamps(user_item, is_create=True)

            # Validate required fields
            self._validate_required_fields(user_item, ['email', 'name', 'password_hash'])

            # Use orders table (single table design)
            created_item = self._safe_put_item(self.db.orders_table, user_item)

            return User(
                email=user_create.email,
                name=user_create.name,
                phone=user_create.phone,
                created_at=datetime.fromisoformat(created_item['created_at']),
                updated_at=datetime.fromisoformat(created_item['updated_at'])
            )

        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            key = {
                'PK': self._create_primary_key(email),
                'SK': 'PROFILE'
            }

            item = self._safe_get_item(self.db.orders_table, key)
            if not item:
                return None

            return User(
                email=item['email'],
                name=item['name'],
                phone=item.get('phone'),
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at'])
            )

        except Exception as e:
            logger.error(f"Failed to get user {email}: {e}")
            raise

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            key = {
                'PK': self._create_primary_key(email),
                'SK': 'PROFILE'
            }

            item = self._safe_get_item(self.db.orders_table, key)
            if not item:
                return None

            # Verify password
            if not self._verify_password(password, item['password_hash']):
                return None

            return User(
                email=item['email'],
                name=item['name'],
                phone=item.get('phone'),
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at'])
            )

        except Exception as e:
            logger.error(f"Failed to authenticate user {email}: {e}")
            raise

    async def update_user(self, email: str, name: Optional[str] = None, phone: Optional[str] = None) -> Optional[User]:
        """Update user profile"""
        try:
            updates = {}
            if name is not None:
                updates['name'] = name
            if phone is not None:
                updates['phone'] = phone

            if not updates:
                # No updates provided, just return current user
                return await self.get_user_by_email(email)

            key = {
                'PK': self._create_primary_key(email),
                'SK': 'PROFILE'
            }

            update_expression, expression_values, expression_names = self._build_update_expression(updates)

            item = self._safe_update_item(
                self.db.orders_table,
                key,
                update_expression,
                expression_values,
                expression_names
            )

            if not item:
                return None

            return User(
                email=item['email'],
                name=item['name'],
                phone=item.get('phone'),
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at'])
            )

        except Exception as e:
            logger.error(f"Failed to update user {email}: {e}")
            raise