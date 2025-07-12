"""
User Service Integration Tests
Tests user registration, login, and profile management
"""
import requests
import time
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from simple_retry import simple_retry
from test_data import TestDataManager

class UserServiceTests:
    """Integration tests for user service"""

    def __init__(self, user_service_url: str, timeout: int = 10):
        self.user_service_url = user_service_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()
        self.created_users = []

    def test_user_registration(self) -> Dict[str, Any]:
        """Test user registration with UUID-based data"""
        start_time = time.time()

        # Generate unique test user data
        user_data = self.test_data_manager.generate_user_data()
        self.created_users.append(user_data)

        def register_user():
            return self.session.post(
                f"{self.user_service_url}/auth/register",
                json=user_data,
                timeout=self.timeout
            )

        try:
            response = simple_retry(register_user)
            duration = time.time() - start_time

            success = response.status_code == 201
            data = response.json() if success else {}

            return {
                'test_name': 'User Registration',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 201, got {response.status_code}",
                'service': 'user-service',
                'test_data': user_data['test_id']
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': 'User Registration',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'user-service',
                'test_data': user_data['test_id']
            }

    def test_user_login(self) -> Dict[str, Any]:
        """Test user login with registered user"""
        start_time = time.time()

        if not self.created_users:
            return {
                'test_name': 'User Login',
                'success': False,
                'duration': 0,
                'status_code': None,
                'error': 'No users created for login test',
                'service': 'user-service',
                'test_data': None
            }

        # Use the first created user for login
        user_data = self.created_users[0]
        login_data = {
            'username': user_data['username'],
            'password': user_data['password']
        }

        def login_user():
            return self.session.post(
                f"{self.user_service_url}/auth/login",
                json=login_data,
                timeout=self.timeout
            )

        try:
            response = simple_retry(login_user)
            duration = time.time() - start_time

            success = response.status_code == 200
            data = response.json() if success else {}

            # Store token for profile test
            if success and 'access_token' in data:
                self.access_token = data['access_token']

            return {
                'test_name': 'User Login',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 200, got {response.status_code}",
                'service': 'user-service',
                'test_data': user_data['test_id']
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': 'User Login',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'user-service',
                'test_data': user_data['test_id']
            }

    def test_user_profile(self) -> Dict[str, Any]:
        """Test user profile retrieval with authentication"""
        start_time = time.time()

        if not hasattr(self, 'access_token'):
            return {
                'test_name': 'User Profile',
                'success': False,
                'duration': 0,
                'status_code': None,
                'error': 'No access token available for profile test',
                'service': 'user-service',
                'test_data': None
            }

        headers = {'Authorization': f'Bearer {self.access_token}'}

        def get_profile():
            return self.session.get(
                f"{self.user_service_url}/auth/profile",
                headers=headers,
                timeout=self.timeout
            )

        try:
            response = simple_retry(get_profile)
            duration = time.time() - start_time

            success = response.status_code == 200
            data = response.json() if success else {}

            return {
                'test_name': 'User Profile',
                'success': success,
                'duration': duration,
                'status_code': response.status_code,
                'error': None if success else f"Expected 200, got {response.status_code}",
                'service': 'user-service',
                'test_data': self.created_users[0]['test_id'] if self.created_users else None
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                'test_name': 'User Profile',
                'success': False,
                'duration': duration,
                'status_code': None,
                'error': str(e),
                'service': 'user-service',
                'test_data': self.created_users[0]['test_id'] if self.created_users else None
            }

    def cleanup_test_users(self):
        """Clean up test users (placeholder for future implementation)"""
        print(f"🧹 Cleanup: {len(self.created_users)} test users marked for cleanup")
        # TODO: Implement actual cleanup when user service supports user deletion
        self.created_users = []

    def run_all_user_tests(self) -> list:
        """Run all user service tests"""
        print("👤 Running user service tests...")

        tests = [
            self.test_user_registration(),
            self.test_user_login(),
            self.test_user_profile()
        ]

        # Print results
        for test in tests:
            status = "✅ PASS" if test['success'] else "❌ FAIL"
            print(f"  {status} {test['test_name']} - {test['duration']*1000:.2f}ms")
            if test['error']:
                print(f"    Error: {test['error']}")

        # Cleanup test data
        self.cleanup_test_users()

        return tests