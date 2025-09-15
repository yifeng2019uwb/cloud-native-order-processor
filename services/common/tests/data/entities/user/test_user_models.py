# Standard library imports
import os
import sys

# Third-party imports
import pytest
from pydantic import ValidationError

# Local imports - import directly to avoid dependency issues
from src.data.entities.user.user import User, UserItem

# Add src directory to path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))


class TestUser:
    """Test User model validation"""

    def test_valid_user(self):
        """Test valid user data"""
        user_data = {
            "username": "john_doe123",
            "email": "test@example.com",
            "password": "ValidPass123!",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890"
        }
        user = User(**user_data)
        assert user.username == "john_doe123"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.phone == "+1234567890"

    def test_username_validation_valid(self):
        """Test valid username formats - simple DB constraints only"""
        valid_usernames = [
            "john_doe",      # Valid username
            "user123",       # Valid username
            "test_user_123", # Valid username
            "johnsmith"      # Valid username
        ]

        for username in valid_usernames:
            user = User(
                username=username,
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",
                last_name="User",
                phone="+1234567890"
            )
            assert user.username == username

    def test_username_validation_invalid(self):
        """Test invalid username formats - simple DB constraints only"""
        invalid_usernames = [
            "a" * 51,         # Too long (over 50 chars)
        ]

        for username in invalid_usernames:
            with pytest.raises(ValidationError):
                User(
                    username=username,
                    email="test@example.com",
                    password="ValidPass123!",
                    first_name="Test",
                    last_name="User",
                    phone="+1234567890"
                )

    def test_email_validation_valid(self):
        """Test valid email formats"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org"
        ]

        for email in valid_emails:
            user = User(
                username="testuser",
                email=email,
                password="ValidPass123!",
                first_name="Test",
                last_name="User",
                phone="+1234567890"
            )
            assert user.email == email

    def test_password_validation_valid(self):
        """Test valid password formats"""
        valid_passwords = [
            "ValidPass123!",
            "AnotherPass456@",
            "Test123$"
        ]

        for password in valid_passwords:
            user = User(
                username="testuser",
                email="test@example.com",
                password=password,
                first_name="Test",
                last_name="User",
                phone="+1234567890"
            )
            assert user.password == password

    def test_password_validation_invalid(self):
        """Test invalid password formats - only length validation"""
        invalid_passwords = [
            "a" * 201,        # Too long (over 200 chars)
        ]

        for password in invalid_passwords:
            with pytest.raises(ValidationError):
                User(
                    username="testuser",
                    email="test@example.com",
                    password=password,
                    first_name="Test",
                    last_name="User",
                    phone="+1234567890"
                )

    def test_required_fields(self):
        """Test that required fields are enforced"""
        # Missing username
        with pytest.raises(ValidationError):
            User(
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",
                last_name="User",
                phone="+1234567890"
            )

        # Missing email
        with pytest.raises(ValidationError):
            User(
                username="testuser",
                password="ValidPass123!",
                first_name="Test",
                last_name="User",
                phone="+1234567890"
            )

        # Missing password
        with pytest.raises(ValidationError):
            User(
                username="testuser",
                email="test@example.com",
                first_name="Test",
                last_name="User",
                phone="+1234567890"
            )

        # Missing first_name
        with pytest.raises(ValidationError):
            User(
                username="testuser",
                email="test@example.com",
                password="ValidPass123!",
                last_name="User",
                phone="+1234567890"
            )

        # Missing last_name
        with pytest.raises(ValidationError):
            User(
                username="testuser",
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",
                phone="+1234567890"
            )

    def test_optional_fields(self):
        """Test that optional fields work correctly"""
        user = User(
            username="testuser",
            email="test@example.com",
            password="ValidPass123!",
            first_name="Test",
            last_name="User"
            # phone is optional
        )
        assert user.phone is None
        assert user.date_of_birth is None
        assert user.marketing_emails_consent is False
        assert user.role == "customer"

    def test_default_values(self):
        """Test default values for optional fields"""
        user = User(
            username="testuser",
            email="test@example.com",
            password="ValidPass123!",
            first_name="Test",
            last_name="User"
        )
        assert user.marketing_emails_consent is False
        assert user.role == "customer"
        assert user.date_of_birth is None


class TestUserItem:
    """Test UserItem model validation"""

    def test_valid_user_item(self):
        """Test valid user item data"""
        from datetime import datetime
        now = datetime.utcnow()
        user_item_data = {
            "Pk": "testuser",
            "Sk": "USER",
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890",
            "created_at": now,
            "updated_at": now
        }
        user_item = UserItem(**user_item_data)
        assert user_item.Pk == "testuser"
        assert user_item.Sk == "USER"
        assert user_item.username == "testuser"
        assert user_item.email == "test@example.com"
        assert user_item.password_hash == "hashed_password"

    def test_user_item_from_user(self):
        """Test converting User to UserItem"""
        user = User(
            username="testuser",
            email="test@example.com",
            password="ValidPass123!",
            first_name="Test",
            last_name="User",
            phone="+1234567890"
        )
        user_item = UserItem.from_user(user)
        assert user_item.username == user.username
        assert user_item.email == user.email
        assert user_item.first_name == user.first_name
        assert user_item.last_name == user.last_name
        assert user_item.phone == user.phone

    def test_user_item_to_user(self):
        """Test converting UserItem to User"""
        from datetime import datetime
        now = datetime.utcnow()
        user_item = UserItem(
            Pk="testuser",
            Sk="USER",
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            phone="+1234567890",
            created_at=now,
            updated_at=now
        )
        user = user_item.to_user()
        assert user.username == user_item.username
        assert user.email == user_item.email
        assert user.first_name == user_item.first_name
        assert user.last_name == user_item.last_name
        assert user.phone == user_item.phone
        assert user.password == "[HASHED]"  # Password should be masked
