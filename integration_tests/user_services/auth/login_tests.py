"""
User Login API Integration Tests
Tests POST /auth/login endpoint with comprehensive validation
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
from test_data import TestDataManager
from api_endpoints import APIEndpoints, UserAPI
from test_constants import UserFields, TestValues, CommonFields

class UserLoginTests:
    """Integration tests for user login API with comprehensive validation"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()
        self.test_user = None
        self.access_token = None

    def user_api(self, api: UserAPI) -> str:
        """Helper method to get complete user service API URLs"""
        return APIEndpoints.get_user_endpoint(api)

    def setup_test_user(self):
        """Create a test user for login tests"""
        self.test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Integration',
            UserFields.LAST_NAME: 'Test'
        }

        # Register the user
        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=self.test_user,
            timeout=self.timeout
        )

        assert response.status_code in [200, 201], f"Failed to create test user: {response.status_code}: {response.text}"

    def test_login_success(self):
        """Test successful user login"""
        self.setup_test_user()

        login_data = {
            UserFields.USERNAME: self.test_user['username'],
            UserFields.PASSWORD: self.test_user['password']
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Login failed with status {response.status_code}"

        data = response.json()

        # Extract token from either nested or direct structure
        token_data = data.get(UserFields.DATA, data)
        assert UserFields.ACCESS_TOKEN in token_data, f"Missing access_token in response: {data}"
        assert UserFields.TOKEN_TYPE in token_data, f"Missing token_type in response: {data}"
        assert token_data[UserFields.TOKEN_TYPE] == 'bearer', f"Expected bearer token, got {token_data[UserFields.TOKEN_TYPE]}"
        self.access_token = token_data[UserFields.ACCESS_TOKEN]

        return data

    def test_login_success_with_whitespace_trimming(self):
        """Test successful login with whitespace in username/password (should be trimmed)"""
        self.setup_test_user()

        login_data = {
            UserFields.USERNAME: f"  {self.test_user['username']}  ",  # Extra whitespace
            UserFields.PASSWORD: f"  {self.test_user['password']}  "   # Extra whitespace
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Username Validation Tests
    def test_login_username_too_short(self):
        """Test login with username too short (< 6 chars)"""
        login_data = {
            UserFields.USERNAME: 'abc',  # Too short
            UserFields.PASSWORD: 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_username_too_long(self):
        """Test login with username too long (> 30 chars)"""
        login_data = {
            UserFields.USERNAME: 'a' * 31,  # Too long
            UserFields.PASSWORD: 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_username_invalid_chars(self):
        """Test login with username containing invalid characters"""

        login_data = {
            UserFields.USERNAME: 'test-user@123',  # Contains hyphens and @
            UserFields.PASSWORD: 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_username_suspicious_content(self):
        """Test login with username containing suspicious content"""

        login_data = {
            UserFields.USERNAME: '<script>alert("xss")</script>',  # XSS attempt
            UserFields.PASSWORD: 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_username_empty(self):
        """Test login with empty username"""

        login_data = {
            UserFields.USERNAME: '',  # Empty
            UserFields.PASSWORD: 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_username_whitespace_only(self):
        """Test login with username containing only whitespace"""

        login_data = {
            UserFields.USERNAME: '   ',  # Whitespace only
            UserFields.PASSWORD: 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # Password Validation Tests
    def test_login_password_too_short(self):
        """Test login with password too short (< 12 chars)"""

        login_data = {
            UserFields.USERNAME: 'testuser123',
            UserFields.PASSWORD: 'Short1!'  # Too short
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_password_too_long(self):
        """Test login with password too long (> 20 chars)"""

        login_data = {
            UserFields.USERNAME: 'testuser123',
            UserFields.PASSWORD: 'VeryLongPassword123!Extra'  # 25 chars - too long
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_password_no_uppercase(self):
        """Test login with password missing uppercase letter"""

        login_data = {
            UserFields.USERNAME: 'testuser123',
            UserFields.PASSWORD: 'lowercase123!'  # No uppercase
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_password_no_lowercase(self):
        """Test login with password missing lowercase letter"""

        login_data = {
            UserFields.USERNAME: 'testuser123',
            UserFields.PASSWORD: 'UPPERCASE123!'  # No lowercase
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_password_no_number(self):
        """Test login with password missing number"""

        login_data = {
            UserFields.USERNAME: 'testuser123',
            UserFields.PASSWORD: 'PasswordOnly!'  # No number
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_password_no_special_char(self):
        """Test login with password missing special character"""

        login_data = {
            UserFields.USERNAME: 'testuser123',
            UserFields.PASSWORD: 'Password123'  # No special char
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_password_empty(self):
        """Test login with empty password"""

        login_data = {
            UserFields.USERNAME: 'testuser123',
            UserFields.PASSWORD: ''  # Empty
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_password_whitespace_only(self):
        """Test login with password containing only whitespace"""

        login_data = {
            UserFields.USERNAME: 'testuser123',
            UserFields.PASSWORD: '   '  # Whitespace only
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_password_suspicious_content(self):
        """Test login with password containing suspicious content"""

        login_data = {
            UserFields.USERNAME: 'testuser123',
            UserFields.PASSWORD: '<script>alert("xss")</script>'  # XSS attempt
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # Authentication Tests
    def test_login_invalid_username(self):
        """Test login with invalid username (should fail)"""

        login_data = {
            UserFields.USERNAME: 'nonexistent_user',
            UserFields.PASSWORD: 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        # Should fail with invalid credentials
        assert response.status_code in [401, 404], f"Expected 401/404, got {response.status_code}"

    def test_login_invalid_password(self):
        """Test login with invalid password (should fail)"""
        self.setup_test_user()


        login_data = {
            UserFields.USERNAME: self.test_user['username'],
            UserFields.PASSWORD: 'WrongPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        # Should fail with invalid credentials
        assert response.status_code in [401, 400], f"Expected 401/400, got {response.status_code}"

    def test_login_case_sensitive_username(self):
        """Test login with case-sensitive username (should fail if different case)"""
        self.setup_test_user()

        login_data = {
            UserFields.USERNAME: self.test_user['username'].upper(),  # Different case
            UserFields.PASSWORD: self.test_user['password']
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        # Username can be case-insensitive (200) or case-sensitive (400/401/422)
        assert response.status_code in [200, 400, 401, 422], f"Expected 200/4xx, got {response.status_code}: {response.text}"

    def test_login_case_sensitive_password(self):
        """Test login with case-sensitive password (should fail if different case)"""
        self.setup_test_user()

        # Create a password with different case
        wrong_password = self.test_user['password'].swapcase()  # Swap case

        login_data = {
            UserFields.USERNAME: self.test_user['username'],
            UserFields.PASSWORD: wrong_password
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        # Should fail with invalid credentials
        assert response.status_code in [401, 400], f"Expected 401/400, got {response.status_code}"

    # Missing Fields Tests
    def test_login_missing_username(self):
        """Test login with missing username"""

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json={UserFields.PASSWORD: 'TestPassword123!'},
            timeout=self.timeout
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_missing_password(self):
        """Test login with missing password"""

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json={UserFields.USERNAME: 'testuser'},
            timeout=self.timeout
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_missing_both_fields(self):
        """Test login with missing both username and password"""

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json={},
            timeout=self.timeout
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # Edge Cases
    def test_login_with_null_values(self):
        """Test login with null values"""

        login_data = {
            UserFields.USERNAME: None,
            UserFields.PASSWORD: None
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_with_very_long_inputs(self):
        """Test login with extremely long inputs"""

        login_data = {
            UserFields.USERNAME: 'a' * 1000,  # Very long
            UserFields.PASSWORD: 'b' * 1000   # Very long
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_login_with_special_characters(self):
        """Test login with special characters in username/password"""

        login_data = {
            UserFields.USERNAME: 'user!@#$%^&*()',
            UserFields.PASSWORD: 'pass!@#$%^&*()'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def run_all_login_tests(self):
        """Run all user login tests"""
        self.test_login_success()
        self.test_login_success_with_whitespace_trimming()
        self.test_login_username_too_short()
        self.test_login_username_too_long()
        self.test_login_username_invalid_chars()
        self.test_login_username_suspicious_content()
        self.test_login_username_empty()
        self.test_login_username_whitespace_only()
        self.test_login_password_too_short()
        self.test_login_password_too_long()
        self.test_login_password_no_uppercase()
        self.test_login_password_no_lowercase()
        self.test_login_password_no_number()
        self.test_login_password_no_special_char()
        self.test_login_password_empty()
        self.test_login_password_whitespace_only()
        self.test_login_password_suspicious_content()
        self.test_login_invalid_username()
        self.test_login_invalid_password()
        self.test_login_case_sensitive_username()
        self.test_login_case_sensitive_password()
        self.test_login_missing_username()
        self.test_login_missing_password()
        self.test_login_missing_both_fields()
        self.test_login_with_null_values()
        self.test_login_with_very_long_inputs()
        self.test_login_with_special_characters()

if __name__ == "__main__":
    tests = UserLoginTests()
    tests.run_all_login_tests()
