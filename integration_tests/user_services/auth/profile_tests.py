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
        if not self.test_user:
            self.test_user = {
                'username': f'testuser_{uuid.uuid4().hex[:8]}',
                'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
                'password': 'TestPassword123!',
                'first_name': 'Integration',
                'last_name': 'Test',
                'phone': '1234567890',
                'date_of_birth': '1990-01-01',
                'marketing_emails_consent': True
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

    # GET Profile Tests
    def test_profile_unauthorized(self):
        """Test user profile without authentication (should fail)"""
        print("  🚫 Testing profile access without authentication")

        response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            timeout=self.timeout
        )

        # Should return 401 or 403 for unauthorized
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        data = response.json()
        # Gateway returns error format: {"error":"PERM_001","message":"Insufficient permissions","code":"PERM_001","timestamp":"..."}
        assert 'error' in data and 'message' in data, f"Expected error format, got: {data}"
        print("  ✅ Unauthorized profile access correctly rejected")

    def test_profile_invalid_token(self):
        """Test user profile with invalid authentication token"""
        print("  🚫 Testing profile access with invalid token")

        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 for invalid token
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("  ✅ Invalid token correctly rejected")

    def test_profile_malformed_token(self):
        """Test user profile with malformed authentication header"""
        print("  🚫 Testing profile access with malformed token")

        headers = {'Authorization': 'Bearer'}  # Missing token value
        response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            timeout=self.timeout
        )

        # Should return 401 or 403 for malformed token (depends on middleware implementation)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"  ✅ Malformed token correctly rejected with status {response.status_code}")

    def test_profile_authorized(self):
        """Test user profile with authentication"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping authorized profile test - no access token")
            return

        print(f"  🔐 Testing profile access with authentication for user: {self.test_user['username']}")

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.get(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            timeout=self.timeout
        )

        if response.status_code == 200:
            data = response.json()
            # Check required fields
            assert 'username' in data
            assert data['username'] == self.test_user['username']
            assert 'email' in data
            assert 'first_name' in data
            assert 'last_name' in data
            assert 'created_at' in data
            assert 'updated_at' in data

            # Check optional fields if they exist
            if 'phone' in data:
                print(f"  📱 Phone: {data['phone']}")
            if 'date_of_birth' in data:
                print(f"  🎂 Date of Birth: {data['date_of_birth']}")
            if 'marketing_emails_consent' in data:
                print(f"  📧 Marketing Consent: {data['marketing_emails_consent']}")

            print("  ✅ Authorized profile access successful")
            return data
        else:
            print(f"  ❌ Authorized profile access failed: {response.status_code}")
            print(f"  Response: {response.text}")
            raise AssertionError(f"Authorized profile access failed with status {response.status_code}")

    def test_profile_authorized_case_insensitive_username(self):
        """Test user profile with case-insensitive username in token"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping case-insensitive test - no access token")
            return

        print(f"  🔐 Testing profile access with case-insensitive username for user: {self.test_user['username']}")

        # Login with different case username to get token
        login_data = {
            'username': self.test_user['username'].upper(),  # Different case
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
            case_token = token_data['access_token']

            headers = {'Authorization': f'Bearer {case_token}'}
            response = self.session.get(
                self.user_api(UserAPI.PROFILE),
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                assert data['username'] == self.test_user['username']  # Should return original case
                print("  ✅ Case-insensitive username profile access successful")
            else:
                print(f"  ❌ Case-insensitive profile access failed: {response.status_code}")
                raise AssertionError(f"Case-insensitive profile access failed with status {response.status_code}")
        else:
            print("  ℹ️  Username is case-sensitive, skipping case-insensitive test")

    # PUT Profile Update Tests
    def test_profile_update_success(self):
        """Test successful profile update with all fields"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping profile update test - no access token")
            return

        print(f"  ✏️  Testing comprehensive profile update for user: {self.test_user['username']}")

        # Update profile data with all fields
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Profile',
            'email': f'updated_{uuid.uuid4().hex[:8]}@example.com',
            'phone': '9876543210',
            'date_of_birth': '1985-06-15'
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        if response.status_code == 200:
            data = response.json()
            assert 'success' in data or 'user' in data
            print("  ✅ Comprehensive profile update successful")
            return data
        else:
            print(f"  ❌ Profile update failed: {response.status_code}")
            print(f"  Response: {response.text}")
            raise AssertionError(f"Profile update failed with status {response.status_code}")

    def test_profile_update_partial(self):
        """Test profile update with only some fields"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping partial update test - no access token")
            return

        print(f"  ✏️  Testing partial profile update for user: {self.test_user['username']}")

        # Update only first name
        update_data = {
            'first_name': 'Partial'
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        if response.status_code == 200:
            data = response.json()
            assert 'success' in data or 'user' in data
            print("  ✅ Partial profile update successful")
        else:
            print(f"  ❌ Partial profile update failed: {response.status_code}")
            print(f"  Response: {response.text}")
            raise AssertionError(f"Partial profile update failed with status {response.status_code}")

    def test_profile_update_empty_fields(self):
        """Test profile update with empty string fields (should be rejected)"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping empty fields test - no access token")
            return

        print(f"  🚫 Testing profile update with empty fields for user: {self.test_user['username']}")

        # Try to update with empty strings
        update_data = {
            'first_name': '',
            'last_name': '',
            'email': ''
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
        print("  ✅ Empty fields correctly rejected")

    def test_profile_update_whitespace_only(self):
        """Test profile update with whitespace-only fields (should be rejected)"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping whitespace test - no access token")
            return

        print(f"  🚫 Testing profile update with whitespace-only fields for user: {self.test_user['username']}")

        # Try to update with whitespace-only strings
        update_data = {
            'first_name': '   ',
            'last_name': '   ',
            'email': '   '
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
        print("  ✅ Whitespace-only fields correctly rejected")

    # First Name Validation Tests
    def test_profile_update_first_name_too_short(self):
        """Test profile update with first name too short (< 1 char)"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping first name test - no access token")
            return

        print(f"  🚫 Testing profile update with first name too short for user: {self.test_user['username']}")

        update_data = {
            'first_name': ''  # Too short
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ First name too short correctly rejected")

    def test_profile_update_first_name_too_long(self):
        """Test profile update with first name too long (> 50 chars)"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping first name test - no access token")
            return

        print(f"  🚫 Testing profile update with first name too long for user: {self.test_user['username']}")

        update_data = {
            'first_name': 'A' * 51  # Too long
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ First name too long correctly rejected")

    def test_profile_update_first_name_invalid_chars(self):
        """Test profile update with first name containing invalid characters"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping first name test - no access token")
            return

        print(f"  🚫 Testing profile update with first name containing invalid chars for user: {self.test_user['username']}")

        update_data = {
            'first_name': 'John@123'  # Contains @ and numbers
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ First name with invalid chars correctly rejected")

    def test_profile_update_first_name_suspicious_content(self):
        """Test profile update with first name containing suspicious content"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping first name test - no access token")
            return

        print(f"  🚫 Testing profile update with first name containing suspicious content for user: {self.test_user['username']}")

        update_data = {
            'first_name': '<script>alert("xss")</script>'  # XSS attempt
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ First name with suspicious content correctly rejected")

    # Last Name Validation Tests
    def test_profile_update_last_name_too_short(self):
        """Test profile update with last name too short (< 1 char)"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping last name test - no access token")
            return

        print(f"  🚫 Testing profile update with last name too short for user: {self.test_user['username']}")

        update_data = {
            'last_name': ''  # Too short
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Last name too short correctly rejected")

    def test_profile_update_last_name_too_long(self):
        """Test profile update with last name too long (> 50 chars)"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping last name test - no access token")
            return

        print(f"  🚫 Testing profile update with last name too long for user: {self.test_user['username']}")

        update_data = {
            'last_name': 'A' * 51  # Too long
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Last name too long correctly rejected")

    def test_profile_update_last_name_invalid_chars(self):
        """Test profile update with last name containing invalid characters"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping last name test - no access token")
            return

        print(f"  🚫 Testing profile update with last name containing invalid chars for user: {self.test_user['username']}")

        update_data = {
            'last_name': 'Doe@123'  # Contains @ and numbers
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Last name with invalid chars correctly rejected")

    # Email Validation Tests
    def test_profile_update_email_invalid_format(self):
        """Test profile update with invalid email format"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping email test - no access token")
            return

        print(f"  🚫 Testing profile update with invalid email format for user: {self.test_user['username']}")

        update_data = {
            'email': 'invalid-email'  # Invalid format
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Invalid email format correctly rejected")

    def test_profile_update_email_suspicious_content(self):
        """Test profile update with email containing suspicious content"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping email test - no access token")
            return

        print(f"  🚫 Testing profile update with email containing suspicious content for user: {self.test_user['username']}")

        update_data = {
            'email': '<script>alert("xss")</script>@example.com'  # XSS attempt
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Email with suspicious content correctly rejected")

    # Phone Validation Tests
    def test_profile_update_phone_too_short(self):
        """Test profile update with phone number too short (< 10 digits)"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping phone test - no access token")
            return

        print(f"  🚫 Testing profile update with phone number too short for user: {self.test_user['username']}")

        update_data = {
            'phone': '123456789'  # Too short (9 digits)
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Phone number too short correctly rejected")

    def test_profile_update_phone_too_long(self):
        """Test profile update with phone number too long (> 15 digits)"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping phone test - no access token")
            return

        print(f"  🚫 Testing profile update with phone number too long for user: {self.test_user['username']}")

        update_data = {
            'phone': '1234567890123456'  # Too long (16 digits)
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Phone number too long correctly rejected")

    def test_profile_update_phone_formatted_success(self):
        """Test profile update with formatted phone number (should succeed and be sanitized)"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping phone test - no access token")
            return

        print(f"  ✅ Testing profile update with formatted phone number for user: {self.test_user['username']}")

        update_data = {
            'phone': '123-456-7890'  # Contains hyphens - should be sanitized to digits
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
        print("  ✅ Formatted phone number correctly accepted and sanitized")

    def test_profile_update_phone_suspicious_content(self):
        """Test profile update with phone number containing suspicious content"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping phone test - no access token")
            return

        print(f"  🚫 Testing profile update with phone number containing suspicious content for user: {self.test_user['username']}")

        update_data = {
            'phone': '<script>alert("xss")</script>123-456-7890'  # XSS attempt
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Phone number with suspicious content correctly rejected")

    # Date of Birth Validation Tests
    def test_profile_update_dob_future_date(self):
        """Test profile update with future date of birth"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping DOB test - no access token")
            return

        print(f"  🚫 Testing profile update with future date of birth for user: {self.test_user['username']}")

        # Set future date
        future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')

        update_data = {
            'date_of_birth': future_date
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Future date of birth correctly rejected")

    def test_profile_update_dob_invalid_format(self):
        """Test profile update with invalid date of birth format"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping DOB test - no access token")
            return

        print(f"  🚫 Testing profile update with invalid date of birth format for user: {self.test_user['username']}")

        update_data = {
            'date_of_birth': '1990/01/01'  # Invalid format (should be YYYY-MM-DD)
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Invalid date of birth format correctly rejected")

    # Edge Cases
    def test_profile_update_with_null_values(self):
        """Test profile update with null values (should succeed as fields are optional)"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping null values test - no access token")
            return

        print(f"  ✅ Testing profile update with null values for user: {self.test_user['username']}")

        update_data = {
            'first_name': None,
            'last_name': None,
            'email': None
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
        print("  ✅ Null values correctly accepted (fields are optional)")

    def test_profile_update_with_very_long_inputs(self):
        """Test profile update with extremely long inputs"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping long inputs test - no access token")
            return

        print(f"  🚫 Testing profile update with very long inputs for user: {self.test_user['username']}")

        update_data = {
            'first_name': 'A' * 1000,  # Very long
            'last_name': 'B' * 1000,   # Very long
            'email': f'{"very_long_email_" + "a" * 1000}@example.com'  # Very long
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Very long inputs correctly rejected")

    def test_profile_update_with_special_characters(self):
        """Test profile update with special characters"""
        self.setup_test_user()

        if not self.access_token:
            print("  ⚠️  Skipping special chars test - no access token")
            return

        print(f"  🚫 Testing profile update with special characters for user: {self.test_user['username']}")

        update_data = {
            'first_name': 'John!@#$%^&*()',
            'last_name': 'Doe!@#$%^&*()',
            'email': 'john!@#$%^&*()@example.com'
        }

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = self.session.put(
            self.user_api(UserAPI.PROFILE),
            headers=headers,
            json=update_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Special characters correctly rejected")

    def run_all_profile_tests(self):
        """Run all user profile tests"""
        print("👤 Running comprehensive user profile integration tests...")
        print(f"🎯 Service URL: {APIEndpoints.get_user_endpoint(UserAPI.PROFILE)}")

        try:
            # GET Profile Tests
            print("\n📋 === GET PROFILE TESTS ===")
            self.test_profile_unauthorized()
            print("  ✅ Profile (Unauthorized) - PASS")

            self.test_profile_invalid_token()
            print("  ✅ Profile (Invalid Token) - PASS")

            self.test_profile_malformed_token()
            print("  ✅ Profile (Malformed Token) - PASS")

            self.test_profile_authorized()
            print("  ✅ Profile (Authorized) - PASS")

            self.test_profile_authorized_case_insensitive_username()
            print("  ✅ Profile (Case-Insensitive Username) - PASS")

            # PUT Profile Update Tests
            print("\n📋 === PROFILE UPDATE TESTS ===")
            self.test_profile_update_success()
            print("  ✅ Profile Update (Success) - PASS")

            self.test_profile_update_partial()
            print("  ✅ Profile Update (Partial) - PASS")

            self.test_profile_update_empty_fields()
            print("  ✅ Profile Update (Empty Fields) - PASS")

            self.test_profile_update_whitespace_only()
            print("  ✅ Profile Update (Whitespace Only) - PASS")

            # First Name Validation
            print("\n📋 === FIRST NAME VALIDATION ===")
            self.test_profile_update_first_name_too_short()
            print("  ✅ First Name Too Short - PASS")

            self.test_profile_update_first_name_too_long()
            print("  ✅ First Name Too Long - PASS")

            self.test_profile_update_first_name_invalid_chars()
            print("  ✅ First Name Invalid Chars - PASS")

            self.test_profile_update_first_name_suspicious_content()
            print("  ✅ First Name Suspicious Content - PASS")

            # Last Name Validation
            print("\n📋 === LAST NAME VALIDATION ===")
            self.test_profile_update_last_name_too_short()
            print("  ✅ Last Name Too Short - PASS")

            self.test_profile_update_last_name_too_long()
            print("  ✅ Last Name Too Long - PASS")

            self.test_profile_update_last_name_invalid_chars()
            print("  ✅ Last Name Invalid Chars - PASS")

            # Email Validation
            print("\n📋 === EMAIL VALIDATION ===")
            self.test_profile_update_email_invalid_format()
            print("  ✅ Email Invalid Format - PASS")

            self.test_profile_update_email_suspicious_content()
            print("  ✅ Email Suspicious Content - PASS")

                        # Phone Validation
            print("\n📋 === PHONE VALIDATION ===")
            self.test_profile_update_phone_too_short()
            print("  ✅ Phone Too Short - PASS")

            self.test_profile_update_phone_too_long()
            print("  ✅ Phone Too Long - PASS")

            self.test_profile_update_phone_formatted_success()
            print("  ✅ Phone Formatted Success - PASS")

            self.test_profile_update_phone_suspicious_content()
            print("  ✅ Phone Suspicious Content - PASS")

            # Date of Birth Validation
            print("\n📋 === DATE OF BIRTH VALIDATION ===")
            self.test_profile_update_dob_future_date()
            print("  ✅ DOB Future Date - PASS")

            self.test_profile_update_dob_invalid_format()
            print("  ✅ DOB Invalid Format - PASS")

            # Edge Cases
            print("\n📋 === EDGE CASES ===")
            self.test_profile_update_with_null_values()
            print("  ✅ Null Values - PASS")

            self.test_profile_update_with_very_long_inputs()
            print("  ✅ Very Long Inputs - PASS")

            self.test_profile_update_with_special_characters()
            print("  ✅ Special Characters - PASS")

            print("\n  🎉 All user profile tests completed successfully!")

        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            raise

if __name__ == "__main__":
    # Run user profile tests
    tests = UserProfileTests()
    tests.run_all_profile_tests()
    print("All user profile integration tests completed successfully!")
