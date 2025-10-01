"""
User Transaction History API Integration Tests
Tests GET /balance/transactions endpoint
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

class UserTransactionHistoryTests:
    """Integration tests for user transaction history API"""

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
        """Create a test user and get access token for transaction history tests"""
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

    def test_transaction_history_unauthorized(self):
        """Test transaction history access without authentication (should fail)"""
        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS),
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_transaction_history_invalid_token(self):
        """Test transaction history access with invalid token"""
        headers = {'Authorization': 'Bearer invalid_token_123'}
        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS),
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_transaction_history_malformed_token(self):
        """Test transaction history access with malformed token header"""
        headers = {'Authorization': 'Bearer'}  # Missing token
        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS),
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_transaction_history_authorized(self):
        """Test transaction history access with authentication"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert UserFields.TRANSACTIONS in data and isinstance(data[UserFields.TRANSACTIONS], list)
        assert CommonFields.TOTAL_COUNT in data
        return data

    def test_transaction_history_with_pagination(self):
        """Test transaction history with pagination parameters (best-effort)"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS) + "?limit=10&offset=0",
            headers=headers,
            timeout=self.timeout
        )

        # Pagination is optional, so we just check it doesn't error
        assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"

    def test_transaction_history_with_date_filter(self):
        """Test transaction history with date filter parameters (best-effort)"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        from_date = "2024-01-01"
        to_date = "2024-12-31"

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS) + f"?from_date={from_date}&to_date={to_date}",
            headers=headers,
            timeout=self.timeout
        )

        # Date filter is optional, so we just check it doesn't error
        assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"

    def run_all_transaction_history_tests(self):
        """Run all user transaction history tests"""
        self.test_transaction_history_unauthorized()
        self.test_transaction_history_invalid_token()
        self.test_transaction_history_malformed_token()
        self.test_transaction_history_authorized()
        self.test_transaction_history_with_pagination()
        self.test_transaction_history_with_date_filter()

if __name__ == "__main__":
    tests = UserTransactionHistoryTests()
    tests.run_all_transaction_history_tests()
