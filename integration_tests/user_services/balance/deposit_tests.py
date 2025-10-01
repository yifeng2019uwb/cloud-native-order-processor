"""
User Deposit API Integration Tests
Tests POST /balance/deposit endpoint
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

class UserDepositTests:
    """Integration tests for user deposit API"""

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
        """Create a test user and get access token for deposit tests"""
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

    def test_deposit_unauthorized(self):
        """Test deposit without authentication (should fail)"""

        deposit_data = {
            UserFields.AMOUNT: 100.00
        }

        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            json=deposit_data,
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_deposit_invalid_token(self):
        """Test deposit with invalid token (should fail)"""

        deposit_data = {UserFields.AMOUNT: 100.00}
        headers = {'Authorization': 'Bearer invalid_token_123'}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            headers=headers,
            json=deposit_data,
            timeout=self.timeout
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_deposit_malformed_token(self):
        """Test deposit with malformed token header (should fail)"""

        deposit_data = {UserFields.AMOUNT: 100.00}
        headers = {'Authorization': 'Bearer'}  # Missing token
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            headers=headers,
            json=deposit_data,
            timeout=self.timeout
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_deposit_success(self):
        """Test successful deposit with authentication"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        deposit_data = {
            UserFields.AMOUNT: 100.00
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            headers=headers,
            json=deposit_data,
            timeout=self.timeout
        )

        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        data = response.json()
        assert 'success' in data or 'transaction_id' in data
        return data

    def test_deposit_invalid_amount(self):
        """Test deposit with invalid amount (should fail)"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        headers = {'Authorization': f'Bearer {self.access_token}'}

        # Negative amount
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            headers=headers,
            json={UserFields.AMOUNT: -50.00},
            timeout=self.timeout
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

        # Zero amount
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            headers=headers,
            json={UserFields.AMOUNT: 0},
            timeout=self.timeout
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

        # Excessive precision
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            headers=headers,
            json={UserFields.AMOUNT: 100.123456},
            timeout=self.timeout
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_deposit_missing_fields(self):
        """Test deposit with missing required fields (should fail)"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            headers=headers,
            json={},
            timeout=self.timeout
        )

        # Should fail with validation error
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def run_all_deposit_tests(self):
        """Run all user deposit tests"""
        self.test_deposit_unauthorized()
        self.test_deposit_invalid_token()
        self.test_deposit_malformed_token()
        self.test_deposit_success()
        self.test_deposit_invalid_amount()
        self.test_deposit_missing_fields()

if __name__ == "__main__":
    tests = UserDepositTests()
    tests.run_all_deposit_tests()
