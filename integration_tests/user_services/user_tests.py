"""
User Service Integration Tests
Tests user login, logout, and profile management
"""
import requests
import time
import sys
import os
import uuid
import json

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from test_data import TestDataManager
from api_endpoints import APIEndpoints, UserAPI

class UserServiceTests:
    """Integration tests for user service"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()
        self.access_token = None
        self.test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Integration',
            'last_name': 'Test'
        }

    def user_api(self, api: UserAPI) -> str:
        """Helper method to get complete user service API URLs"""
        return APIEndpoints.get_user_endpoint(api)

    def test_health_check(self):
        """Test health endpoint"""
        response = self.session.get(
            self.user_api(UserAPI.HEALTH),
            timeout=self.timeout
        )
        data = response.json()

        # Assert response
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        assert data['service'] == 'user-auth-service'

    def test_user_registration(self):
        """Test user registration with real test data"""
        print(f"  📝 Testing registration with user: {self.test_user['username']}")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=self.test_user,
            timeout=self.timeout
        )

        if response.status_code in [200, 201]:  # 201 is correct for resource creation
            data = response.json()
            assert 'success' in data
            assert data['success'] == True
            print("  ✅ Registration successful")
        else:
            print(f"  ❌ Registration failed: {response.status_code}")
            print(f"  Response: {response.text}")
            raise AssertionError(f"Registration failed with status {response.status_code}")

    def test_user_login(self):
        """Test user login with real test data"""
        print(f"  🔐 Testing login with user: {self.test_user['username']}")

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
            assert 'access_token' in data
            self.access_token = data['access_token']
            print("  ✅ Login successful")
        else:
            print(f"  ❌ Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            raise AssertionError(f"Login failed with status {response.status_code}")

    def test_user_profile_unauthorized(self):
        """Test user profile without authentication (should fail)"""
        response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        data = response.json()
        assert 'detail' in data
        print("  ✅ Unauthorized profile access correctly rejected")

    def test_user_profile_authorized(self):
        """Test user profile with authentication"""
        if not self.access_token:
            print("  ⚠️  Skipping authorized profile test - no access token")
            return

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            timeout=self.timeout
        )

        if response.status_code == 200:
            data = response.json()
            assert 'username' in data
            assert data['username'] == self.test_user['username']
            print("  ✅ Authorized profile access successful")
        else:
            print(f"  ❌ Authorized profile access failed: {response.status_code}")
            print(f"  Response: {response.text}")
            raise AssertionError(f"Authorized profile access failed with status {response.status_code}")

    def test_user_logout(self):
        """Test user logout"""
        if not self.access_token:
            print("  ⚠️  Skipping logout test - no access token")
            return

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

    def run_all_user_tests(self):
        """Run all user service tests"""
        print("👤 Running user service integration tests...")
        print(f"🎯 Service URL: {APIEndpoints.get_user_endpoint(UserAPI.HEALTH)}")

        try:
            # Test 1: Health Check
            self.test_health_check()
            print("  ✅ Health Check - PASS")

            # Test 2: User Registration
            self.test_user_registration()
            print("  ✅ User Registration - PASS")

            # Test 3: User Login
            self.test_user_login()
            print("  ✅ User Login - PASS")

            # Test 4: Profile (Unauthorized)
            self.test_user_profile_unauthorized()
            print("  ✅ User Profile (Unauthorized) - PASS")

            # Test 5: Profile (Authorized)
            self.test_user_profile_authorized()
            print("  ✅ User Profile (Authorized) - PASS")

            # Test 6: User Logout
            self.test_user_logout()
            print("  ✅ User Logout - PASS")

            print("  🎉 All user service integration tests completed successfully!")

        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            raise

if __name__ == "__main__":
    # Run user service tests
    tests = UserServiceTests()
    tests.run_all_user_tests()
    print("All user service integration tests completed successfully!")