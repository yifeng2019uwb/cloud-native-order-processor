"""
User Profile API Integration Tests
Tests GET /auth/profile and PUT /auth/profile endpoints with comprehensive validation
"""
import requests
import time
import sys
import os
import uuid
import json
from datetime import date, datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from test_data import TestDataManager
from api_endpoints import APIEndpoints, UserAPI
from test_constants import UserFields, TestValues, CommonFields

class UserProfileTests:
    """Integration tests for user profile API with comprehensive validation"""

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
        """Create a test user and get access token for profile tests"""
        self.test_user = {
            UserFields.USERNAME: f'testuser_{uuid.uuid4().hex[:8]}',
            UserFields.EMAIL: f'test_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PASSWORD: 'TestPassword123!',
            UserFields.FIRST_NAME: 'Integration',
            UserFields.LAST_NAME: 'Test',
            UserFields.PHONE: '1234567890',
            UserFields.DATE_OF_BIRTH: '1990-01-01',
            UserFields.MARKETING_EMAILS_CONSENT: True
        }

        # Register the user
        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=self.test_user,
            timeout=self.timeout
        )

        assert response.status_code in [200, 201], f"Failed to create test user: {response.status_code}: {response.text}"

        # Login to get access token
        login_data = {
            UserFields.USERNAME: self.test_user[UserFields.USERNAME],
            UserFields.PASSWORD: self.test_user[UserFields.PASSWORD]
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Failed to login test user: {response.status_code}: {response.text}"
        data = response.json()
        token_data = data.get(UserFields.DATA, data)
        self.access_token = token_data[UserFields.ACCESS_TOKEN]

    # GET Profile Tests
    def test_profile_unauthorized(self):
        """Test user profile without authentication (should fail)"""

        response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        data = response.json()
        # Gateway returns error format: {"error":"PERM_001","message":"Insufficient permissions","code":"PERM_001","timestamp":"..."}
        assert CommonFields.ERROR in data and CommonFields.MESSAGE in data, f"Expected error format, got: {data}"

    def test_profile_invalid_token(self):
        """Test user profile with invalid authentication token"""

        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 for invalid token
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_profile_malformed_token(self):
        """Test user profile with malformed authentication header"""

        headers = {'Authorization': 'Bearer'}  # Missing token value
        response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 or 403 for malformed token (depends on middleware implementation)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"

    def test_profile_authorized(self):
        """Test user profile with authentication"""
        self.setup_test_user()


        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Check required fields
        assert UserFields.USERNAME in data
        assert data[UserFields.USERNAME] == self.test_user[UserFields.USERNAME]
        assert UserFields.EMAIL in data
        assert UserFields.FIRST_NAME in data
        assert UserFields.LAST_NAME in data
        assert UserFields.CREATED_AT in data
        assert UserFields.UPDATED_AT in data
        return data

    def test_profile_authorized_case_insensitive_username(self):
        """Test user profile with case-insensitive username in token"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        # Login with different case username to get token
        login_data = {
            UserFields.USERNAME: self.test_user[UserFields.USERNAME].upper(),  # Different case
            UserFields.PASSWORD: self.test_user[UserFields.PASSWORD]
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        # Username should be case-insensitive for login
        assert response.status_code == 200, f"Expected 200 (case-insensitive username), got {response.status_code}: {response.text}"

        data = response.json()
        token_data = data.get(UserFields.DATA, data)
        case_token = token_data[UserFields.ACCESS_TOKEN]

        headers = {'Authorization': f'Bearer {case_token}'}
        profile_response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            timeout=self.timeout
        )

        assert profile_response.status_code == 200, f"Expected 200, got {profile_response.status_code}: {profile_response.text}"
        profile_data = profile_response.json()
        assert profile_data[UserFields.USERNAME] == self.test_user[UserFields.USERNAME]  # Should return original case

    # PUT Profile Update Tests
    def test_profile_update_success(self):
        """Test successful profile update with all fields"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        # Update profile data with all fields
        update_data = {
            UserFields.FIRST_NAME: 'Updated',
            UserFields.LAST_NAME: 'Profile',
            UserFields.EMAIL: f'updated_{uuid.uuid4().hex[:8]}@example.com',
            UserFields.PHONE: '9876543210',
            UserFields.DATE_OF_BIRTH: '1985-06-15'
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert 'success' in data or 'user' in data
        return data

    def test_profile_update_partial(self):
        """Test profile update with only some fields"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        # Update only first name
        update_data = {
            UserFields.FIRST_NAME: 'Partial'
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert 'success' in data or 'user' in data

    def test_profile_update_empty_fields(self):
        """Test profile update with empty string fields (should be rejected)"""
        self.setup_test_user()

        # Try to update with empty strings
        update_data = {
            UserFields.FIRST_NAME: '',
            UserFields.LAST_NAME: '',
            UserFields.EMAIL: ''
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        # Should fail with validation error
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_profile_update_whitespace_only(self):
        """Test profile update with whitespace-only fields (should be rejected)"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        # Try to update with whitespace-only strings
        update_data = {
            UserFields.FIRST_NAME: '   ',
            UserFields.LAST_NAME: '   ',
            UserFields.EMAIL: '   '
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        # Should fail with validation error
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # First Name Validation Tests
    def test_profile_update_first_name_too_short(self):
        """Test profile update with first name too short (< 1 char)"""
        self.setup_test_user()

        assert self.access_token, "No access token available"

        update_data = {
            UserFields.FIRST_NAME: ''  # Too short
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_profile_update_first_name_too_long(self):
        """Test profile update with first name too long (> 50 chars)"""
        self.setup_test_user()

        update_data = {
            UserFields.FIRST_NAME: 'A' * 51  # Too long
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_profile_update_first_name_invalid_chars(self):
        """Test profile update with first name containing invalid characters"""
        self.setup_test_user()

        update_data = {
            UserFields.FIRST_NAME: 'John@123'  # Contains @ and numbers
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_profile_update_first_name_suspicious_content(self):
        """Test profile update with first name containing suspicious content"""
        self.setup_test_user()

        update_data = {
            UserFields.FIRST_NAME: '<script>alert("xss")</script>'  # XSS attempt
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # Last Name Validation Tests
    def test_profile_update_last_name_too_short(self):
        """Test profile update with last name too short (< 1 char)"""
        self.setup_test_user()

        update_data = {
            UserFields.LAST_NAME: ''  # Too short
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_profile_update_last_name_too_long(self):
        """Test profile update with last name too long (> 50 chars)"""
        self.setup_test_user()

        update_data = {
            UserFields.LAST_NAME: 'A' * 51  # Too long
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_profile_update_last_name_invalid_chars(self):
        """Test profile update with last name containing invalid characters"""
        self.setup_test_user()

        update_data = {
            UserFields.LAST_NAME: 'Doe@123'  # Contains @ and numbers
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # Email Validation Tests
    def test_profile_update_email_invalid_format(self):
        """Test profile update with invalid email format"""
        self.setup_test_user()

        update_data = {
            UserFields.EMAIL: 'invalid-email'  # Invalid format
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_profile_update_email_suspicious_content(self):
        """Test profile update with email containing suspicious content"""
        self.setup_test_user()

        update_data = {
            UserFields.EMAIL: '<script>alert("xss")</script>@example.com'  # XSS attempt
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # Phone Validation Tests
    def test_profile_update_phone_too_short(self):
        """Test profile update with phone number too short (< 10 digits)"""
        self.setup_test_user()

        update_data = {
            UserFields.PHONE: '123456789'  # Too short (9 digits)
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_profile_update_phone_too_long(self):
        """Test profile update with phone number too long (> 15 digits)"""
        self.setup_test_user()

        update_data = {
            UserFields.PHONE: '1234567890123456'  # Too long (16 digits)
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_profile_update_phone_formatted_success(self):
        """Test profile update with formatted phone number (should succeed and be sanitized)"""
        self.setup_test_user()

        update_data = {
            UserFields.PHONE: '123-456-7890'  # Contains hyphens - should be sanitized to digits
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        # Should succeed because phone validation accepts formatted numbers and sanitizes them
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_profile_update_phone_suspicious_content(self):
        """Test profile update with phone number containing suspicious content"""
        self.setup_test_user()

        update_data = {
            UserFields.PHONE: '<script>alert("xss")</script>123-456-7890'  # XSS attempt
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # Date of Birth Validation Tests
    def test_profile_update_dob_future_date(self):
        """Test profile update with future date of birth"""
        self.setup_test_user()

        # Set future date
        future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')

        update_data = {
            UserFields.DATE_OF_BIRTH: future_date
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_profile_update_dob_invalid_format(self):
        """Test profile update with invalid date of birth format"""
        self.setup_test_user()

        update_data = {
            UserFields.DATE_OF_BIRTH: '1990/01/01'  # Invalid format (should be YYYY-MM-DD)
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    # Edge Cases
    def test_profile_update_with_null_values(self):
        """Test profile update with null values (should succeed as fields are optional)"""
        self.setup_test_user()

        update_data = {
            UserFields.FIRST_NAME: None,
            UserFields.LAST_NAME: None,
            UserFields.EMAIL: None
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        # Should succeed because all fields are Optional and can be set to None
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_profile_update_with_very_long_inputs(self):
        """Test profile update with extremely long inputs"""
        self.setup_test_user()

        update_data = {
            UserFields.FIRST_NAME: 'A' * 1000,  # Very long
            UserFields.LAST_NAME: 'B' * 1000,   # Very long
            UserFields.EMAIL: f'{"very_long_email_" + "a" * 1000}@example.com'  # Very long
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def test_profile_update_with_special_characters(self):
        """Test profile update with special characters"""
        self.setup_test_user()

        update_data = {
            UserFields.FIRST_NAME: 'John!@#$%^&*()',
            UserFields.LAST_NAME: 'Doe!@#$%^&*()',
            UserFields.EMAIL: 'john!@#$%^&*()@example.com'
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"

    def run_all_profile_tests(self):
        """Run all user profile tests"""
        self.test_profile_unauthorized()
        self.test_profile_invalid_token()
        self.test_profile_malformed_token()
        self.test_profile_authorized()
        self.test_profile_authorized_case_insensitive_username()
        self.test_profile_update_success()
        self.test_profile_update_partial()
        self.test_profile_update_empty_fields()
        self.test_profile_update_whitespace_only()
        self.test_profile_update_first_name_too_short()
        self.test_profile_update_first_name_too_long()
        self.test_profile_update_first_name_invalid_chars()
        self.test_profile_update_first_name_suspicious_content()
        self.test_profile_update_last_name_too_short()
        self.test_profile_update_last_name_too_long()
        self.test_profile_update_last_name_invalid_chars()
        self.test_profile_update_email_invalid_format()
        self.test_profile_update_email_suspicious_content()
        self.test_profile_update_phone_too_short()
        self.test_profile_update_phone_too_long()
        self.test_profile_update_phone_formatted_success()
        self.test_profile_update_phone_suspicious_content()
        self.test_profile_update_dob_future_date()
        self.test_profile_update_dob_invalid_format()
        self.test_profile_update_with_null_values()
        self.test_profile_update_with_very_long_inputs()
        self.test_profile_update_with_special_characters()

if __name__ == "__main__":
    tests = UserProfileTests()
    tests.run_all_profile_tests()
