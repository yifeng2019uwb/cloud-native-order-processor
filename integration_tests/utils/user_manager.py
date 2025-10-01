"""
User Management Utility for Integration Tests
Handles test user creation and authentication
"""
import uuid
import requests
from typing import Dict, Tuple
from api_endpoints import APIEndpoints, UserAPI
from test_constants import UserFields, TestValues, CommonFields

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
            UserFields.USERNAME: f'testuser_{user_id}',
            UserFields.EMAIL: f'test_{user_id}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Integration',
            UserFields.LAST_NAME: 'Test'
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
            UserFields.USERNAME: user_data['username'],
            UserFields.PASSWORD: user_data['password']
        }

        response = session.post(
            APIEndpoints.get_user_endpoint(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        if response.status_code == 200:
            data = response.json()
            # Handle different response structures
            if UserFields.DATA in data and UserFields.ACCESS_TOKEN in data[UserFields.DATA]:
                access_token = data[UserFields.DATA][UserFields.ACCESS_TOKEN]
            elif UserFields.ACCESS_TOKEN in data:
                access_token = data[UserFields.ACCESS_TOKEN]
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
