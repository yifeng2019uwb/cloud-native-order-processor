"""
User Registration API Integration Tests
Tests POST /auth/register endpoint with comprehensive validation
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

class UserRegistrationTests:
    """Integration tests for user registration API with comprehensive validation"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.test_data_manager = TestDataManager()

    def user_api(self, api: UserAPI) -> str:
        """Helper method to get complete user service API URLs"""
        return APIEndpoints.get_user_endpoint(api)

    def test_registration_success(self):
        """Test successful user registration with all fields"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Integration',
            'last_name': 'Test',
            'phone': '1234567890',
            'date_of_birth': '1990-01-01',
            'marketing_emails_consent': True
        }

        print(f"  📝 Testing registration with user: {test_user['username']}")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        if response.status_code in [200, 201]:
            data = response.json()
            assert 'success' in data
            assert data['success'] == True
            print("  ✅ Registration successful")
            return test_user
        else:
            print(f"  ❌ Registration failed: {response.status_code}")
            print(f"  Response: {response.text}")
            raise AssertionError(f"Registration failed with status {response.status_code}")

    def test_registration_minimal_success(self):
        """Test successful user registration with only required fields"""
        test_user = {
            'username': f'minuser_{uuid.uuid4().hex[:8]}',
            'email': f'min_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'MinPassword123!',
            'first_name': 'Minimal',
            'last_name': 'User'
        }

        print(f"  📝 Testing minimal registration with user: {test_user['username']}")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        data = response.json()
        assert data['success'] == True
        print("  ✅ Minimal registration successful")

    def test_registration_duplicate_username(self):
        """Test registration with duplicate username (should fail)"""
        # First, create a user
        test_user = self.test_registration_success()

        # Try to register again with same username
        duplicate_user = test_user.copy()
        duplicate_user['email'] = f'duplicate_{uuid.uuid4().hex[:8]}@example.com'

        print(f"  🔄 Testing duplicate username: {duplicate_user['username']}")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=duplicate_user,
            timeout=self.timeout
        )

        # Should fail with duplicate username error
        assert response.status_code in [400, 409], f"Expected 400/409, got {response.status_code}"
        print("  ✅ Duplicate username correctly rejected")

    def test_registration_duplicate_email(self):
        """Test registration with duplicate email (should fail)"""
        # First, create a user
        test_user = self.test_registration_success()

        # Try to register again with same email
        duplicate_user = test_user.copy()
        duplicate_user['username'] = f'duplicate_{uuid.uuid4().hex[:8]}'

        print(f"  🔄 Testing duplicate email: {duplicate_user['email']}")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=duplicate_user,
            timeout=self.timeout
        )

        # Should fail with duplicate email error
        assert response.status_code in [400, 409], f"Expected 400/409, got {response.status_code}"
        print("  ✅ Duplicate email correctly rejected")

    # Username Validation Tests
    def test_registration_username_too_short(self):
        """Test registration with username too short (< 6 chars)"""
        test_user = {
            'username': 'abc',  # Too short
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing username too short: '{test_user['username']}'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Username too short correctly rejected")

    def test_registration_username_too_long(self):
        """Test registration with username too long (> 30 chars)"""
        test_user = {
            'username': 'a' * 31,  # Too long
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing username too long: '{test_user['username'][:10]}...'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Username too long correctly rejected")

    def test_registration_username_invalid_chars(self):
        """Test registration with username containing invalid characters"""
        test_user = {
            'username': 'test-user@123',  # Contains hyphens and @
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing username with invalid chars: '{test_user['username']}'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Username with invalid chars correctly rejected")

    def test_registration_username_suspicious_content(self):
        """Test registration with username containing suspicious content"""
        test_user = {
            'username': '<script>alert("xss")</script>',  # XSS attempt
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing username with suspicious content: '{test_user['username'][:20]}...'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Username with suspicious content correctly rejected")

    # Email Validation Tests
    def test_registration_email_invalid_format(self):
        """Test registration with invalid email format"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': 'invalid-email',  # Invalid format
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing invalid email format: '{test_user['email']}'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Invalid email format correctly rejected")

    def test_registration_email_suspicious_content(self):
        """Test registration with email containing suspicious content"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': '<script>alert("xss")</script>@example.com',  # XSS attempt
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing email with suspicious content: '{test_user['email'][:20]}...'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Email with suspicious content correctly rejected")

    # Password Validation Tests
    def test_registration_password_too_short(self):
        """Test registration with password too short (< 12 chars)"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'Short1!',  # Too short
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing password too short: '{test_user['password']}'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password too short correctly rejected")

    def test_registration_password_too_long(self):
        """Test registration with password too long (> 20 chars)"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'VeryLongPassword123!Extra',  # 25 chars - too long
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing password too long: '{test_user['password']}'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password too long correctly rejected")

    def test_registration_password_no_uppercase(self):
        """Test registration with password missing uppercase letter"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'lowercase123!',  # No uppercase
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing password no uppercase: '{test_user['password']}'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password no uppercase correctly rejected")

    def test_registration_password_no_lowercase(self):
        """Test registration with password missing lowercase letter"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'UPPERCASE123!',  # No lowercase
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing password no lowercase: '{test_user['password']}'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password no lowercase correctly rejected")

    def test_registration_password_no_number(self):
        """Test registration with password missing number"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'PasswordOnly!',  # No number
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing password no number: '{test_user['password']}'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password no number correctly rejected")

    def test_registration_password_no_special_char(self):
        """Test registration with password missing special character"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'Password123',  # No special char
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing password no special char: '{test_user['password']}'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Password no special char correctly rejected")

    # Name Validation Tests
    def test_registration_name_invalid_chars(self):
        """Test registration with name containing invalid characters"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test123',  # Contains numbers
            'last_name': 'User'
        }

        print(f"  🚫 Testing first name with invalid chars: '{test_user['first_name']}'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ First name with invalid chars correctly rejected")

    def test_registration_name_suspicious_content(self):
        """Test registration with name containing suspicious content"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': '<script>alert("xss")</script>',  # XSS attempt
            'last_name': 'User'
        }

        print(f"  🚫 Testing first name with suspicious content: '{test_user['first_name'][:20]}...'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ First name with suspicious content correctly rejected")

    # Phone Validation Tests
    def test_registration_phone_invalid_format(self):
        """Test registration with invalid phone format"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '123'  # Too short
        }

        print(f"  🚫 Testing invalid phone format: '{test_user['phone']}'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Invalid phone format correctly rejected")

    def test_registration_phone_too_long(self):
        """Test registration with phone too long"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1' * 20  # Too long
        }

        print(f"  🚫 Testing phone too long: '{test_user['phone'][:10]}...'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Phone too long correctly rejected")

    # Date of Birth Validation Tests
    def test_registration_dob_too_young(self):
        """Test registration with date of birth making user too young (< 13)"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': '2020-01-01'  # Too young
        }

        print(f"  🚫 Testing DOB too young: '{test_user['date_of_birth']}'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ DOB too young correctly rejected")

    def test_registration_dob_future_date(self):
        """Test registration with future date of birth"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': '2030-01-01'  # Future date
        }

        print(f"  🚫 Testing future DOB: '{test_user['date_of_birth']}'")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Future DOB correctly rejected")

    # Missing Required Fields Tests
    def test_registration_missing_username(self):
        """Test registration with missing username"""
        test_user = {
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing missing username")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Missing username correctly rejected")

    def test_registration_missing_email(self):
        """Test registration with missing email"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing missing email")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Missing email correctly rejected")

    def test_registration_missing_password(self):
        """Test registration with missing password"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }

        print(f"  🚫 Testing missing password")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Missing password correctly rejected")

    def test_registration_missing_first_name(self):
        """Test registration with missing first name"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'last_name': 'User'
        }

        print(f"  🚫 Testing missing first name")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Missing first name correctly rejected")

    def test_registration_missing_last_name(self):
        """Test registration with missing last name"""
        test_user = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test'
        }

        print(f"  🚫 Testing missing last name")

        response = self.session.post(
            self.user_api(UserAPI.REGISTER),
            json=test_user,
            timeout=self.timeout
        )

        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print("  ✅ Missing last name correctly rejected")

    def run_all_registration_tests(self):
        """Run all user registration tests"""
        print("👤 Running comprehensive user registration integration tests...")
        print(f"🎯 Service URL: {APIEndpoints.get_user_endpoint(UserAPI.REGISTER)}")

        try:
            # Success Cases
            print("\n📋 === SUCCESS CASES ===")
            self.test_registration_success()
            print("  ✅ Registration Success - PASS")

            self.test_registration_minimal_success()
            print("  ✅ Minimal Registration Success - PASS")

            # Duplicate Cases
            print("\n📋 === DUPLICATE CASES ===")
            self.test_registration_duplicate_username()
            print("  ✅ Duplicate Username - PASS")

            self.test_registration_duplicate_email()
            print("  ✅ Duplicate Email - PASS")

            # Username Validation
            print("\n📋 === USERNAME VALIDATION ===")
            self.test_registration_username_too_short()
            print("  ✅ Username Too Short - PASS")

            self.test_registration_username_too_long()
            print("  ✅ Username Too Long - PASS")

            self.test_registration_username_invalid_chars()
            print("  ✅ Username Invalid Chars - PASS")

            self.test_registration_username_suspicious_content()
            print("  ✅ Username Suspicious Content - PASS")

            # Email Validation
            print("\n📋 === EMAIL VALIDATION ===")
            self.test_registration_email_invalid_format()
            print("  ✅ Email Invalid Format - PASS")

            self.test_registration_email_suspicious_content()
            print("  ✅ Email Suspicious Content - PASS")

            # Password Validation
            print("\n📋 === PASSWORD VALIDATION ===")
            self.test_registration_password_too_short()
            print("  ✅ Password Too Short - PASS")

            self.test_registration_password_too_long()
            print("  ✅ Password Too Long - PASS")

            self.test_registration_password_no_uppercase()
            print("  ✅ Password No Uppercase - PASS")

            self.test_registration_password_no_lowercase()
            print("  ✅ Password No Lowercase - PASS")

            self.test_registration_password_no_number()
            print("  ✅ Password No Number - PASS")

            self.test_registration_password_no_special_char()
            print("  ✅ Password No Special Char - PASS")

            # Name Validation
            print("\n📋 === NAME VALIDATION ===")
            self.test_registration_name_invalid_chars()
            print("  ✅ Name Invalid Chars - PASS")

            self.test_registration_name_suspicious_content()
            print("  ✅ Name Suspicious Content - PASS")

            # Phone Validation
            print("\n📋 === PHONE VALIDATION ===")
            self.test_registration_phone_invalid_format()
            print("  ✅ Phone Invalid Format - PASS")

            self.test_registration_phone_too_long()
            print("  ✅ Phone Too Long - PASS")

            # Date of Birth Validation
            print("\n📋 === DATE OF BIRTH VALIDATION ===")
            self.test_registration_dob_too_young()
            print("  ✅ DOB Too Young - PASS")

            self.test_registration_dob_future_date()
            print("  ✅ DOB Future Date - PASS")

            # Missing Required Fields
            print("\n📋 === MISSING REQUIRED FIELDS ===")
            self.test_registration_missing_username()
            print("  ✅ Missing Username - PASS")

            self.test_registration_missing_email()
            print("  ✅ Missing Email - PASS")

            self.test_registration_missing_password()
            print("  ✅ Missing Password - PASS")

            self.test_registration_missing_first_name()
            print("  ✅ Missing First Name - PASS")

            self.test_registration_missing_last_name()
            print("  ✅ Missing Last Name - PASS")

            print("\n  🎉 All user registration tests completed successfully!")

        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            raise

if __name__ == "__main__":
    # Run user registration tests
    tests = UserRegistrationTests()
    tests.run_all_registration_tests()
    print("All user registration integration tests completed successfully!")
