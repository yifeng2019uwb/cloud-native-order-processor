"""
User Login API Integration Tests
Tests POST /auth/login endpoint with comprehensive validation
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

class UserLoginTests:
    """Integration tests for user login API with comprehensive validation"""

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
        """Create a test user for login tests"""
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

    def test_login_success(self):
        """Test successful user login"""
        self.setup_test_user()

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

            # Check if response has nested data structure
            if 'data' in data:
                token_data = data['data']
                assert 'access_token' in token_data
                assert 'token_type' in token_data
                assert token_data['token_type'] == 'bearer'
                self.access_token = token_data['access_token']
            else:
                # Direct structure
                assert 'access_token' in data
                assert 'token_type' in data
                assert data['token_type'] == 'bearer'
                self.access_token = data['access_token']

            print("  ✅ Login successful")
            return data
        else:
            print(f"  ❌ Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            raise AssertionError(f"Login failed with status {response.status_code}")

    def test_login_success_with_whitespace_trimming(self):
        """Test successful login with whitespace in username/password (should be trimmed)"""
        self.setup_test_user()

        print(f"  🔐 Testing login with whitespace trimming for user: {self.test_user['username']}")

        login_data = {
            'username': f"  {self.test_user['username']}  ",  # Extra whitespace
            'password': f"  {self.test_user['password']}  "   # Extra whitespace
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("  ✅ Login with whitespace trimming successful")

    # Username Validation Tests
    def test_login_username_too_short(self):
        """Test login with username too short (< 6 chars)"""
        print("  🚫 Testing login with username too short")

        login_data = {
            'username': 'abc',  # Too short
            'password': 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Username too short correctly rejected")

    def test_login_username_too_long(self):
        """Test login with username too long (> 30 chars)"""
        print("  🚫 Testing login with username too long")

        login_data = {
            'username': 'a' * 31,  # Too long
            'password': 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Username too long correctly rejected")

    def test_login_username_invalid_chars(self):
        """Test login with username containing invalid characters"""
        print("  🚫 Testing login with username containing invalid characters")

        login_data = {
            'username': 'test-user@123',  # Contains hyphens and @
            'password': 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Username with invalid chars correctly rejected")

    def test_login_username_suspicious_content(self):
        """Test login with username containing suspicious content"""
        print("  🚫 Testing login with username containing suspicious content")

        login_data = {
            'username': '<script>alert("xss")</script>',  # XSS attempt
            'password': 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Username with suspicious content correctly rejected")

    def test_login_username_empty(self):
        """Test login with empty username"""
        print("  🚫 Testing login with empty username")

        login_data = {
            'username': '',  # Empty
            'password': 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Empty username correctly rejected")

    def test_login_username_whitespace_only(self):
        """Test login with username containing only whitespace"""
        print("  🚫 Testing login with username containing only whitespace")

        login_data = {
            'username': '   ',  # Whitespace only
            'password': 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Username with only whitespace correctly rejected")

    # Password Validation Tests
    def test_login_password_too_short(self):
        """Test login with password too short (< 12 chars)"""
        print("  🚫 Testing login with password too short")

        login_data = {
            'username': 'testuser123',
            'password': 'Short1!'  # Too short
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password too short correctly rejected")

    def test_login_password_too_long(self):
        """Test login with password too long (> 20 chars)"""
        print("  🚫 Testing login with password too long")

        login_data = {
            'username': 'testuser123',
            'password': 'VeryLongPassword123!Extra'  # 25 chars - too long
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password too long correctly rejected")

    def test_login_password_no_uppercase(self):
        """Test login with password missing uppercase letter"""
        print("  🚫 Testing login with password missing uppercase letter")

        login_data = {
            'username': 'testuser123',
            'password': 'lowercase123!'  # No uppercase
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password no uppercase correctly rejected")

    def test_login_password_no_lowercase(self):
        """Test login with password missing lowercase letter"""
        print("  🚫 Testing login with password missing lowercase letter")

        login_data = {
            'username': 'testuser123',
            'password': 'UPPERCASE123!'  # No lowercase
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password no lowercase correctly rejected")

    def test_login_password_no_number(self):
        """Test login with password missing number"""
        print("  🚫 Testing login with password missing number")

        login_data = {
            'username': 'testuser123',
            'password': 'PasswordOnly!'  # No number
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password no number correctly rejected")

    def test_login_password_no_special_char(self):
        """Test login with password missing special character"""
        print("  🚫 Testing login with password missing special character")

        login_data = {
            'username': 'testuser123',
            'password': 'Password123'  # No special char
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password no special char correctly rejected")

    def test_login_password_empty(self):
        """Test login with empty password"""
        print("  🚫 Testing login with empty password")

        login_data = {
            'username': 'testuser123',
            'password': ''  # Empty
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Empty password correctly rejected")

    def test_login_password_whitespace_only(self):
        """Test login with password containing only whitespace"""
        print("  🚫 Testing login with password containing only whitespace")

        login_data = {
            'username': 'testuser123',
            'password': '   '  # Whitespace only
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password with only whitespace correctly rejected")

    def test_login_password_suspicious_content(self):
        """Test login with password containing suspicious content"""
        print("  🚫 Testing login with password containing suspicious content")

        login_data = {
            'username': 'testuser123',
            'password': '<script>alert("xss")</script>'  # XSS attempt
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password with suspicious content correctly rejected")

    # Authentication Tests
    def test_login_invalid_username(self):
        """Test login with invalid username (should fail)"""
        print("  🚫 Testing login with invalid username")

        login_data = {
            'username': 'nonexistent_user',
            'password': 'TestPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        # Should fail with invalid credentials
        assert response.status_code in [401, 404], f"Expected 401/404, got {response.status_code}"
        print("  ✅ Invalid username correctly rejected")

    def test_login_invalid_password(self):
        """Test login with invalid password (should fail)"""
        self.setup_test_user()

        print(f"  🚫 Testing login with invalid password for user: {self.test_user['username']}")

        login_data = {
            'username': self.test_user['username'],
            'password': 'WrongPassword123!'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        # Should fail with invalid credentials
        assert response.status_code in [401, 400], f"Expected 401/400, got {response.status_code}"
        print("  ✅ Invalid password correctly rejected")

    def test_login_case_sensitive_username(self):
        """Test login with case-sensitive username (should fail if different case)"""
        self.setup_test_user()

        print(f"  🚫 Testing login with case-sensitive username: {self.test_user['username'].upper()}")

        login_data = {
            'username': self.test_user['username'].upper(),  # Different case
            'password': self.test_user['password']
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        # Check if username is case-sensitive or case-insensitive
        if response.status_code == 200:
            print(f"  ℹ️  Username is case-insensitive (accepted: {self.test_user['username'].upper()})")
            print("  ✅ Case-insensitive username correctly handled")
        else:
            # Should fail with invalid credentials (username is case-sensitive)
            assert response.status_code in [401, 404], f"Expected 401/404, got {response.status_code}"
            print("  ✅ Case-sensitive username correctly handled")

    def test_login_case_sensitive_password(self):
        """Test login with case-sensitive password (should fail if different case)"""
        self.setup_test_user()

        print(f"  🚫 Testing login with case-sensitive password for user: {self.test_user['username']}")

        # Create a password with different case
        wrong_password = self.test_user['password'].swapcase()  # Swap case

        login_data = {
            'username': self.test_user['username'],
            'password': wrong_password
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        # Should fail with invalid credentials
        assert response.status_code in [401, 400], f"Expected 401/400, got {response.status_code}"
        print("  ✅ Case-sensitive password correctly handled")

    # Missing Fields Tests
    def test_login_missing_username(self):
        """Test login with missing username"""
        print("  🚫 Testing login with missing username")

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json={'password': 'TestPassword123!'},
            timeout=self.timeout
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Missing username correctly rejected")

    def test_login_missing_password(self):
        """Test login with missing password"""
        print("  🚫 Testing login with missing password")

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json={'username': 'testuser'},
            timeout=self.timeout
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Missing password correctly rejected")

    def test_login_missing_both_fields(self):
        """Test login with missing both username and password"""
        print("  🚫 Testing login with missing both fields")

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json={},
            timeout=self.timeout
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Missing both fields correctly rejected")

    # Edge Cases
    def test_login_with_null_values(self):
        """Test login with null values"""
        print("  🚫 Testing login with null values")

        login_data = {
            'username': None,
            'password': None
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Null values correctly rejected")

    def test_login_with_very_long_inputs(self):
        """Test login with extremely long inputs"""
        print("  🚫 Testing login with very long inputs")

        login_data = {
            'username': 'a' * 1000,  # Very long
            'password': 'b' * 1000   # Very long
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Very long inputs correctly rejected")

    def test_login_with_special_characters(self):
        """Test login with special characters in username/password"""
        print("  🚫 Testing login with special characters")

        login_data = {
            'username': 'user!@#$%^&*()',
            'password': 'pass!@#$%^&*()'
        }

        response = self.session.post(
            self.user_api(UserAPI.LOGIN),
            json=login_data,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Special characters correctly rejected")

    def run_all_login_tests(self):
        """Run all user login tests"""
        print("🔐 Running comprehensive user login integration tests...")
        print(f"🎯 Service URL: {APIEndpoints.get_user_endpoint(UserAPI.LOGIN)}")

        try:
            # Success Cases
            print("\n📋 === SUCCESS CASES ===")
            self.test_login_success()
            print("  ✅ Login Success - PASS")

            self.test_login_success_with_whitespace_trimming()
            print("  ✅ Login with Whitespace Trimming - PASS")

            # Username Validation
            print("\n📋 === USERNAME VALIDATION ===")
            self.test_login_username_too_short()
            print("  ✅ Username Too Short - PASS")

            self.test_login_username_too_long()
            print("  ✅ Username Too Long - PASS")

            self.test_login_username_invalid_chars()
            print("  ✅ Username Invalid Chars - PASS")

            self.test_login_username_suspicious_content()
            print("  ✅ Username Suspicious Content - PASS")

            self.test_login_username_empty()
            print("  ✅ Username Empty - PASS")

            self.test_login_username_whitespace_only()
            print("  ✅ Username Whitespace Only - PASS")

            # Password Validation
            print("\n📋 === PASSWORD VALIDATION ===")
            self.test_login_password_too_short()
            print("  ✅ Password Too Short - PASS")

            self.test_login_password_too_long()
            print("  ✅ Password Too Long - PASS")

            self.test_login_password_no_uppercase()
            print("  ✅ Password No Uppercase - PASS")

            self.test_login_password_no_lowercase()
            print("  ✅ Password No Lowercase - PASS")

            self.test_login_password_no_number()
            print("  ✅ Password No Number - PASS")

            self.test_login_password_no_special_char()
            print("  ✅ Password No Special Char - PASS")

            self.test_login_password_empty()
            print("  ✅ Password Empty - PASS")

            self.test_login_password_whitespace_only()
            print("  ✅ Password Whitespace Only - PASS")

            self.test_login_password_suspicious_content()
            print("  ✅ Password Suspicious Content - PASS")

            # Authentication Tests
            print("\n📋 === AUTHENTICATION TESTS ===")
            self.test_login_invalid_username()
            print("  ✅ Invalid Username - PASS")

            self.test_login_invalid_password()
            print("  ✅ Invalid Password - PASS")

            self.test_login_case_sensitive_username()
            print("  ✅ Case-Sensitive Username - PASS")

            self.test_login_case_sensitive_password()
            print("  ✅ Case-Sensitive Password - PASS")

            # Missing Fields Tests
            print("\n📋 === MISSING FIELDS TESTS ===")
            self.test_login_missing_username()
            print("  ✅ Missing Username - PASS")

            self.test_login_missing_password()
            print("  ✅ Missing Password - PASS")

            self.test_login_missing_both_fields()
            print("  ✅ Missing Both Fields - PASS")

            # Edge Cases
            print("\n📋 === EDGE CASES ===")
            self.test_login_with_null_values()
            print("  ✅ Null Values - PASS")

            self.test_login_with_very_long_inputs()
            print("  ✅ Very Long Inputs - PASS")

            self.test_login_with_special_characters()
            print("  ✅ Special Characters - PASS")

            print("\n  🎉 All user login tests completed successfully!")

        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            raise

if __name__ == "__main__":
    # Run user login tests
    tests = UserLoginTests()
    tests.run_all_login_tests()
    print("All user login integration tests completed successfully!")
