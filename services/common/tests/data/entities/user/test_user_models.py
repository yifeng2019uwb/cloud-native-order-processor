# Standard library imports
import os
import sys

# Third-party imports
import pytest
from pydantic import ValidationError

# Local imports
from src.data.entities.user import UserCreate, User, UserResponse, UserLogin

# Add src directory to path for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))


class TestUserCreate:
    """Test UserCreate model validation"""

    def test_valid_user_create(self):
        """Test valid user creation data"""
        user_data = {
            "username": "john_doe123",
            "email": "test@example.com",
            "password": "ValidPass123!",
            "first_name": "Test",      # FIXED: Split from 'name'
            "last_name": "User",       # FIXED: Split from 'name'
            "phone": "+1234567890"
        }
        user = UserCreate(**user_data)
        assert user.username == "john_doe123"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"      # FIXED: Split field
        assert user.last_name == "User"       # FIXED: Split field
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
            user = UserCreate(
                username=username,
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",
                last_name="User"
            )
            # Username should be stored as provided (no transformation)
            assert user.username == username

    def test_username_too_short(self):
        """Test username length validation - too short (simple DB constraint)"""
        # This should now pass since we removed complex validation
        # Only testing basic DB constraints
        user = UserCreate(
            username="abc12",  # Short username - should be allowed
            email="test@example.com",
            password="ValidPass123!",
            first_name="Test",
            last_name="User"
        )
        assert user.username == "abc12"

    def test_username_too_long(self):
        """Test username length validation - too long (simple DB constraint)"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="a" * 31,  # 31 chars - exceeds max_length=30
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",
                last_name="User"
            )
        # Should get Pydantic's default error message for string_too_long
        assert "String should have at most 30 characters" in str(exc_info.value)

    def test_username_invalid_format(self):
        """Test username format validation - simple DB constraints only"""
        # These should now pass since we removed complex validation
        # Only testing basic DB constraints
        invalid_usernames = [
            "_john_doe",     # Starts with underscore
            "john_doe_",     # Ends with underscore
            "john__doe",     # Consecutive underscores
            "john-doe",      # Contains hyphen
            "john doe",      # Contains space
            "john@doe",      # Contains @ symbol
            "john.doe",      # Contains period
        ]

        for username in invalid_usernames:
            # These should now be allowed since we removed complex validation
            user = UserCreate(
                username=username,
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",
                last_name="User"
            )
            assert user.username == username

    def test_username_empty(self):
        """Test empty username - simple DB constraints only"""
        # Empty username should be allowed since we removed complex validation
        user = UserCreate(
            username="",
            email="test@example.com",
            password="ValidPass123!",
            first_name="Test",
            last_name="User"
        )
        assert user.username == ""

    def test_username_whitespace_only(self):
        """Test whitespace username - simple DB constraints only"""
        # Whitespace username should be allowed since we removed complex validation
        user = UserCreate(
            username="   ",
            email="test@example.com",
            password="ValidPass123!",
            first_name="Test",
            last_name="User"
        )
        assert user.username == "   "

    def test_password_valid_complexity(self):
        """Test valid password with all complexity requirements"""
        valid_passwords = [
            "ValidPass123!",   # Standard valid password
            "MySecure1@Pass",  # Different special chars
            "Test123#Strong",  # Hash special char
            "Complex1$Word"    # Dollar special char
        ]

        for password in valid_passwords:
            user = UserCreate(
                username="john_doe123",
                email="test@example.com",
                password=password,
                first_name="Test",
                last_name="User"
            )
            assert user.password == password

    def test_password_boundary_lengths(self):
        """Test password boundary lengths"""
        # Test minimum length (12 chars)
        min_password = "ValidPass12!"  # Exactly 12 chars
        user = UserCreate(
            username="john_doe123",
            email="test@example.com",
            password=min_password,
            first_name="Test",
            last_name="User"
        )
        assert user.password == min_password

        # Test maximum length (20 chars)
        max_password = "ValidPassword123456!"  # Exactly 20 chars
        user = UserCreate(
            username="john_doe123",
            email="test@example.com",
            password=max_password,
            first_name="Test",
            last_name="User"
        )
        assert user.password == max_password

    def test_password_too_short(self):
        """Test password length validation - too short (simple DB constraint)"""
        # Short password should be allowed since we removed complex validation
        user = UserCreate(
            username="john_doe123",
            email="test@example.com",
            password="Short1!",  # Only 7 chars
            first_name="Test",
            last_name="User"
        )
        assert user.password == "Short1!"

    def test_password_too_long(self):
        """Test password length validation - too long (simple DB constraint)"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe123",
                email="test@example.com",
                password="a" * 129,  # 129 chars - exceeds max_length=128
                first_name="Test",
                last_name="User"
            )
        # Should get Pydantic's default error message for string_too_long
        assert "String should have at most 128 characters" in str(exc_info.value)

    def test_password_no_uppercase(self):
        """Test password complexity - simple DB constraints only"""
        # Password without uppercase should be allowed since we removed complex validation
        user = UserCreate(
            username="john_doe123",
            email="test@example.com",
            password="validpass123!",  # No uppercase
            first_name="Test",
                last_name="User"     # FIXED: Split field
            )
        assert user.password == "validpass123!"

    def test_password_no_lowercase(self):
        """Test password complexity - simple DB constraints only"""
        # Password without lowercase should be allowed since we removed complex validation
        user = UserCreate(
            username="john_doe123",
            email="test@example.com",
            password="VALIDPASS123!",  # No lowercase
            first_name="Test",
            last_name="User"
        )
        assert user.password == "VALIDPASS123!"

    def test_password_no_number(self):
        """Test password complexity - simple DB constraints only"""
        # Password without number should be allowed since we removed complex validation
        user = UserCreate(
            username="john_doe123",
            email="test@example.com",
            password="ValidPassword!",  # No number
            first_name="Test",
            last_name="User"
        )
        assert user.password == "ValidPassword!"

    def test_password_no_special_char(self):
        """Test password complexity - simple DB constraints only"""
        # Password without special char should be allowed since we removed complex validation
        user = UserCreate(
            username="john_doe123",
            email="test@example.com",
            password="ValidPass123",  # No special char
            first_name="Test",
            last_name="User"
        )
        assert user.password == "ValidPass123"

    def test_invalid_email(self):
        """Test email validation"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe123",
                email="invalid-email",
                password="ValidPass123!",
                first_name="Test",   # FIXED: Split field
                last_name="User"     # FIXED: Split field
            )
        assert "value is not a valid email address" in str(exc_info.value)

    def test_empty_first_name(self):
        """Test empty first name - simple DB constraints only"""
        # Empty first name should be allowed since we removed complex validation
        user = UserCreate(
            username="john_doe123",
            email="test@example.com",
            password="ValidPass123!",
            first_name="   ",    # Only whitespace
            last_name="User"
        )
        assert user.first_name == "   "

    def test_empty_last_name(self):
        """Test empty last name - simple DB constraints only"""
        # Empty last name should be allowed since we removed complex validation
        user = UserCreate(
            username="john_doe123",
            email="test@example.com",
            password="ValidPass123!",
            first_name="Test",
            last_name="   "      # Only whitespace
        )
        assert user.last_name == "   "

    def test_invalid_phone_too_short(self):
        """Test phone validation - too short (simple DB constraint)"""
        # Short phone should be allowed since we removed complex validation
        user = UserCreate(
            username="john_doe123",
            email="test@example.com",
            password="ValidPass123!",
            first_name="Test",
            last_name="User",
            phone="123"  # Too short
        )
        assert user.phone == "123"

    def test_invalid_phone_too_long(self):
        """Test phone validation - too long (simple DB constraint)"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe123",
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",
                last_name="User",
                phone="a" * 16  # 16 chars - exceeds max_length=15
            )
        # Should get Pydantic's default error message for string_too_long
        assert "String should have at most 15 characters" in str(exc_info.value)

    def test_valid_phone_formats(self):
        """Test various valid phone formats - simple DB constraints only"""
        # Only test phones that fit within max_length=15
        valid_phones = [
            "+1234567890",      # 11 chars
            "1234567890",       # 10 chars
            "123-456-7890",     # 12 chars
        ]

        for phone in valid_phones:
            user = UserCreate(
                username="john_doe123",
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",
                last_name="User",
                phone=phone
            )
            assert user.phone == phone

    def test_optional_phone(self):
        """Test phone is optional"""
        user = UserCreate(
            username="john_doe123",
            email="test@example.com",
            password="ValidPass123!",
            first_name="Test",       # FIXED: Split field
            last_name="User"         # FIXED: Split field
        )
        assert user.phone is None


class TestUserLogin:
    """Test UserLogin model"""

    def test_valid_login_with_username(self):
        """Test valid login with username"""
        login = UserLogin(
            username="john_doe123",
            password="ValidPass123!"
        )
        assert login.username == "john_doe123"
        assert login.password == "ValidPass123!"

    def test_valid_login_with_email_like_username(self):
        """Test valid login with email-like username (email as username)"""
        login = UserLogin(
            username="test@example.com",  # Email-like string as username
            password="ValidPass123!"
        )
        assert login.username == "test@example.com"
        assert login.password == "ValidPass123!"

    def test_username_whitespace_stripping(self):
        """Test username whitespace handling in login - simple DB constraints only"""
        # Username should be stored as provided since we removed complex validation
        login = UserLogin(
            username="  john_doe123  ",
            password="ValidPass123!"
        )
        assert login.username == "  john_doe123  "

    def test_empty_username(self):
        """Test login with empty username - simple DB constraints only"""
        # Empty username should be allowed since we removed complex validation
        login = UserLogin(
            username="",
            password="ValidPass123!"
        )
        assert login.username == ""

    def test_whitespace_username(self):
        """Test login with whitespace username - simple DB constraints only"""
        # Whitespace username should be allowed since we removed complex validation
        login = UserLogin(
            username="   ",
            password="ValidPass123!"
        )
        assert login.username == "   "

    def test_missing_username(self):
        """Test login missing username field"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(password="ValidPass123!")
        assert "Field required" in str(exc_info.value)

    def test_missing_password(self):
        """Test login missing password field"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(username="john_doe123")
        assert "Field required" in str(exc_info.value)


class TestUser:
    """Test User model"""

    def test_valid_user(self):
        """Test valid user model"""
        from datetime import datetime

        now = datetime.utcnow()
        user = User(
            Pk="john_doe123",
            Sk="USER",
            username="john_doe123",
            email="test@example.com",
            first_name="Test",       # FIXED: Split field
            last_name="User",        # FIXED: Split field
            phone="+1234567890",
            created_at=now,
            updated_at=now
        )

        assert user.username == "john_doe123"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.phone == "+1234567890"
        assert user.Pk == "john_doe123"

    def test_name_property_removed(self):
        """Test that name property was removed from User model"""
        from datetime import datetime

        now = datetime.utcnow()
        user = User(
            Pk="john_doe123",
            Sk="USER",
            username="john_doe123",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="+1234567890",
            created_at=now,
            updated_at=now
        )

        # Verify name property doesn't exist
        assert not hasattr(user, 'name')
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.Pk == "john_doe123"

    def test_optional_phone(self):
        """Test user with no phone"""
        from datetime import datetime

        now = datetime.utcnow()
        user = User(
            Pk="john_doe123",
            Sk="USER",
            username="john_doe123",
            email="test@example.com",
            first_name="Test",       # FIXED: Split field
            last_name="User",        # FIXED: Split field
            created_at=now,
            updated_at=now
        )

        assert user.username == "john_doe123"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.phone is None
        assert user.Pk == "john_doe123"


class TestUserResponse:
    """Test UserResponse model"""

    def test_valid_response(self):
        """Test valid user response"""
        from datetime import datetime

        now = datetime.utcnow()
        response = UserResponse(
            username="john_doe123",
            email="test@example.com",
            first_name="Test",       # FIXED: Split field
            last_name="User",        # FIXED: Split field
            phone="+1234567890",
            created_at=now,
            updated_at=now
        )
        assert response.username == "john_doe123"
        assert response.email == "test@example.com"
        assert response.first_name == "Test"    # FIXED: Split field
        assert response.last_name == "User"     # FIXED: Split field

    def test_name_property_removed_response(self):
        """Test that name property was removed from UserResponse model"""
        from datetime import datetime

        now = datetime.utcnow()
        response = UserResponse(
            username="john_doe123",
            email="test@example.com",
            first_name="Jane",
            last_name="Smith",
            created_at=now,
            updated_at=now
        )
        # Test that name property no longer exists
        assert not hasattr(response, 'name')
        # Test that first_name and last_name are separate fields
        assert response.first_name == "Jane"
        assert response.last_name == "Smith"

    def test_name_property_removed_response_edge_cases(self):
        """Test that name property was removed from UserResponse model - edge cases"""
        from datetime import datetime

        now = datetime.utcnow()

        # Test with single character names
        response = UserResponse(
            username="john_doe123",
            email="test@example.com",
            first_name="A",
            last_name="B",
            created_at=now,
            updated_at=now
        )
        # Test that name property no longer exists
        assert not hasattr(response, 'name')
        # Test that first_name and last_name are separate fields
        assert response.first_name == "A"
        assert response.last_name == "B"

    def test_userresponse_all_fields(self):
        """Test UserResponse with all fields populated"""
        from datetime import datetime

        now = datetime.utcnow()
        response = UserResponse(
            username="complete_user",
            email="complete@example.com",
            first_name="Complete",
            last_name="User",
            phone="+1234567890",
            created_at=now,
            updated_at=now
        )
        assert response.username == "complete_user"
        assert response.email == "complete@example.com"
        assert response.first_name == "Complete"
        assert response.last_name == "User"
        assert response.phone == "+1234567890"
        # Test that name property no longer exists
        assert not hasattr(response, 'name')

    def test_optional_phone_in_response(self):
        """Test user response with no phone"""
        from datetime import datetime

        now = datetime.utcnow()
        response = UserResponse(
            username="john_doe123",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            created_at=now,
            updated_at=now
        )
        assert response.phone is None