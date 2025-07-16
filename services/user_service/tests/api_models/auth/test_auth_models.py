import pytest
from pydantic import ValidationError
from api_models.auth.login import UserLoginRequest, LoginSuccessResponse, LoginErrorResponse
from api_models.auth.registration import UserRegistrationRequest, RegistrationSuccessResponse
from api_models.auth.profile import UserProfileResponse
from api_models.auth.logout import LogoutSuccessResponse, LogoutErrorResponse


class TestAuthModels:
    """Test authentication API models"""

    def test_user_login_request_valid(self):
        """Test valid login request"""
        login_data = {
            "username": "testuser",
            "password": "testpass123456"
        }
        login_request = UserLoginRequest(**login_data)

        assert login_request.username == "testuser"
        assert login_request.password == "testpass123456"

    def test_user_login_request_invalid_short_password(self):
        """Test invalid login request with short password"""
        with pytest.raises(ValidationError):
            UserLoginRequest(username="testuser", password="short")

    def test_user_login_request_invalid_empty_username(self):
        """Test invalid login request with empty username"""
        with pytest.raises(ValidationError):
            UserLoginRequest(username="", password="testpass123456")

    def test_login_success_response_valid(self):
        """Test valid login success response"""
        response_data = {
            "success": True,
            "message": "Login successful",
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 86400,
            "user": {
                "username": "testuser",
                "email": "testuser@example.com",
                "first_name": "Test",
                "last_name": "User",
                "marketing_emails_consent": False,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            },
            "timestamp": "2025-01-01T00:00:00Z"
        }
        response = LoginSuccessResponse(**response_data)

        assert response.success is True
        assert response.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert response.token_type == "bearer"
        assert response.user.username == "testuser"

    def test_login_error_response_valid(self):
        """Test valid login error response"""
        error_data = {
            "success": False,
            "error": "AUTHENTICATION_FAILED",
            "message": "Invalid credentials",
            "timestamp": "2025-01-01T00:00:00Z"
        }
        response = LoginErrorResponse(**error_data)

        assert response.success is False
        assert response.error == "AUTHENTICATION_FAILED"
        assert response.message == "Invalid credentials"

    def test_logout_success_response_valid(self):
        """Test valid logout success response"""
        logout_data = {
            "success": True,
            "message": "Logged out successfully",
            "timestamp": "2025-01-01T00:00:00Z"
        }
        response = LogoutSuccessResponse(**logout_data)

        assert response.success is True
        assert response.message == "Logged out successfully"

    def test_logout_error_response_valid(self):
        """Test valid logout error response"""
        error_data = {
            "success": False,
            "error": "LOGOUT_FAILED",
            "message": "Logout failed. Please try again.",
            "timestamp": "2025-01-01T00:00:00Z"
        }
        response = LogoutErrorResponse(**error_data)

        assert response.success is False
        assert response.error == "LOGOUT_FAILED"
        assert response.message == "Logout failed. Please try again."


class TestRegistrationModels:
    """Test registration API models and validators"""

    def test_user_registration_request_valid(self):
        data = {
            "username": "valid_user",
            "email": "valid@example.com",
            "password": "ValidPass123!@#",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1-555-123-4567",
            "date_of_birth": "2000-01-01",
            "marketing_emails_consent": True
        }
        req = UserRegistrationRequest(**data)
        assert req.username == "valid_user"
        assert req.email == "valid@example.com"
        assert req.password == "ValidPass123!@#"
        assert req.first_name == "John"
        assert req.last_name == "Doe"
        assert req.phone == "+1-555-123-4567"
        assert req.date_of_birth.isoformat() == "2000-01-01"
        assert req.marketing_emails_consent is True

    @pytest.mark.parametrize("username", [
        "_badstart", "badend_", "bad__underscore", "bad!char", "shrt", "a"*31
    ])
    def test_username_invalid(self, username):
        data = {
            "username": username,
            "email": "valid@example.com",
            "password": "ValidPass123!@#",
            "first_name": "John",
            "last_name": "Doe"
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    @pytest.mark.parametrize("password", [
        "nouppercase123!@#", "NOLOWERCASE123!@#", "NoNumber!@#", "NoSpecial123", "Short1!a", "a"*21
    ])
    def test_password_invalid(self, password):
        data = {
            "username": "validuser",
            "email": "valid@example.com",
            "password": password,
            "first_name": "John",
            "last_name": "Doe"
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    @pytest.mark.parametrize("first_name", ["John1", "J@hn", "", " "])
    def test_first_name_invalid(self, first_name):
        data = {
            "username": "validuser",
            "email": "valid@example.com",
            "password": "ValidPass123!@#",
            "first_name": first_name,
            "last_name": "Doe"
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    @pytest.mark.parametrize("last_name", ["Doe1", "D0e", "", " "])
    def test_last_name_invalid(self, last_name):
        data = {
            "username": "validuser",
            "email": "valid@example.com",
            "password": "ValidPass123!@#",
            "first_name": "John",
            "last_name": last_name
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    @pytest.mark.parametrize("phone", ["12345", "+1-555-123-456789012345", "badphone!!"])
    def test_phone_invalid(self, phone):
        data = {
            "username": "validuser",
            "email": "valid@example.com",
            "password": "ValidPass123!@#",
            "first_name": "John",
            "last_name": "Doe",
            "phone": phone
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    def test_date_of_birth_too_young(self):
        from datetime import date, timedelta
        too_young = (date.today() - timedelta(days=12*365)).isoformat()
        data = {
            "username": "validuser",
            "email": "valid@example.com",
            "password": "ValidPass123!@#",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": too_young
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    def test_date_of_birth_in_future(self):
        from datetime import date, timedelta
        future = (date.today() + timedelta(days=1)).isoformat()
        data = {
            "username": "validuser",
            "email": "valid@example.com",
            "password": "ValidPass123!@#",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": future
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    def test_date_of_birth_too_old(self):
        from datetime import date, timedelta
        too_old = (date.today() - timedelta(days=121*365)).isoformat()
        data = {
            "username": "validuser",
            "email": "valid@example.com",
            "password": "ValidPass123!@#",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": too_old
        }
        with pytest.raises(ValidationError):
            UserRegistrationRequest(**data)

    def test_optional_fields(self):
        data = {
            "username": "validuser",
            "email": "valid@example.com",
            "password": "ValidPass123!@#",
            "first_name": "John",
            "last_name": "Doe"
        }
        req = UserRegistrationRequest(**data)
        assert req.phone is None
        assert req.date_of_birth is None
        assert req.marketing_emails_consent is False