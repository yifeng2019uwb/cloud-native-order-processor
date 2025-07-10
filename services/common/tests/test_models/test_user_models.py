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
        """Test valid username formats"""
        valid_usernames = [
            "john_doe",      # With underscore (6+ chars)
            "user123",       # With numbers (6+ chars)
            "test_user_123", # Multiple underscores and numbers
            "johnsmith"      # Mixed case (6+ chars)
            # REMOVED: "john", "a" - too short now (< 6 chars)
        ]

        for username in valid_usernames:
            user = UserCreate(
                username=username,
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",     # FIXED: Split field
                last_name="User"       # FIXED: Split field
            )
            # Username should be converted to lowercase
            assert user.username == username.lower()

    def test_username_too_short(self):
        """Test username length validation - too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="abc12",  # FIXED: 5 chars (still too short for 6+ requirement)
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",     # FIXED: Split field
                last_name="User"       # FIXED: Split field
            )
        assert "Username must be 6-30 characters long" in str(exc_info.value)  # FIXED: 6-30

    def test_username_too_long(self):
        """Test username length validation - too long"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="a" * 31,  # 31 chars
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",     # FIXED: Split field
                last_name="User"       # FIXED: Split field
            )
        assert "Username must be 6-30 characters long" in str(exc_info.value)  # FIXED: 6-30

    def test_username_invalid_format(self):
        """Test username format validation"""
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
            with pytest.raises(ValidationError) as exc_info:
                UserCreate(
                    username=username,
                    email="test@example.com",
                    password="ValidPass123!",
                    first_name="Test",     # FIXED: Split field
                    last_name="User"       # FIXED: Split field
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
                first_name="Test",     # FIXED: Split field
                last_name="User"       # FIXED: Split field
            )
        assert "Username cannot be empty" in str(exc_info.value)

    def test_username_whitespace_only(self):
        """Test username cannot be whitespace only"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="   ",
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",     # FIXED: Split field
                last_name="User"       # FIXED: Split field
            )
        assert "Username cannot be empty" in str(exc_info.value)

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
        min_password = "ValidPass1!"  # Exactly 12 chars
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
        """Test password length validation - too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe123",
                email="test@example.com",
                password="Short1!",  # Only 7 chars
                first_name="Test",   # FIXED: Split field
                last_name="User"     # FIXED: Split field
            )
        assert "Password must be 12-20 characters long" in str(exc_info.value)

    def test_password_too_long(self):
        """Test password length validation - too long"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe123",
                email="test@example.com",
                password="ThisPasswordIsTooLong123!",  # 25 chars
                first_name="Test",   # FIXED: Split field
                last_name="User"     # FIXED: Split field
            )
        assert "Password must be 12-20 characters long" in str(exc_info.value)

    def test_password_no_uppercase(self):
        """Test password requires uppercase"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe123",
                email="test@example.com",
                password="validpass123!",  # No uppercase
                first_name="Test",   # FIXED: Split field
                last_name="User"     # FIXED: Split field
            )
        assert "Password must contain at least one uppercase letter" in str(exc_info.value)

    def test_password_no_lowercase(self):
        """Test password requires lowercase"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe123",
                email="test@example.com",
                password="VALIDPASS123!",  # No lowercase
                first_name="Test",   # FIXED: Split field
                last_name="User"     # FIXED: Split field
            )
        assert "Password must contain at least one lowercase letter" in str(exc_info.value)

    def test_password_no_number(self):
        """Test password requires number"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe123",
                email="test@example.com",
                password="ValidPassword!",  # No number
                first_name="Test",   # FIXED: Split field
                last_name="User"     # FIXED: Split field
            )
        assert "Password must contain at least one number" in str(exc_info.value)

    def test_password_no_special_char(self):
        """Test password requires special character"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe123",
                email="test@example.com",
                password="ValidPass123",  # No special char
                first_name="Test",   # FIXED: Split field
                last_name="User"     # FIXED: Split field
            )
        assert "Password must contain at least one special character" in str(exc_info.value)

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
        """Test first name cannot be empty"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe123",
                email="test@example.com",
                password="ValidPass123!",
                first_name="   ",    # FIXED: Only whitespace
                last_name="User"
            )
        assert "First name cannot be empty" in str(exc_info.value)

    def test_empty_last_name(self):
        """Test last name cannot be empty"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe123",
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",
                last_name="   "      # FIXED: Only whitespace
            )
        assert "Last name cannot be empty" in str(exc_info.value)

    def test_invalid_phone_too_short(self):
        """Test phone validation - too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe123",
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",   # FIXED: Split field
                last_name="User",    # FIXED: Split field
                phone="123"  # Too short
            )
        assert "Phone number must be 10-15 digits" in str(exc_info.value)

    def test_invalid_phone_too_long(self):
        """Test phone validation - too long"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe123",
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",   # FIXED: Split field
                last_name="User",    # FIXED: Split field
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
                username="john_doe123",
                email="test@example.com",
                password="ValidPass123!",
                first_name="Test",   # FIXED: Split field
                last_name="User",    # FIXED: Split field
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

    def test_valid_login_with_email(self):
        """Test valid login with email"""
        login = UserLogin(
            username="test@example.com",  # Email in username field
            password="ValidPass123!"
        )
        assert login.username == "test@example.com"
        assert login.password == "ValidPass123!"

    def test_username_whitespace_stripping(self):
        """Test username whitespace stripping in login"""
        login = UserLogin(
            username="  john_doe123  ",
            password="ValidPass123!"
        )
        assert login.username == "john_doe123"

    def test_empty_username(self):
        """Test login with empty username"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(
                username="",
                password="ValidPass123!"
            )
        assert "Username or email cannot be empty" in str(exc_info.value)

    def test_whitespace_username(self):
        """Test login with whitespace username"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(
                username="   ",
                password="ValidPass123!"
            )
        assert "Username or email cannot be empty" in str(exc_info.value)

    def test_missing_username(self):
        """Test login missing username field"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(password="ValidPass123!")
        assert "field required" in str(exc_info.value)

    def test_missing_password(self):
        """Test login missing password field"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(username="john_doe123")
        assert "field required" in str(exc_info.value)


class TestUser:
    """Test User model"""

    def test_valid_user(self):
        """Test valid user model"""
        from datetime import datetime

        now = datetime.utcnow()
        user = User(
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
        assert user.first_name == "Test"    # FIXED: Split field
        assert user.last_name == "User"     # FIXED: Split field
        assert user.phone == "+1234567890"
        assert user.created_at == now
        assert user.updated_at == now

    def test_computed_name_property(self):
        """Test computed name property for backward compatibility"""
        from datetime import datetime

        now = datetime.utcnow()
        user = User(
            username="john_doe123",
            email="test@example.com",
            first_name="John",       # FIXED: Split field
            last_name="Doe",         # FIXED: Split field
            phone="+1234567890",
            created_at=now,
            updated_at=now
        )
        assert user.name == "John Doe"      # ADDED: Test computed property

    def test_optional_phone(self):
        """Test user with no phone"""
        from datetime import datetime

        now = datetime.utcnow()
        user = User(
            username="john_doe123",
            email="test@example.com",
            first_name="Test",       # FIXED: Split field
            last_name="User",        # FIXED: Split field
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

    def test_computed_name_property_response(self):
        """Test computed name property in response"""
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
        assert response.name == "Jane Smith"

    def test_computed_name_property_response_edge_cases(self):
        """Test computed name property edge cases in response"""
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
        assert response.name == "A B"

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
        assert response.name == "Complete User"

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