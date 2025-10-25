# Standard library imports
import os
import sys
from datetime import datetime, timezone

# Third-party imports
import pytest
from pydantic import ValidationError

# Local imports - import directly to avoid dependency issues
from src.data.entities.user.user import User, UserItem

# Add src directory to path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

# Test constants
TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "ValidPass123!"
TEST_FIRST_NAME = "Test"
TEST_LAST_NAME = "User"
TEST_PHONE = "+1234567890"
TEST_PASSWORD_HASH = "hashed_password"
TEST_USER_PK = "testuser"
TEST_USER_SK = "USER"
TEST_USERNAME_TOO_LONG = "a" * 51


class TestUser:
    """Test User model validation - Simplified"""

    def test_valid_user_creation(self):
        """Test valid user creation"""
        user = User(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            phone=TEST_PHONE
        )
        assert user.username == TEST_USERNAME
        assert user.email == TEST_EMAIL
        assert user.first_name == TEST_FIRST_NAME
        assert user.last_name == TEST_LAST_NAME
        assert user.phone == TEST_PHONE

    def test_required_fields_validation(self):
        """Test that required fields are enforced"""
        with pytest.raises(ValidationError):
            User()  # Missing all required fields

    def test_username_length_validation(self):
        """Test username length validation"""
        with pytest.raises(ValidationError):
            User(
                username=TEST_USERNAME_TOO_LONG,
                email=TEST_EMAIL,
                password=TEST_PASSWORD,
                first_name=TEST_FIRST_NAME,
                last_name=TEST_LAST_NAME
            )

    def test_optional_fields(self):
        """Test that optional fields work correctly"""
        user = User(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME
            # phone is optional
        )
        assert user.phone is None
        assert user.marketing_emails_consent is False
        assert user.role == "customer"


class TestUserItem:
    """Test UserItem model validation - Simplified"""

    def test_user_item_creation(self):
        """Test valid user item creation"""
        now = datetime.now(timezone.utc)
        user_item = UserItem(
            Pk=TEST_USER_PK,
            Sk=TEST_USER_SK,
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password_hash=TEST_PASSWORD_HASH,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            phone=TEST_PHONE,
            created_at=now,
            updated_at=now
        )
        assert user_item.Pk == TEST_USER_PK
        assert user_item.Sk == TEST_USER_SK
        assert user_item.username == TEST_USERNAME
        assert user_item.email == TEST_EMAIL

    def test_user_item_conversion(self):
        """Test converting between User and UserItem"""
        user = User(
            username=TEST_USERNAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME,
            phone=TEST_PHONE
        )

        # Convert User to UserItem
        user_item = UserItem.from_user(user)
        assert user_item.username == user.username
        assert user_item.email == user.email

        # Convert UserItem back to User
        converted_user = user_item.to_user()
        assert converted_user.username == user.username
        assert converted_user.email == user.email
        assert converted_user.password == "[HASHED]"  # Password should be masked