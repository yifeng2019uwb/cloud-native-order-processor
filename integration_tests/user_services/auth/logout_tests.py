"""
User Logout API Integration Tests
Tests POST /auth/logout endpoint - validates logout functionality
"""
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, UserAPI
from test_constants import UserFields

class UserLogoutTests:
    """Integration tests for user logout API"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager()

    def user_api(self, api: UserAPI) -> str:
        """Helper method to get complete user service API URLs"""
        return APIEndpoints.get_user_endpoint(api)

    def test_logout_success(self):
        """Test successful user logout"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        logout_data = {
            UserFields.ACCESS_TOKEN: token
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGOUT),
            headers=headers,
            json=logout_data,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert 'success' in data
        assert data['success'] == True

    def test_logout_missing_body(self):
        """Test logout with missing request body is rejected"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        response = self.session.post(
            self.user_api(UserAPI.LOGOUT),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def run_all_logout_tests(self):
        """Run all logout tests"""
        self.test_logout_success()
        self.test_logout_missing_body()

if __name__ == "__main__":
    tests = UserLogoutTests()
    tests.run_all_logout_tests()
