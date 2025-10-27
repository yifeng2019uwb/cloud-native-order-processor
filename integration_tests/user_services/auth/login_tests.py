"""
User Login API Integration Tests
Tests POST /auth/login endpoint with comprehensive validation
"""
import requests
import sys
import os
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, UserAPI
from test_constants import UserFields, TestUserValues

class UserLoginTests:
    """Integration tests for user login API with comprehensive validation"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager()

    def user_api(self, api: UserAPI) -> str:
        """Helper method to get complete user service API URLs"""
        return APIEndpoints.get_user_endpoint(api)

    def test_login_success(self):
        """Test successful user login"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)

        login_data = {
            UserFields.USERNAME: username,
            UserFields.PASSWORD: TestUserValues.DEFAULT_PASSWORD
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        token_data = data.get(UserFields.DATA, data)
        assert UserFields.ACCESS_TOKEN in token_data
        assert UserFields.TOKEN_TYPE in token_data
        assert token_data[UserFields.TOKEN_TYPE] == 'bearer'

    def test_login_case_insensitive_username(self):
        """Test login with different case username"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)

        login_data = {
            UserFields.USERNAME: username.upper(),
            UserFields.PASSWORD: TestUserValues.DEFAULT_PASSWORD
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code == 200

    def test_login_username_too_short(self):
        """Test login with username too short"""
        login_data = {
            UserFields.USERNAME: 'abc',
            UserFields.PASSWORD: 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_login_username_empty(self):
        """Test login with empty username"""
        login_data = {
            UserFields.USERNAME: '',
            UserFields.PASSWORD: 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_login_password_too_short(self):
        """Test login with password too short"""
        login_data = {
            UserFields.USERNAME: 'testuser123',
            UserFields.PASSWORD: 'Short1!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_login_password_empty(self):
        """Test login with empty password"""
        login_data = {
            UserFields.USERNAME: 'testuser123',
            UserFields.PASSWORD: ''
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_login_invalid_credentials(self):
        """Test login with non-existent user"""
        login_data = {
            UserFields.USERNAME: f'nonexistent_{uuid.uuid4().hex[:8]}',
            UserFields.PASSWORD: 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code == 404

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        username = f'testuser_{uuid.uuid4().hex[:8]}'
        token = self.user_manager.create_test_user(self.session, username)

        login_data = {
            UserFields.USERNAME: username,
            UserFields.PASSWORD: 'WrongPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code == 401

    def test_login_missing_username(self):
        """Test login with missing username"""
        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json={UserFields.PASSWORD: 'TestPassword123!'},
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_login_missing_password(self):
        """Test login with missing password"""
        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json={UserFields.USERNAME: 'testuser'},
            timeout=self.timeout
        )

        assert response.status_code == 422

    def run_all_login_tests(self):
        """Run all user login tests"""
        self.test_login_success()
        self.test_login_case_insensitive_username()
        self.test_login_username_too_short()
        self.test_login_username_empty()
        self.test_login_password_too_short()
        self.test_login_password_empty()
        self.test_login_invalid_credentials()
        self.test_login_wrong_password()
        self.test_login_missing_username()
        self.test_login_missing_password()

if __name__ == "__main__":
    tests = UserLoginTests()
    tests.run_all_login_tests()
