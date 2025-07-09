import pytest
from pydantic import ValidationError
from src.models.user import UserCreate, User, UserResponse


class TestUserCreate:
    """Test UserCreate model validation"""

    def test_valid_user_create(self):
        """Test valid user creation data"""
        user_data = {
            "email": "test@example.com",
            "password": "ValidPass123!",
            "name": "Test User",
            "phone": "+1234567890"
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.phone == "+1234567890"

    def test_password_too_short(self):
        """Test password length validation - too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="Short1!",  # Only 7 chars
                name="Test User"
            )
        assert "Password must be 12-20 characters long" in str(exc_info.value)

    def test_password_too_long(self):
        """Test password length validation - too long"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="ThisPasswordIsTooLong123!",  # 25 chars
                name="Test User"
            )
        assert "Password must be 12-20 characters long" in str(exc_info.value)

    def test_password_no_uppercase(self):
        """Test password requires uppercase"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="validpass123!",  # No uppercase
                name="Test User"
            )
        assert "Password must contain at least one uppercase letter" in str(exc_info.value)

    def test_password_no_lowercase(self):
        """Test password requires lowercase"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="VALIDPASS123!",  # No lowercase
                name="Test User"
            )
        assert "Password must contain at least one lowercase letter" in str(exc_info.value)

    def test_password_no_number(self):
        """Test password requires number"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="ValidPassword!",  # No number
                name="Test User"
            )
        assert "Password must contain at least one number" in str(exc_info.value)

    def test_password_no_special_char(self):
        """Test password requires special character"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="ValidPass123",  # No special char
                name="Test User"
            )
        assert "Password must contain at least one special character" in str(exc_info.value)

    def test_invalid_email(self):
        """Test email validation"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="invalid-email",
                password="ValidPass123!",
                name="Test User"
            )
        assert "value is not a valid email address" in str(exc_info.value)

    def test_empty_name(self):
        """Test name cannot be empty"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="ValidPass123!",
                name="   "  # Only whitespace
            )
        assert "Name cannot be empty" in str(exc_info.value)

    def test_invalid_phone_too_short(self):
        """Test phone validation - too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
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
                email="test@example.com",
                password="ValidPass123!",
                name="Test User",
                phone=phone
            )
            assert user.phone == phone

    def test_optional_phone(self):
        """Test phone is optional"""
        user = UserCreate(
            email="test@example.com",
            password="ValidPass123!",
            name="Test User"
        )
        assert user.phone is None


# class TestUserLogin:
#     """Test UserLogin model"""
#
#     def test_valid_login(self):
#         """Test valid login data"""
#         login = UserLogin(
#             email="test@example.com",
#             password="ValidPass123!"
#         )
#         assert login.email == "test@example.com"
#         assert login.password == "ValidPass123!"
#
#     def test_invalid_email(self):
#         """Test login email validation"""
#         with pytest.raises(ValidationError):
#             UserLogin(
#                 email="invalid-email",
#                 password="ValidPass123!"
#             )


class TestUser:
    """Test User model"""

    def test_valid_user(self):
        """Test valid user model"""
        from datetime import datetime

        now = datetime.utcnow()
        user = User(
            email="test@example.com",
            name="Test User",
            phone="+1234567890",
            created_at=now,
            updated_at=now
        )
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
            email="test@example.com",
            name="Test User",
            phone="+1234567890",
            created_at=now,
            updated_at=now
        )
        assert response.email == "test@example.com"
        assert response.name == "Test User"


# class TestTokenResponse:
#     """Test TokenResponse model"""
#
#     def test_valid_token_response(self):
#         """Test valid token response"""
#         token = TokenResponse(access_token="test-token-123")
#         assert token.access_token == "test-token-123"
#         assert token.token_type == "bearer"
#
#     def test_custom_token_type(self):
#         """Test custom token type"""
#         token = TokenResponse(
#             access_token="test-token-123",
#             token_type="custom"
#         )
#         assert token.token_type == "custom"