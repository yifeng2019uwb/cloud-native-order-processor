"""
Tests for user service validation
"""
import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock

from validation.field_validators import (
    validate_username,
    validate_name,
    validate_email,
    validate_phone,
    validate_password,
    validate_date_of_birth
)
from validation.business_validators import (
    validate_username_uniqueness,
    validate_email_uniqueness,
    validate_user_exists,
    validate_age_requirements
)
from common.exceptions.shared_exceptions import UserValidationException, UserNotFoundException
from user_exceptions import UserAlreadyExistsException


class TestFieldValidators:
    """Test field validation functions"""

    class TestUsernameValidation:
        """Test username validation"""

        def test_valid_usernames(self):
            """Test valid username formats"""
            valid_usernames = [
                "john_doe123",
                "user123",
                "test_user",
                "admin_2024",
                "john123doe"
            ]

            for username in valid_usernames:
                result = validate_username(username)
                assert result == username.lower()

        def test_empty_username(self):
            """Test empty username"""
            with pytest.raises(UserValidationException, match="Username cannot be empty"):
                validate_username("")

        def test_whitespace_only_username(self):
            """Test whitespace-only username"""
            with pytest.raises(UserValidationException, match="Username cannot be empty"):
                validate_username("   ")

        def test_invalid_characters(self):
            """Test usernames with invalid characters"""
            invalid_usernames = [
                "john-doe",      # Contains hyphen
                "user@name",     # Contains special char
                "user name",     # Contains space
                "user#name",     # Contains special char
                "user.name",     # Contains dot
            ]

            for username in invalid_usernames:
                with pytest.raises(UserValidationException, match="Username must be 6-30 alphanumeric characters and underscores only"):
                    validate_username(username)

        def test_too_short_username(self):
            """Test username that's too short"""
            with pytest.raises(UserValidationException, match="Username must be 6-30 alphanumeric characters and underscores only"):
                validate_username("abc")

        def test_too_long_username(self):
            """Test username that's too long"""
            with pytest.raises(UserValidationException, match="Username must be 6-30 alphanumeric characters and underscores only"):
                validate_username("a" * 31)

        def test_suspicious_content(self):
            """Test usernames with suspicious content"""
            suspicious_usernames = [
                "<script>alert('xss')</script>user",
                "javascript:alert('xss')",
                "data:text/html,<script>alert('xss')</script>",
            ]

            for username in suspicious_usernames:
                with pytest.raises(UserValidationException, match="Username contains potentially malicious content"):
                    validate_username(username)

        def test_case_conversion(self):
            """Test that usernames are converted to lowercase"""
            assert validate_username("JohnDoe123") == "johndoe123"
            assert validate_username("USER_NAME") == "user_name"

    class TestNameValidation:
        """Test name validation (first_name, last_name)"""

        def test_valid_names(self):
            """Test valid name formats"""
            valid_names = [
                "John",
                "Mary",
                "Jean-Pierre",
                "O'Connor",
                "Van der Berg",
                "McDonald"
            ]

            for name in valid_names:
                result = validate_name(name)
                assert result == name.title()

        def test_empty_name(self):
            """Test empty name"""
            with pytest.raises(UserValidationException, match="Name cannot be empty"):
                validate_name("")

        def test_invalid_characters(self):
            """Test names with invalid characters"""
            invalid_names = [
                "John123",       # Contains numbers
                "Mary@",         # Contains special char
                "Jean#Pierre",   # Contains special char
                "O'Connor!",     # Contains special char
            ]

            for name in invalid_names:
                with pytest.raises(UserValidationException, match="Name must contain only letters, spaces, apostrophes, and hyphens"):
                    validate_name(name)

        def test_valid_names_with_hyphens(self):
            """Test names with hyphens and apostrophes"""
            valid_names = [
                "Jean-Pierre",
                "O'Connor",
                "Mary-Jane"
            ]

            for name in valid_names:
                result = validate_name(name)
                assert result == name.title()

        def test_suspicious_content(self):
            """Test names with suspicious content"""
            suspicious_names = [
                "<script>alert('xss')</script>John",
                "javascript:alert('xss')",
                "data:text/html,<script>alert('xss')</script>",
            ]

            for name in suspicious_names:
                with pytest.raises(UserValidationException, match="Name contains potentially malicious content"):
                    validate_name(name)

        def test_case_conversion(self):
            """Test that names are converted to title case"""
            assert validate_name("john doe") == "John Doe"
            assert validate_name("MARY JANE") == "Mary Jane"

    class TestEmailValidation:
        """Test email validation"""

        def test_valid_emails(self):
            """Test valid email formats"""
            valid_emails = [
                "user@example.com",
                "user.name@example.com",
                "user+tag@example.com",
                "user@subdomain.example.com",
                "user@example.co.uk"
            ]

            for email in valid_emails:
                result = validate_email(email)
                assert result == email.lower()

        def test_empty_email(self):
            """Test empty email"""
            with pytest.raises(UserValidationException, match="Email cannot be empty"):
                validate_email("")

        def test_invalid_email_format(self):
            """Test invalid email formats"""
            invalid_emails = [
                "user@",           # Missing domain
                "@example.com",    # Missing username
                "user.example.com", # Missing @
                "user@.com",       # Missing domain
                "user@example",    # Missing TLD
            ]

            for email in invalid_emails:
                with pytest.raises(UserValidationException, match="Invalid email format"):
                    validate_email(email)

        def test_suspicious_content(self):
            """Test emails with suspicious content"""
            suspicious_emails = [
                "<script>alert('xss')</script>user@example.com",
                "javascript:alert('xss')@example.com",
                "data:text/html,<script>alert('xss')</script>@example.com",
            ]

            for email in suspicious_emails:
                with pytest.raises(UserValidationException, match="Email contains potentially malicious content"):
                    validate_email(email)

        def test_case_conversion(self):
            """Test that emails are converted to lowercase"""
            assert validate_email("User@Example.COM") == "user@example.com"
            assert validate_email("USER@EXAMPLE.COM") == "user@example.com"

    class TestPhoneValidation:
        """Test phone validation"""

        def test_valid_phones(self):
            """Test valid phone formats"""
            valid_phones = [
                "1234567890",      # 10 digits
                "123456789012345", # 15 digits
                "+1-555-123-4567", # With formatting
                "(555) 123-4567",  # With formatting
                "555.123.4567",    # With formatting
            ]

            for phone in valid_phones:
                result = validate_phone(phone)
                # Should return digits only
                assert result.isdigit()
                assert 10 <= len(result) <= 15

        def test_empty_phone(self):
            """Test empty phone (should return empty string)"""
            result = validate_phone("")
            assert result == ""

        def test_invalid_phone_too_short(self):
            """Test phone with too few digits"""
            with pytest.raises(UserValidationException, match="Phone number must contain 10-15 digits"):
                validate_phone("123456789")  # 9 digits

        def test_invalid_phone_too_long(self):
            """Test phone with too many digits"""
            with pytest.raises(UserValidationException, match="Phone number must contain 10-15 digits"):
                validate_phone("1234567890123456")  # 16 digits

        def test_suspicious_content(self):
            """Test phones with suspicious content"""
            suspicious_phones = [
                "<script>alert('xss')</script>1234567890",
                "javascript:alert('xss')1234567890",
                "data:text/html,<script>alert('xss')</script>1234567890",
            ]

            for phone in suspicious_phones:
                with pytest.raises(UserValidationException, match="Phone contains potentially malicious content"):
                    validate_phone(phone)

    class TestPasswordValidation:
        """Test password validation"""

        def test_valid_passwords(self):
            """Test valid password formats"""
            valid_passwords = [
                "SecurePass123!",
                "MyPassword456@",
                "ComplexPwd789#",
                "StrongPass2024$",
            ]

            for password in valid_passwords:
                result = validate_password(password)
                assert result == password

        def test_empty_password(self):
            """Test empty password"""
            with pytest.raises(UserValidationException, match="Password cannot be empty"):
                validate_password("")

        def test_password_too_short(self):
            """Test password that's too short"""
            with pytest.raises(UserValidationException, match="Password must be at least 12 characters long"):
                validate_password("Short123!")

        def test_password_too_long(self):
            """Test password that's too long"""
            with pytest.raises(UserValidationException, match="Password must be no more than 20 characters long"):
                validate_password("VeryLongPassword123!Extra")

        def test_password_no_uppercase(self):
            """Test password without uppercase"""
            with pytest.raises(UserValidationException, match="Password must contain at least one uppercase letter"):
                validate_password("lowercase123!")

        def test_password_no_lowercase(self):
            """Test password without lowercase"""
            with pytest.raises(UserValidationException, match="Password must contain at least one lowercase letter"):
                validate_password("UPPERCASE123!")

        def test_password_no_number(self):
            """Test password without number"""
            with pytest.raises(UserValidationException, match="Password must contain at least one number"):
                validate_password("NoNumbers!ExtraLong")

        def test_password_no_special_char(self):
            """Test password without special character"""
            with pytest.raises(UserValidationException, match="Password must contain at least one special character"):
                validate_password("NoSpecialChar123")

        def test_suspicious_content(self):
            """Test passwords with suspicious content"""
            suspicious_passwords = [
                "<script>alert('xss')</script>Pass123!",
                "javascript:alert('xss')Pass123!",
                "data:text/html,<script>alert('xss')</script>Pass123!",
            ]

            for password in suspicious_passwords:
                with pytest.raises(UserValidationException, match="Password contains potentially malicious content"):
                    validate_password(password)

    class TestDateOfBirthValidation:
        """Test date of birth validation"""

        def test_valid_dates(self):
            """Test valid dates of birth"""
            today = date.today()
            valid_dates = [
                today - timedelta(days=18 * 365),  # 18 years old
                today - timedelta(days=25 * 365),  # 25 years old
                today - timedelta(days=50 * 365),  # 50 years old
                today - timedelta(days=80 * 365),  # 80 years old
            ]

            for dob in valid_dates:
                result = validate_date_of_birth(dob)
                assert result == dob

        def test_none_date(self):
            """Test None date (should return None)"""
            result = validate_date_of_birth(None)
            assert result is None

        def test_too_young(self):
            """Test date that makes user too young"""
            today = date.today()
            too_young = today - timedelta(days=12 * 365)  # 12 years old

            with pytest.raises(UserValidationException, match="User must be at least 13 years old"):
                validate_date_of_birth(too_young)

        def test_too_old(self):
            """Test date that makes user too old"""
            today = date.today()
            too_old = today - timedelta(days=125 * 365)  # 125 years old

            with pytest.raises(UserValidationException, match="Invalid date of birth"):
                validate_date_of_birth(too_old)


class TestBusinessValidators:
    """Test business validation functions"""

    def test_validate_username_uniqueness_unique(self):
        """Test username uniqueness when username is unique"""
        mock_dao = Mock()
        mock_dao.get_user_by_username.return_value = None

        result = validate_username_uniqueness("newuser", mock_dao)
        assert result is True
        mock_dao.get_user_by_username.assert_called_once_with("newuser")

    def test_validate_username_uniqueness_exists(self):
        """Test username uniqueness when username already exists"""
        mock_dao = Mock()
        mock_user = MagicMock()
        mock_user.username = "user123"
        mock_dao.get_user_by_username.return_value = mock_user

        with pytest.raises(UserAlreadyExistsException, match="Username 'existinguser' already exists"):
            validate_username_uniqueness("existinguser", mock_dao)

    # Removed test_validate_username_uniqueness_exclude_current as we simplified the logic
    # to just raise UserAlreadyExistsException if user exists, without exclude_user_id handling

    def test_validate_email_uniqueness_unique(self):
        """Test email uniqueness when email is unique"""
        mock_dao = Mock()
        mock_dao.get_user_by_email.return_value = None

        result = validate_email_uniqueness("new@example.com", mock_dao)
        assert result is True
        mock_dao.get_user_by_email.assert_called_once_with("new@example.com")

    def test_validate_email_uniqueness_exists(self):
        """Test email uniqueness when email already exists"""
        mock_dao = Mock()
        mock_user = MagicMock()
        mock_user.username = "user123"
        mock_dao.get_user_by_email.return_value = mock_user

        with pytest.raises(UserAlreadyExistsException, match="Email 'existing@example.com' already exists"):
            validate_email_uniqueness("existing@example.com", mock_dao)

    def test_validate_user_exists_found(self):
        """Test user existence when user exists"""
        mock_dao = Mock()
        mock_user = MagicMock()
        mock_dao.get_user_by_username.return_value = mock_user

        result = validate_user_exists("user123", mock_dao)
        assert result is True
        mock_dao.get_user_by_username.assert_called_once_with("user123")

    def test_validate_user_exists_not_found(self):
        """Test user existence when user doesn't exist"""
        mock_dao = Mock()
        mock_dao.get_user_by_username.return_value = None

        with pytest.raises(UserNotFoundException, match="User with ID 'nonexistent' not found"):
            validate_user_exists("nonexistent", mock_dao)

    def test_validate_age_requirements_valid(self):
        """Test age requirements with valid age"""
        today = date.today()
        valid_dob = today - timedelta(days=25 * 365)  # 25 years old

        result = validate_age_requirements(valid_dob)
        assert result is True

    def test_validate_age_requirements_none(self):
        """Test age requirements with None date"""
        result = validate_age_requirements(None)
        assert result is True

    def test_validate_age_requirements_too_young(self):
        """Test age requirements with too young user"""
        today = date.today()
        too_young = today - timedelta(days=12 * 365)  # 12 years old

        with pytest.raises(UserValidationException, match="User must be at least 13 years old"):
            validate_age_requirements(too_young)

    def test_validate_age_requirements_too_old(self):
        """Test age requirements with too old user"""
        today = date.today()
        too_old = today - timedelta(days=125 * 365)  # 125 years old

        with pytest.raises(UserValidationException, match="Invalid date of birth"):
            validate_age_requirements(too_old)