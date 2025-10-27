"""
User Management Utility for Integration Tests
Handles test user creation and authentication
"""
import uuid
import requests
from typing import Tuple
import sys
import os

from api_endpoints import APIEndpoints, UserAPI
from test_constants import UserFields, TestValues, CommonFields, TestUserValues

class TestUserManager:
    """Manages test users for integration tests"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def create_test_user(self, session: requests.Session, username: str) -> str:
        """
        Create a test user and return access token

        Args:
            session: Requests session to use for API calls
            username: Required username for the test user

        Returns:
            Access token string

        Raises:
            Exception: If user creation or login fails
        """
        email = f'{username}{TestUserValues.DEFAULT_EMAIL_DOMAIN}'
        password = TestUserValues.DEFAULT_PASSWORD

        # Create registration request as plain dict
        register_data = {
            UserFields.USERNAME: username,
            UserFields.EMAIL: email,
            UserFields.PASSWORD: password,
            UserFields.FIRST_NAME: TestUserValues.DEFAULT_FIRST_NAME,
            UserFields.LAST_NAME: TestUserValues.DEFAULT_LAST_NAME
        }

        # Register user
        response = session.post(
            APIEndpoints.get_user_endpoint(UserAPI.REGISTER),
            json=register_data,
            timeout=self.timeout
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create test user: {response.status_code} - {response.text}")

        # Login user to get token
        login_data = {
            UserFields.USERNAME: username,
            UserFields.PASSWORD: password
        }

        response = session.post(
            APIEndpoints.get_user_endpoint(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        if response.status_code == 200:
            # Parse response as plain dict
            response_data = response.json()
            return response_data[UserFields.ACCESS_TOKEN]
        else:
            raise Exception(f"Failed to login test user: {response.status_code} - {response.text}")

    def build_auth_headers(self, token: str) -> dict:
        """
        Build authorization headers from token

        Args:
            token: Access token

        Returns:
            Dictionary with Authorization header
        """
        return {'Authorization': f'Bearer {token}'}
