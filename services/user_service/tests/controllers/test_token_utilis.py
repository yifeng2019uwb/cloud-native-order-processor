import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone, timedelta
import jwt
import time

from controllers.token_utilis import (
    create_access_token, verify_access_token, decode_token_payload,
    is_token_expired, get_token_expiration, JWT_SECRET
)
from user_exceptions import TokenExpiredException, TokenInvalidException


def test_create_access_token_returns_valid_jwt():
    username = "testuser"
    token_data = create_access_token(username)
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["expires_in"] == 24 * 3600
    # Decode and check payload
    payload = jwt.decode(token_data["access_token"], JWT_SECRET, algorithms=["HS256"])
    assert payload["sub"] == username
    assert payload["type"] == "access_token"


def test_verify_access_token_valid():
    username = "testuser"
    token_data = create_access_token(username)
    result = verify_access_token(token_data["access_token"])
    assert result == username


def test_verify_access_token_invalid():
    # Invalid token string
    with pytest.raises(TokenInvalidException):
        verify_access_token("not.a.valid.token")


def test_verify_access_token_wrong_type():
    username = "testuser"
    # Create a token with type != 'access_token'
    payload = {
        "sub": username,
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "type": "refresh_token"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    with pytest.raises(TokenInvalidException) as exc:
        verify_access_token(token)
    assert "Invalid token type" in str(exc.value)


def test_verify_access_token_missing_sub():
    # Token missing 'sub'
    payload = {
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "type": "access_token"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    with pytest.raises(TokenInvalidException) as exc:
        verify_access_token(token)
    assert "Token missing subject" in str(exc.value)


def test_verify_access_token_invalid_type():
    """Test verify_access_token with invalid token type"""
    # Create token with wrong type
    token = create_access_token("testuser", expires_delta=timedelta(hours=1))
    # Manually modify the token to have wrong type
    payload = jwt.decode(token["access_token"], JWT_SECRET, algorithms=["HS256"])
    payload["type"] = "wrong_type"
    wrong_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    with pytest.raises(TokenInvalidException):
        verify_access_token(wrong_token)


def test_verify_access_token_missing_subject():
    """Test verify_access_token with missing subject"""
    # Create token without subject
    payload = {
        "type": "access_token",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    with pytest.raises(TokenInvalidException) as exc:
        verify_access_token(token)
    assert "Token missing subject" in str(exc.value)


def test_verify_access_token_expired():
    """Test verify_access_token with expired token"""
    # Create expired token
    payload = {
        "sub": "testuser",
        "type": "access_token",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),  # Expired
        "iat": datetime.now(timezone.utc) - timedelta(hours=2)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    with pytest.raises(TokenExpiredException) as exc:
        verify_access_token(token)
    assert "Token has expired" in str(exc.value)


def test_verify_access_token_verification_failed():
    """Test verify_access_token with verification failure"""
    with patch('jwt.decode') as mock_decode:
        mock_decode.side_effect = Exception("decode error")

        with pytest.raises(TokenInvalidException) as exc:
            verify_access_token("any_token")
        assert "Invalid token" in str(exc.value)


def test_decode_token_payload_valid():
    username = "testuser"
    token_data = create_access_token(username)
    payload = decode_token_payload(token_data["access_token"])
    assert payload["sub"] == username
    assert payload["type"] == "access_token"


def test_decode_token_payload_error():
    """Test decode_token_payload with error"""
    with patch('jwt.decode') as mock_decode:
        mock_decode.side_effect = Exception("decode error")

        result = decode_token_payload("invalid_token")
        assert result == {}


def test_is_token_expired_false():
    username = "testuser"
    token_data = create_access_token(username, expires_delta=timedelta(hours=1))
    token = token_data["access_token"]
    assert is_token_expired(token) is False


def test_is_token_expired_true():
    username = "testuser"
    token_data = create_access_token(username, expires_delta=timedelta(seconds=1))
    token = token_data["access_token"]
    time.sleep(2)
    assert is_token_expired(token) is True


def test_is_token_expired_error():
    """Test is_token_expired with error"""
    with patch('controllers.token_utilis.decode_token_payload') as mock_decode:
        mock_decode.side_effect = Exception("decode error")

        result = is_token_expired("invalid_token")
        assert result is True


def test_get_token_expiration_valid():
    username = "testuser"
    token_data = create_access_token(username, expires_delta=timedelta(hours=1))
    token = token_data["access_token"]
    expiration = get_token_expiration(token)
    assert expiration is not None
    assert isinstance(expiration, datetime)


def test_get_token_expiration_none():
    # Token without expiration
    payload = {
        "sub": "testuser",
        "type": "access_token"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    assert get_token_expiration(token) is None


def test_get_token_expiration_error():
    """Test get_token_expiration with error"""
    with patch('controllers.token_utilis.decode_token_payload') as mock_decode:
        mock_decode.side_effect = Exception("decode error")

        result = get_token_expiration("invalid_token")
        assert result is None
