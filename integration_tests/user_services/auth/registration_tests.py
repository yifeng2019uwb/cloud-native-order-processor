"""
User Registration API Integration Tests
Tests POST /auth/register endpoint with comprehensive validation
"""
import requests
import time
import sys
import os
import uuid
import json

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from api_endpoints import APIEndpoints, UserAPI
from test_constants import UserFields

class UserRegistrationTests:
    """Integration tests for user registration API with comprehensive validation"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()

    def user_api(self, api: UserAPI) -> str:
        """Helper method to get complete user service API URLs"""
        return APIEndpoints.get_user_endpoint(api)

    def test_registration_success(self):
        """Test successful user registration with all fields"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Integration',
            UserFields.LAST_NAME: 'Test',
            UserFields.PHONE: '1234567890',
            UserFields.DATE_OF_BIRTH: '1990-01-01',
            UserFields.MARKETING_EMAILS_CONSENT: True
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code == 201
        data = response.json()
        assert UserFields.MESSAGE in data
        assert data[UserFields.MESSAGE] == "User registered successfully"
        return test_user

    def test_registration_minimal_success(self):
        """Test successful user registration with only required fields"""
        test_user = {
            UserFields.USERNAME: f'minuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'min_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'MinPassword123!',
            UserFields.FIRST_NAME: 'Minimal',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code == 201
        data = response.json()
        assert UserFields.MESSAGE in data
        assert data[UserFields.MESSAGE] == "User registered successfully"

    def test_registration_duplicate_username(self):
        """Test registration with duplicate username (should fail)"""
        # First, create a user
        test_user = self.test_registration_success()

        # Try to register again with same username
        duplicate_user = test_user.copy()
        duplicate_user[UserFields.EMAIL] = f'duplicate_{uuid.uuid4().hex[:8]}@example.com'

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=duplicate_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 409], f"Expected 400/409, got {response.status_code}: {response.text}"

    def test_registration_duplicate_email(self):
        """Test registration with duplicate email (should fail)"""
        # First, create a user
        test_user = self.test_registration_success()

        # Try to register again with same email
        duplicate_user = test_user.copy()
        duplicate_username = f'duplicate_{uuid.uuid4().hex[:8]}'

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=duplicate_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 409], f"Expected 400/409, got {response.status_code}: {response.text}"

    # Username Validation Tests
    def test_registration_username_too_short(self):
        """Test registration with username too short (< 6 chars)"""
        test_user = {
            UserFields.USERNAME: 'abc',  # Too short
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}: {response.text}"

    def test_registration_username_too_long(self):
        """Test registration with username too long (> 30 chars)"""
        test_user = {
            UserFields.USERNAME: 'a' * 31,  # Too long
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}: {response.text}"

    def test_registration_username_invalid_chars(self):
        """Test registration with username containing invalid characters"""
        test_user = {
            UserFields.USERNAME: 'test-user@123',  # Contains hyphens and @
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}: {response.text}"

    def test_registration_username_suspicious_content(self):
        """Test registration with username containing suspicious content"""
        test_user = {
            UserFields.USERNAME: '<script>alert("xss")</script>',  # XSS attempt
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}: {response.text}"

    # Email Validation Tests
    def test_registration_email_invalid_format(self):
        """Test registration with invalid email format"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: 'invalid-email',  # Invalid format
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}: {response.text}"

    def test_registration_email_suspicious_content(self):
        """Test registration with email containing suspicious content"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: '<script>alert("xss")</script>@example.com',  # XSS attempt
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}: {response.text}"

    # Password Validation Tests
    def test_registration_password_too_short(self):
        """Test registration with password too short (< 12 chars)"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'Short1!',  # Too short
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_registration_password_too_long(self):
        """Test registration with password too long (> 20 chars)"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'VeryLongPassword123!Extra',  # 25 chars - too long
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_registration_password_no_uppercase(self):
        """Test registration with password missing uppercase letter"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'lowercase123!',  # No uppercase
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_registration_password_no_lowercase(self):
        """Test registration with password missing lowercase letter"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'UPPERCASE123!',  # No lowercase
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_registration_password_no_number(self):
        """Test registration with password missing number"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'PasswordOnly!',  # No number
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_registration_password_no_special_char(self):
        """Test registration with password missing special character"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'Password123',  # No special char
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # Name Validation Tests
    def test_registration_name_invalid_chars(self):
        """Test registration with name containing invalid characters"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test123',  # Contains numbers
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_registration_name_suspicious_content(self):
        """Test registration with name containing suspicious content"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: '<script>alert("xss")</script>',  # XSS attempt
            UserFields.LAST_NAME: 'User'
        }


        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}: {response.text}"

    # Phone Validation Tests
    def test_registration_phone_invalid_format(self):
        """Test registration with invalid phone format"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User',
            UserFields.PHONE: '123'  # Too short
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_registration_phone_too_long(self):
        """Test registration with phone too long"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User',
            UserFields.PHONE: '1' * 20  # Too long
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # Date of Birth Validation Tests
    def test_registration_dob_too_young(self):
        """Test registration with date of birth making user too young (< 13)"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User',
            UserFields.DATE_OF_BIRTH: '2020-01-01'  # Too young
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_registration_dob_future_date(self):
        """Test registration with future date of birth"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User',
            UserFields.DATE_OF_BIRTH: '2030-01-01'  # Future date
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # Missing Required Fields Tests
    def test_registration_missing_username(self):
        """Test registration with missing username"""
        test_user = {
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_registration_missing_email(self):
        """Test registration with missing email"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_registration_missing_password(self):
        """Test registration with missing password"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.FIRST_NAME: 'Test',
            UserFields.LAST_NAME: 'User'
        }


        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_registration_missing_first_name(self):
        """Test registration with missing first name"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.LAST_NAME: 'User'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_registration_missing_last_name(self):
        """Test registration with missing last name"""
        test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Test'
        }

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def run_all_registration_tests(self):
        """Run all user registration tests"""
        self.test_registration_success()
        self.test_registration_minimal_success()
        self.test_registration_duplicate_username()
        self.test_registration_duplicate_email()
        self.test_registration_username_too_short()
        self.test_registration_username_too_long()
        self.test_registration_username_invalid_chars()
        self.test_registration_username_suspicious_content()
        self.test_registration_email_invalid_format()
        self.test_registration_email_suspicious_content()
        self.test_registration_password_too_short()
        self.test_registration_password_too_long()
        self.test_registration_password_no_uppercase()
        self.test_registration_password_no_lowercase()
        self.test_registration_password_no_number()
        self.test_registration_password_no_special_char()
        self.test_registration_name_invalid_chars()
        self.test_registration_name_suspicious_content()
        self.test_registration_phone_invalid_format()
        self.test_registration_phone_too_long()
        self.test_registration_dob_too_young()
        self.test_registration_dob_future_date()
        self.test_registration_missing_username()
        self.test_registration_missing_email()
        self.test_registration_missing_password()
        self.test_registration_missing_first_name()
        self.test_registration_missing_last_name()

if __name__ == "__main__":
    tests = UserRegistrationTests()
    tests.run_all_registration_tests()
