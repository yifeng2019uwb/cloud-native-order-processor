"""
User Logout API Integration Tests
Tests POST /auth/logout endpoint
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

class UserLogoutTests:
    """Integration tests for user logout API"""

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
        """Create a test user and get access token for logout tests"""
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

        # Login to get access token
        login_data = {
            UserFields.USERNAME: self.test_user[UserFields.USERNAME],
            UserFields.PASSWORD: self.test_user[UserFields.PASSWORD]
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Failed to login test user: {response.status_code}: {response.text}"
        data = response.json()
        token_data = data.get(UserFields.DATA, data)
        self.access_token = token_data[UserFields.ACCESS_TOKEN]

    def test_logout_success(self):
        """Test successful user logout"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.post(
            self.user_api(UserAPI.LOGOUT),
            headers=headers,
            json={},  # Empty body as required by the API
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert 'success' in data
        assert data['success'] == True

    def test_logout_unauthorized(self):
        """Test logout without authentication (should fail)"""

        response = self.session.post(
            self.user_api(UserAPI.LOGOUT),
            json={},
            timeout=self.timeout
        )

        # Should fail without authentication
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_logout_invalid_token(self):
        """Test logout with invalid token (should fail)"""

        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = self.session.post(
            self.user_api(UserAPI.LOGOUT),
            headers=headers,
            json={},
            timeout=self.timeout
        )

        # Should fail with invalid token
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_logout_missing_body(self):
        """Test logout with missing request body (should fail with 422)"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.post(
            self.user_api(UserAPI.LOGOUT),
            headers=headers,
            timeout=self.timeout
        )

        # Should fail when body is missing (API requires body)
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}: {response.text}"

    def run_all_logout_tests(self):
        """Run all user logout tests"""
        self.test_logout_success()
        self.test_logout_unauthorized()
        self.test_logout_invalid_token()
        self.test_logout_missing_body()

if __name__ == "__main__":
    tests = UserLogoutTests()
    tests.run_all_logout_tests()
