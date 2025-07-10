import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

import pytest
from pydantic import ValidationError
from models.user import UserCreate, User, UserResponse, UserLogin


class TestUserCreate:
    """Test UserCreate model validation"""

    def test_valid_user_create(self):
        """Test valid user creation data"""
        user_data = {
            "username": "john_doe123",
            "email": "test@example.com",
            "password": "ValidPass123!",
            "name": "Test User",
            "phone": "+1234567890"
        }
        user = UserCreate(**user_data)
        assert user.username == "john_doe123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.phone == "+1234567890"

    def test_username_validation_valid(self):
        """Test valid username formats"""
        valid_usernames = [
            "john",          # Single word
            "john_doe",      # With underscore
            "user123",       # With numbers
            "a",             # Single character
            "test_user_123", # Multiple underscores and numbers
            "JohnDoe"        # Mixed case (should become lowercase)
        ]

        for username in valid_usernames:
            user = UserCreate(
                username=username,
                email="test@example.com",
                password="ValidPass123!",
                name="Test User"
            )
            # Username should be converted to lowercase
            assert user.username == username.lower()

    def test_username_too_short(self):
        """Test username length validation - too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab",  # Only 2 chars
                email="test@example.com",
                password="ValidPass123!",
                name="Test User"
            )
        assert "Username must be 3-30 characters long" in str(exc_info.value)

    def test_username_too_long(self):
        """Test username length validation - too long"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="a" * 31,  # 31 chars
                email="test@example.com",
                password="ValidPass123!",
                name="Test User"
            )
        assert "Username must be 3-30 characters long" in str(exc_info.value)

    def test_username_invalid_format(self):
        """Test username format validation"""
        invalid_usernames = [
            "_john",         # Starts with underscore
            "john_",         # Ends with underscore
            "john__doe",     # Consecutive underscores
            "john-doe",      # Contains hyphen
            "john doe",      # Contains space
            "john@doe",      # Contains @ symbol
            "john.doe",      # Contains period
        ]

        for username in invalid_usernames:
            with pytest.raises(ValidationError) as exc_info:
                UserCreate(
                    username=username,
                    email="test@example.com",
                    password="ValidPass123!",
                    name="Test User"
                )
            error_msg = str(exc_info.value)
            # Should contain one of these error messages
            assert any(msg in error_msg for msg in [
                "Username can only contain letters, numbers, and underscores",
                "Username cannot contain consecutive underscores"
            ])

    def test_username_empty(self):
        """Test username cannot be empty"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="",
                email="test@example.com",
                password="ValidPass123!",
                name="Test User"
            )
        assert "Username cannot be empty" in str(exc_info.value)

    def test_username_whitespace_only(self):
        """Test username cannot be whitespace only"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="   ",
                email="test@example.com",
                password="ValidPass123!",
                name="Test User"
            )
        assert "Username cannot be empty" in str(exc_info.value)

    def test_password_too_short(self):
        """Test password length validation - too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="test@example.com",
                password="Short1!",  # Only 7 chars
                name="Test User"
            )
        assert "Password must be 12-20 characters long" in str(exc_info.value)

    def test_password_too_long(self):
        """Test password length validation - too long"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="test@example.com",
                password="ThisPasswordIsTooLong123!",  # 25 chars
                name="Test User"
            )
        assert "Password must be 12-20 characters long" in str(exc_info.value)

    def test_password_no_uppercase(self):
        """Test password requires uppercase"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="test@example.com",
                password="validpass123!",  # No uppercase
                name="Test User"
            )
        assert "Password must contain at least one uppercase letter" in str(exc_info.value)

    def test_password_no_lowercase(self):
        """Test password requires lowercase"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="test@example.com",
                password="VALIDPASS123!",  # No lowercase
                name="Test User"
            )
        assert "Password must contain at least one lowercase letter" in str(exc_info.value)

    def test_password_no_number(self):
        """Test password requires number"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="test@example.com",
                password="ValidPassword!",  # No number
                name="Test User"
            )
        assert "Password must contain at least one number" in str(exc_info.value)

    def test_password_no_special_char(self):
        """Test password requires special character"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="test@example.com",
                password="ValidPass123",  # No special char
                name="Test User"
            )
        assert "Password must contain at least one special character" in str(exc_info.value)

    def test_invalid_email(self):
        """Test email validation"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="invalid-email",
                password="ValidPass123!",
                name="Test User"
            )
        assert "value is not a valid email address" in str(exc_info.value)

    def test_empty_name(self):
        """Test name cannot be empty"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="test@example.com",
                password="ValidPass123!",
                name="   "  # Only whitespace
            )
        assert "Name cannot be empty" in str(exc_info.value)

    def test_invalid_phone_too_short(self):
        """Test phone validation - too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="test@example.com",
                password="ValidPass123!",
                name="Test User",
                phone="123"  # Too short
            )
        assert "Phone number must be 10-15 digits" in str(exc_info.value)

    def test_invalid_phone_too_long(self):
        """Test phone validation - too long"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="test@example.com",
                password="ValidPass123!",
                name="Test User",
                phone="12345678901234567890"  # Too long
            )
        assert "Phone number must be 10-15 digits" in str(exc_info.value)

    def test_valid_phone_formats(self):
        """Test various valid phone formats"""
        valid_phones = [
            "+1234567890",
            "1234567890",
            "(123) 456-7890",
            "123-456-7890",
            "+1 (123) 456-7890"
        ]

        for phone in valid_phones:
            user = UserCreate(
                username="john_doe",
                email="test@example.com",
                password="ValidPass123!",
                name="Test User",
                phone=phone
            )
            assert user.phone == phone

    def test_optional_phone(self):
        """Test phone is optional"""
        user = UserCreate(
            username="john_doe",
            email="test@example.com",
            password="ValidPass123!",
            name="Test User"
        )
        assert user.phone is None


class TestUserLogin:
    """Test UserLogin model"""

    def test_valid_login_with_username(self):
        """Test valid login with username"""
        login = UserLogin(
            identifier="john_doe",
            password="ValidPass123!"
        )
        assert login.identifier == "john_doe"
        assert login.password == "ValidPass123!"

    def test_valid_login_with_email(self):
        """Test valid login with email"""
        login = UserLogin(
            identifier="test@example.com",
            password="ValidPass123!"
        )
        assert login.identifier == "test@example.com"
        assert login.password == "ValidPass123!"

    def test_empty_identifier(self):
        """Test login with empty identifier"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(
                identifier="",
                password="ValidPass123!"
            )
        assert "Username or email cannot be empty" in str(exc_info.value)

    def test_whitespace_identifier(self):
        """Test login with whitespace identifier"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(
                identifier="   ",
                password="ValidPass123!"
            )
        assert "Username or email cannot be empty" in str(exc_info.value)

    def test_missing_identifier(self):
        """Test login missing identifier field"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(password="ValidPass123!")
        assert "field required" in str(exc_info.value)

    def test_missing_password(self):
        """Test login missing password field"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(identifier="john_doe")
        assert "field required" in str(exc_info.value)


class TestUser:
    """Test User model"""

    def test_valid_user(self):
        """Test valid user model"""
        from datetime import datetime

        now = datetime.utcnow()
        user = User(
            username="john_doe",
            email="test@example.com",
            name="Test User",
            phone="+1234567890",
            created_at=now,
            updated_at=now
        )
        assert user.username == "john_doe"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.phone == "+1234567890"
        assert user.created_at == now
        assert user.updated_at == now

    def test_optional_phone(self):
        """Test user with no phone"""
        from datetime import datetime

        now = datetime.utcnow()
        user = User(
            username="john_doe",
            email="test@example.com",
            name="Test User",
            created_at=now,
            updated_at=now
        )
        assert user.phone is None


class TestUserResponse:
    """Test UserResponse model"""

    def test_valid_response(self):
        """Test valid user response"""
        from datetime import datetime

        now = datetime.utcnow()
        response = UserResponse(
            username="john_doe",
            email="test@example.com",
            name="Test User",
            phone="+1234567890",
            created_at=now,
            updated_at=now
        )
        assert response.username == "john_doe"
        assert response.email == "test@example.com"
        assert response.name == "Test User"

    def test_optional_phone_in_response(self):
        """Test user response with no phone"""
        from datetime import datetime

        now = datetime.utcnow()
        response = UserResponse(
            username="john_doe",
            email="test@example.com",
            name="Test User",
            created_at=now,
            updated_at=now
        )
        assert response.phone is None