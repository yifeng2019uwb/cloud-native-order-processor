"""
User Profile API Integration Tests
Tests GET /auth/profile and PUT /auth/profile endpoints with comprehensive validation
"""
import requests
import sys
import os
import uuid
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from user_manager import TestUserManager
from api_endpoints import APIEndpoints, UserAPI
from test_constants import UserFields

class UserProfileTests:
    """Integration tests for user profile API - focus on profile validation"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.user_manager = TestUserManager()

    def user_api(self, api: UserAPI) -> str:
        """Helper method to get complete user service API URLs"""
        return APIEndpoints.get_user_endpoint(api)

    def test_get_profile_success(self):
        """Test getting user profile"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert UserFields.USERNAME in data
        assert data[UserFields.USERNAME] == user[UserFields.USERNAME]
        assert UserFields.EMAIL in data
        assert UserFields.FIRST_NAME in data
        assert UserFields.LAST_NAME in data
        assert UserFields.CREATED_AT in data
        assert UserFields.UPDATED_AT in data

    def test_profile_update_success(self):
        """Test successful profile update with all fields"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        new_email = f'updated_{uuid.uuid4().hex[:8]}@example.com'
        update_data = {
            UserFields.FIRST_NAME: 'Updated',
            UserFields.LAST_NAME: 'Profile',
            UserFields.EMAIL: new_email,
            UserFields.PHONE: '9876543210',
            UserFields.DATE_OF_BIRTH: '1985-06-15'
        }

        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 200

        # Verify the update by getting the profile
        get_response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            timeout=self.timeout
        )

        assert get_response.status_code == 200
        profile_data = get_response.json()
        assert profile_data[UserFields.FIRST_NAME] == 'Updated'
        assert profile_data[UserFields.LAST_NAME] == 'Profile'
        assert profile_data[UserFields.EMAIL] == new_email

    def test_profile_update_partial(self):
        """Test profile update with only first name"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        update_data = {
            UserFields.FIRST_NAME: 'Partial'
        }

        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 200

        # Verify the update
        get_response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            timeout=self.timeout
        )

        assert get_response.status_code == 200
        profile_data = get_response.json()
        assert profile_data[UserFields.FIRST_NAME] == 'Partial'

    def test_profile_update_empty_first_name(self):
        """Test profile update with empty first name"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        update_data = {
            UserFields.FIRST_NAME: ''
        }

        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_profile_update_whitespace_first_name(self):
        """Test profile update with whitespace-only first name"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        update_data = {
            UserFields.FIRST_NAME: '   '
        }

        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_profile_update_first_name_too_long(self):
        """Test profile update with first name too long"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        update_data = {
            UserFields.FIRST_NAME: 'A' * 51
        }

        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_profile_update_first_name_invalid_chars(self):
        """Test profile update with first name containing invalid characters"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        update_data = {
            UserFields.FIRST_NAME: 'John@123'
        }

        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_profile_update_last_name_too_long(self):
        """Test profile update with last name too long"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        update_data = {
            UserFields.LAST_NAME: 'B' * 51
        }

        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_profile_update_email_invalid_format(self):
        """Test profile update with invalid email format"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        update_data = {
            UserFields.EMAIL: 'invalid-email'
        }

        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_profile_update_phone_too_short(self):
        """Test profile update with phone number too short"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        update_data = {
            UserFields.PHONE: '123456789'
        }

        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_profile_update_phone_too_long(self):
        """Test profile update with phone number too long"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        update_data = {
            UserFields.PHONE: '1234567890123456'
        }

        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_profile_update_dob_future_date(self):
        """Test profile update with future date of birth"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')

        update_data = {
            UserFields.DATE_OF_BIRTH: future_date
        }

        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def test_profile_update_dob_invalid_format(self):
        """Test profile update with invalid date of birth format"""
        user, token = self.user_manager.create_test_user(self.session)
        headers = {'Authorization': f'Bearer {token}'}

        update_data = {
            UserFields.DATE_OF_BIRTH: '1990/01/01'
        }

        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 422

    def run_all_profile_tests(self):
        """Run all user profile tests"""
        self.test_get_profile_success()
        self.test_profile_update_success()
        self.test_profile_update_partial()
        self.test_profile_update_empty_first_name()
        self.test_profile_update_whitespace_first_name()
        self.test_profile_update_first_name_too_long()
        self.test_profile_update_first_name_invalid_chars()
        self.test_profile_update_last_name_too_long()
        self.test_profile_update_email_invalid_format()
        self.test_profile_update_phone_too_short()
        self.test_profile_update_phone_too_long()
        self.test_profile_update_dob_future_date()
        self.test_profile_update_dob_invalid_format()

if __name__ == "__main__":
    tests = UserProfileTests()
    tests.run_all_profile_tests()
