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

    def test_balance_unauthorized(self):
        """Test balance access without authentication (should fail)"""
        print("  🚫 Testing balance access without authentication")

        response = self.session.get(
            self.user_api(UserAPI.BALANCE),
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("  ✅ Unauthorized balance access correctly rejected")

    def test_balance_invalid_token(self):
        """Test balance access with invalid token (should fail)"""
        print("  🚫 Testing balance access with invalid token")

        headers = {'Authorization': 'Bearer invalid_token_123'}
        response = self.session.get(
            self.user_api(UserAPI.BALANCE),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("  ✅ Invalid token correctly rejected")

    def test_balance_malformed_token(self):
        """Test balance access with malformed token header (should fail)"""
        print("  🚫 Testing balance access with malformed token header")

        headers = {'Authorization': 'Bearer'}  # Missing token
        response = self.session.get(
            self.user_api(UserAPI.BALANCE),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("  ✅ Malformed token correctly rejected")

    def test_balance_authorized(self):
        """Test balance access with authentication"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping authorized balance test - no access token")
            return

        print(f"  💰 Testing balance access with authentication for user: {self.test_user['username']}")

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.get(
            self.user_api(UserAPI.BALANCE),
            headers=headers,
            timeout=self.timeout
        )

        if response.status_code == 200:
            data = response.json()
            # Expected model: BalanceResponse { current_balance, updated_at }
            assert 'current_balance' in data or 'balance' in data
            assert 'updated_at' in data or 'timestamp' in data
            print("  ✅ Authorized balance access successful")
            return data
        else:
            print(f"  ❌ Authorized balance access failed: {response.status_code}")
            print(f"  Response: {response.text}")
            raise AssertionError(f"Authorized balance access failed with status {response.status_code}")

    def run_all_balance_tests(self):
        """Run all user balance tests"""
        print("💰 Running user balance integration tests...")
        print(f"🎯 Service URL: {self.user_api(UserAPI.BALANCE)}")

        try:
            # Unauthorized scenarios
            self.test_balance_unauthorized()
            print("  ✅ Balance (Unauthorized) - PASS")
            self.test_balance_invalid_token()
            print("  ✅ Balance (Invalid Token) - PASS")
            self.test_balance_malformed_token()
            print("  ✅ Balance (Malformed Token) - PASS")

            # Authorized
            self.test_balance_authorized()
            print("  ✅ Balance (Authorized) - PASS")

            print("  🎉 All user balance tests completed successfully!")

        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            raise

if __name__ == "__main__":
    # Run user balance tests
    tests = UserBalanceTests()
    tests.run_all_balance_tests()
    print("All user balance integration tests completed successfully!")
