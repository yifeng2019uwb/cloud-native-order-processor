import bcrypt
from typing import Optional
from datetime import datetime
import logging
from boto3.dynamodb.conditions import Key

from ..config.dynamodb_connection import DynamoDBConnection
from ...models.user import User, UserCreate

logger = logging.getLogger(__name__)


class UserDAO:
    """Data Access Object for user operations using DynamoDB single table"""

    def __init__(self, db_connection: DynamoDBConnection):
        self.db = db_connection

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
            now = datetime.utcnow()

            # Check if user already exists
            existing_user = await self.get_user_by_email(user_create.email)
            if existing_user:
                raise ValueError(f"User with email {user_create.email} already exists")

            # Hash password
            password_hash = self._hash_password(user_create.password)

            # Create user item for DynamoDB single table
            user_item = {
                'PK': f"USER#{user_create.email}",
                'SK': 'PROFILE',
                'email': user_create.email,
                'password_hash': password_hash,
                'name': user_create.name,
                'phone': user_create.phone,
                'entity_type': 'USER',
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }

            # Use orders table (single table design)
            response = self.db.orders_table.put_item(Item=user_item)

            return User(
                email=user_create.email,
                name=user_create.name,
                phone=user_create.phone,
                created_at=now,
                updated_at=now
            )

        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            response = self.db.orders_table.get_item(
                Key={
                    'PK': f"USER#{email}",
                    'SK': 'PROFILE'
                }
            )

            item = response.get('Item')
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
            response = self.db.orders_table.get_item(
                Key={
                    'PK': f"USER#{email}",
                    'SK': 'PROFILE'
                }
            )

            item = response.get('Item')
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
            update_expression = "SET updated_at = :updated_at"
            expression_values = {':updated_at': datetime.utcnow().isoformat()}

            if name is not None:
                update_expression += ", #name = :name"
                expression_values[':name'] = name

            if phone is not None:
                update_expression += ", phone = :phone"
                expression_values[':phone'] = phone

            response = self.db.orders_table.update_item(
                Key={
                    'PK': f"USER#{email}",
                    'SK': 'PROFILE'
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames={'#name': 'name'} if name is not None else None,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )

            item = response.get('Attributes')
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