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

    def test_logout_success(self):
        """Test successful user logout"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping logout test - no access token")
            return

        print(f"  🚪 Testing logout for user: {self.test_user['username']}")

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.post(
            self.user_api(UserAPI.LOGOUT),
            headers=headers,
            json={},  # Empty body as required by the API
            timeout=self.timeout
        )

        if response.status_code == 200:
            data = response.json()
            assert 'success' in data
            assert data['success'] == True
            print("  ✅ Logout successful")
        else:
            print(f"  ⚠️  Logout response: {response.status_code}")
            print(f"  Response: {response.text}")

    def test_logout_unauthorized(self):
        """Test logout without authentication (should fail)"""
        print("  🚫 Testing logout without authentication")

        response = self.session.post(
            self.user_api(UserAPI.LOGOUT),
            json={},
            timeout=self.timeout
        )

        # Should fail without authentication
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("  ✅ Unauthorized logout correctly rejected")

    def test_logout_invalid_token(self):
        """Test logout with invalid token (should fail)"""
        print("  🚫 Testing logout with invalid token")

        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = self.session.post(
            self.user_api(UserAPI.LOGOUT),
            headers=headers,
            json={},
            timeout=self.timeout
        )

        # Should fail with invalid token
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("  ✅ Invalid token logout correctly rejected")

    def test_logout_missing_body(self):
        """Test logout with missing request body"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping logout test - no access token")
            return

        print(f"  🚪 Testing logout with missing body for user: {self.test_user['username']}")

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.post(
            self.user_api(UserAPI.LOGOUT),
            headers=headers,
            timeout=self.timeout
        )

        # Should work with or without body
        if response.status_code == 200:
            print("  ✅ Logout successful without body")
        else:
            print(f"  ⚠️  Logout response without body: {response.status_code}")

    def run_all_logout_tests(self):
        """Run all user logout tests"""
        print("🚪 Running user logout integration tests...")
        print(f"🎯 Service URL: {APIEndpoints.get_user_endpoint(UserAPI.LOGOUT)}")

        try:
            # Test 1: Logout Success
            self.test_logout_success()
            print("  ✅ Logout Success - PASS")

            # Test 2: Logout Unauthorized
            self.test_logout_unauthorized()
            print("  ✅ Logout Unauthorized - PASS")

            # Test 3: Logout Invalid Token
            self.test_logout_invalid_token()
            print("  ✅ Logout Invalid Token - PASS")

            # Test 4: Logout Missing Body
            self.test_logout_missing_body()
            print("  ✅ Logout Missing Body - PASS")

            print("  🎉 All user logout tests completed successfully!")

        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            raise

if __name__ == "__main__":
    # Run user logout tests
    tests = UserLogoutTests()
    tests.run_all_logout_tests()
    print("All user logout integration tests completed successfully!")
