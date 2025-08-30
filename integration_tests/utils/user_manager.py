"""
User Management Utility for Integration Tests
Handles test user creation and authentication
"""
import uuid
import requests
from typing import Dict, Tuple
from api_endpoints import APIEndpoints, UserAPI

class TestUserManager:
    """Manages test users for integration tests"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def create_test_user(self, session: requests.Session) -> Tuple[Dict[str, str], str]:
        """
        Create a test user and return user data and access token

        Args:
            session: Requests session to use for API calls

        Returns:
            Tuple of (user_data, access_token)

        Raises:
            Exception: If user creation or login fails
        """
        # Generate unique user data
        user_id = str(uuid.uuid4().hex[:8])
        user_data = {
            'username': f'testuser_{user_id}',
            'email': f'test_{user_id}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Integration',
            'last_name': 'Test'
        }

        # Register the user
        response = session.post(
            APIEndpoints.get_user_endpoint(UserAPI.REGISTER),
            json=user_data,
            timeout=self.timeout
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create test user: {response.status_code} - {response.text}")

        # Login to get access token
        login_data = {
            'username': user_data['username'],
            'password': user_data['password']
        }

        response = session.post(
            APIEndpoints.get_user_endpoint(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        if response.status_code == 200:
            data = response.json()
            # Handle different response structures
            if 'data' in data and 'access_token' in data['data']:
                access_token = data['data']['access_token']
            elif 'access_token' in data:
                access_token = data['access_token']
            else:
                raise Exception(f"No access_token found in login response: {data}")

            return user_data, access_token
        else:
            raise Exception(f"Failed to login test user: {response.status_code} - {response.text}")

    def get_auth_headers(self, access_token: str) -> Dict[str, str]:
        """
        Get standard authorization headers

        Args:
            access_token: Valid access token

        Returns:
            Dictionary with Authorization header
        """
        return {'Authorization': f'Bearer {access_token}'}
