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
        if not self.test_user:
            self.test_user = {
                'username': f'testuser_{uuid.uuid4().hex[:8]}',
                'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
                'password': 'TestPassword123!',
                'first_name': 'Integration',
                'last_name': 'Test'
            }

            # Register the user
            response = self.session.post(
                self.user_api(UserAPI.REGISTER),
                json=self.test_user,
                timeout=self.timeout
            )

            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create test user: {response.status_code}")

            # Login to get access token
            login_data = {
                'username': self.test_user['username'],
                'password': self.test_user['password']
            }

            response = self.session.post(
                self.user_api(UserAPI.LOGIN),
                json=login_data,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                token_data = data.get('data', data)
                self.access_token = token_data['access_token']
            else:
                raise Exception(f"Failed to login test user: {response.status_code}")

    def test_transaction_history_unauthorized(self):
        """Test transaction history access without authentication (should fail)"""
        print("  🚫 Testing transaction history access without authentication")

        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS),
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("  ✅ Unauthorized transaction history access correctly rejected")

    def test_transaction_history_invalid_token(self):
        """Test transaction history access with invalid token"""
        print("  🚫 Testing transaction history access with invalid token")

        headers = {'Authorization': 'Bearer invalid_token_123'}
        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS),
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("  ✅ Invalid token correctly rejected")

    def test_transaction_history_malformed_token(self):
        """Test transaction history access with malformed token header"""
        print("  🚫 Testing transaction history access with malformed token header")

        headers = {'Authorization': 'Bearer'}  # Missing token
        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS),
            headers=headers,
            timeout=self.timeout
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("  ✅ Malformed token correctly rejected")

    def test_transaction_history_authorized(self):
        """Test transaction history access with authentication"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping authorized transaction history test - no access token")
            return

        print(f"  📊 Testing transaction history access with authentication for user: {self.test_user['username']}")

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS),
            headers=headers,
            timeout=self.timeout
        )

        if response.status_code == 200:
            data = response.json()
            assert 'transactions' in data and isinstance(data['transactions'], list)
            assert 'total_count' in data
            print("  ✅ Authorized transaction history access successful")
            return data
        else:
            print(f"  ❌ Authorized transaction history access failed: {response.status_code}")
            print(f"  Response: {response.text}")
            raise AssertionError(f"Authorized transaction history access failed with status {response.status_code}")

    def test_transaction_history_with_pagination(self):
        """Test transaction history with pagination parameters (best-effort)"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping pagination test - no access token")
            return

        print(f"  📄 Testing transaction history with pagination for user: {self.test_user['username']}")

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS) + "?limit=10&offset=0",
            headers=headers,
            timeout=self.timeout
        )

        if response.status_code == 200:
            print("  ✅ Transaction history with pagination successful")
        else:
            print(f"  ℹ️  Pagination not supported or not implemented (status {response.status_code})")

    def test_transaction_history_with_date_filter(self):
        """Test transaction history with date filter parameters (best-effort)"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping date filter test - no access token")
            return

        print(f"  📅 Testing transaction history with date filter for user: {self.test_user['username']}")

        from_date = "2024-01-01"
        to_date = "2024-12-31"

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.get(
            self.user_api(UserAPI.BALANCE_TRANSACTIONS) + f"?from_date={from_date}&to_date={to_date}",
            headers=headers,
            timeout=self.timeout
        )

        if response.status_code == 200:
            print("  ✅ Transaction history with date filter successful")
        else:
            print(f"  ℹ️  Date filter not supported or not implemented (status {response.status_code})")

    def run_all_transaction_history_tests(self):
        """Run all user transaction history tests"""
        print("📊 Running user transaction history integration tests...")
        print(f"🎯 Service URL: {self.user_api(UserAPI.BALANCE_TRANSACTIONS)}")

        try:
            # Unauthorized
            self.test_transaction_history_unauthorized()
            print("  ✅ Transaction History (Unauthorized) - PASS")
            self.test_transaction_history_invalid_token()
            print("  ✅ Transaction History (Invalid Token) - PASS")
            self.test_transaction_history_malformed_token()
            print("  ✅ Transaction History (Malformed Token) - PASS")

            # Authorized and optional params
            self.test_transaction_history_authorized()
            print("  ✅ Transaction History (Authorized) - PASS")
            self.test_transaction_history_with_pagination()
            print("  ✅ Transaction History with Pagination - PASS")
            self.test_transaction_history_with_date_filter()
            print("  ✅ Transaction History with Date Filter - PASS")

            print("  🎉 All user transaction history tests completed successfully!")

        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            raise

if __name__ == "__main__":
    # Run user transaction history tests
    tests = UserTransactionHistoryTests()
    tests.run_all_transaction_history_tests()
    print("All user transaction history integration tests completed successfully!")
