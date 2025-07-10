import pytest
from pydantic import ValidationError
from entities.auth import LoginRequest, TokenResponse


class TestLoginRequest:
    """Test LoginRequest model validation"""

    def test_valid_login_request(self):
        """Test valid login request data"""
        login_data = {
            "email": "test@example.com",
            "password": "ValidPass123!"
        }
        login = LoginRequest(**login_data)
        assert login.email == "test@example.com"
        assert login.password == "ValidPass123!"

    def test_invalid_email(self):
        """Test login request with invalid email"""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(
                email="invalid-email",
                password="ValidPass123!"
            )
        assert "value is not a valid email address" in str(exc_info.value)

    def test_empty_email(self):
        """Test login request with empty email"""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(
                email="",
                password="ValidPass123!"
            )
        assert "value is not a valid email address" in str(exc_info.value)

    def test_empty_password(self):
        """Test login request with empty password"""
        login = LoginRequest(
            email="test@example.com",
            password=""
        )
        # Empty password is allowed in login (different from registration)
        assert login.password == ""

    def test_missing_email(self):
        """Test login request missing email field"""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(password="ValidPass123!")
        assert "Field required" in str(exc_info.value)

    def test_missing_password(self):
        """Test login request missing password field"""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(email="test@example.com")
        assert "Field required" in str(exc_info.value)

    def test_special_characters_in_email(self):
        """Test login request with various valid email formats"""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "user123@sub.example.org",
            "test-email@example-domain.com"
        ]

        for email in valid_emails:
            login = LoginRequest(
                email=email,
                password="ValidPass123!"
            )
            assert login.email == email

    def test_case_sensitivity(self):
        """Test that email case is handled by Pydantic"""
        email = "Test.User@Example.Com"
        login = LoginRequest(
            email=email,
            password="ValidPass123!"
        )
        # Pydantic V2 normalizes email domains to lowercase
        assert login.email.lower() == email.lower()


class TestTokenResponse:
    """Test TokenResponse model validation"""

    def test_valid_token_response(self):
        """Test valid token response"""
        token_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token",
            "token_type": "bearer"
        }
        token = TokenResponse(**token_data)
        assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"
        assert token.token_type == "bearer"

    def test_default_token_type(self):
        """Test token response with default token type"""
        token = TokenResponse(access_token="test-token-12345")
        assert token.access_token == "test-token-12345"
        assert token.token_type == "bearer"  # Default value

    def test_custom_token_type(self):
        """Test token response with custom token type"""
        token = TokenResponse(
            access_token="test-token-12345",
            token_type="JWT"
        )
        assert token.token_type == "JWT"

    def test_empty_access_token(self):
        """Test token response with empty access token"""
        token = TokenResponse(access_token="")
        # Empty string is allowed
        assert token.access_token == ""

    def test_missing_access_token(self):
        """Test token response missing access token"""
        with pytest.raises(ValidationError) as exc_info:
            TokenResponse(token_type="bearer")
        assert "Field required" in str(exc_info.value)

    def test_none_access_token(self):
        """Test token response with None access token"""
        with pytest.raises(ValidationError) as exc_info:
            TokenResponse(access_token=None)
        assert "Input should be a valid string" in str(exc_info.value)

    def test_long_access_token(self):
        """Test token response with very long access token"""
        long_token = "a" * 1000  # Very long token
        token = TokenResponse(access_token=long_token)
        assert token.access_token == long_token
        assert len(token.access_token) == 1000

    def test_special_characters_in_token(self):
        """Test token with special characters"""
        special_token = "abc.123-def_456+ghi/789=xyz"
        token = TokenResponse(access_token=special_token)
        assert token.access_token == special_token

    def test_jwt_like_token(self):
        """Test with JWT-like token structure"""
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        token = TokenResponse(access_token=jwt_token)
        assert token.access_token == jwt_token
        assert token.token_type == "bearer"

    def test_token_response_dict(self):
        """Test converting token response to dict"""
        token = TokenResponse(
            access_token="test-token",
            token_type="bearer"
        )
        token_dict = token.model_dump()  # Updated for Pydantic V2

        assert token_dict["access_token"] == "test-token"
        assert token_dict["token_type"] == "bearer"
        assert len(token_dict) == 2

    def test_token_response_json(self):
        """Test converting token response to JSON"""
        token = TokenResponse(
            access_token="test-token",
            token_type="bearer"
        )
        token_json = token.model_dump_json()  # Updated for Pydantic V2

        import json
        parsed = json.loads(token_json)
        assert parsed["access_token"] == "test-token"
        assert parsed["token_type"] == "bearer"


class TestAuthModelsIntegration:
    """Test integration between auth models"""

    def test_login_to_token_flow(self):
        """Test typical login to token response flow"""
        # Create login request
        login = LoginRequest(
            email="user@example.com",
            password="SecurePass123!"
        )

        # Simulate successful authentication
        # In real implementation, this would involve password verification
        assert login.email == "user@example.com"

        # Create token response
        token = TokenResponse(
            access_token="generated-jwt-token-here",
            token_type="bearer"
        )

        assert token.access_token == "generated-jwt-token-here"
        assert token.token_type == "bearer"

    def test_multiple_login_requests(self):
        """Test multiple login requests with same email"""
        email = "user@example.com"

        login1 = LoginRequest(email=email, password="Password1!")
        login2 = LoginRequest(email=email, password="Password2!")

        # Same email, different passwords
        assert login1.email == login2.email
        assert login1.password != login2.password

    def test_case_insensitive_token_type(self):
        """Test that token type can handle different cases"""
        token_types = ["bearer", "Bearer", "BEARER", "JWT", "jwt"]

        for token_type in token_types:
            token = TokenResponse(
                access_token="test-token",
                token_type=token_type
            )
            assert token.token_type == token_type  # Should preserve case