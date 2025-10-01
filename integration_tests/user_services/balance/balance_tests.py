"""
User Balance API Integration Tests
Tests GET /balance endpoint
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
from test_constants import UserFields, TestValues

class UserBalanceTests:
    """Integration tests for user balance API"""

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
        """Create a test user and get access token for balance tests"""
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

    def test_balance_unauthorized(self):
        """Test balance access without authentication (should fail)"""

        response = self.session.get(
            self.user_api(UserAPI.BALANCE),
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_balance_invalid_token(self):
        """Test balance access with invalid token (should fail)"""

        headers = {'Authorization': 'Bearer invalid_token_123'}
        response = self.session.get(
            self.user_api(UserAPI.BALANCE),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_balance_malformed_token(self):
        """Test balance access with malformed token header (should fail)"""

        headers = {'Authorization': 'Bearer'}  # Missing token
        response = self.session.get(
            self.user_api(UserAPI.BALANCE),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_balance_authorized(self):
        """Test balance access with authentication"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.get(
            self.user_api(UserAPI.BALANCE),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Expected model: BalanceResponse { current_balance, updated_at }
        assert UserFields.CURRENT_BALANCE in data or UserFields.BALANCE in data
        assert UserFields.UPDATED_AT in data or CommonFields.TIMESTAMP in data
        return data

    def run_all_balance_tests(self):
        """Run all user balance tests"""
        self.test_balance_unauthorized()
        self.test_balance_invalid_token()
        self.test_balance_malformed_token()
        self.test_balance_authorized()

if __name__ == "__main__":
    tests = UserBalanceTests()
    tests.run_all_balance_tests()
