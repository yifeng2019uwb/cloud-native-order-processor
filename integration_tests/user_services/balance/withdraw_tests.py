"""
User Withdraw API Integration Tests
Tests POST /balance/withdraw endpoint
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

class UserWithdrawTests:
    """Integration tests for user withdraw API"""

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
        """Create a test user and get access token for withdraw tests"""
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

    def test_withdraw_unauthorized(self):
        """Test withdraw without authentication (should fail)"""

        withdraw_data = {
            UserFields.AMOUNT: 50.00
        }

        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            json=withdraw_data,
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_withdraw_invalid_token(self):
        """Test withdraw with invalid token (should fail)"""

        withdraw_data = {UserFields.AMOUNT: 25.00}
        headers = {'Authorization': 'Bearer invalid_token_123'}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            headers=headers,
            json=withdraw_data,
            timeout=self.timeout
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_withdraw_malformed_token(self):
        """Test withdraw with malformed token header (should fail)"""

        withdraw_data = {UserFields.AMOUNT: 25.00}
        headers = {'Authorization': 'Bearer'}  # Missing token
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            headers=headers,
            json=withdraw_data,
            timeout=self.timeout
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_withdraw_success(self):
        """Test successful withdraw with authentication"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        # First deposit to ensure funds available
        headers = {'Authorization': f'Bearer {self.access_token}'}
        self.session.post(
            self.user_api(UserAPI.BALANCE_DEPOSIT),
            headers=headers,
            json={UserFields.AMOUNT: 100.00},
            timeout=self.timeout
        )

        withdraw_data = {
            UserFields.AMOUNT: 25.00
        }

        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            headers=headers,
            json=withdraw_data,
            timeout=self.timeout
        )

        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        data = response.json()
        assert 'success' in data or 'transaction_id' in data
        return data

    def test_withdraw_invalid_amount(self):
        """Test withdraw with invalid amount (should fail)"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        headers = {'Authorization': f'Bearer {self.access_token}'}

        # Negative amount
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            headers=headers,
            json={UserFields.AMOUNT: -25.00},
            timeout=self.timeout
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

        # Zero amount
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            headers=headers,
            json={UserFields.AMOUNT: 0},
            timeout=self.timeout
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_withdraw_insufficient_funds(self):
        """Test withdraw with insufficient funds (should fail)"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            headers=headers,
            json={UserFields.AMOUNT: 999999.00},
            timeout=self.timeout
        )

        # Should fail with insufficient funds or conflict
        assert response.status_code in [400, 422, 409], f"Expected 400/422/409, got {response.status_code}"

    def test_withdraw_missing_fields(self):
        """Test withdraw with missing required fields (should fail)"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.post(
            self.user_api(UserAPI.BALANCE_WITHDRAW),
            headers=headers,
            json={},
            timeout=self.timeout
        )

        # Should fail with validation error
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def run_all_withdraw_tests(self):
        """Run all user withdraw tests"""
        self.test_withdraw_unauthorized()
        self.test_withdraw_invalid_token()
        self.test_withdraw_malformed_token()
        self.test_withdraw_success()
        self.test_withdraw_invalid_amount()
        self.test_withdraw_insufficient_funds()
        self.test_withdraw_missing_fields()

if __name__ == "__main__":
    tests = UserWithdrawTests()
    tests.run_all_withdraw_tests()
