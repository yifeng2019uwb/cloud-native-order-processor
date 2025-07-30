import pytest
from src.controllers.token_utilis import (
    create_access_token, verify_access_token, JWTError, JWT_SECRET, JWT_ALGORITHM,
    decode_token_payload, is_token_expired, get_token_expiration
)
from jose import jwt
from datetime import datetime, timedelta, timezone
import time
from exceptions import TokenExpiredException


def test_create_access_token_returns_valid_jwt():
    username = "testuser"
    token_data = create_access_token(username)
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["expires_in"] == 24 * 3600
    # Decode and check payload
    payload = jwt.decode(token_data["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == username
    assert payload["type"] == "access_token"
    assert "exp" in payload
    assert "iat" in payload


def test_verify_access_token_valid():
    username = "testuser"
    token_data = create_access_token(username)
    token = token_data["access_token"]
    result = verify_access_token(token)
    assert result == username


def test_verify_access_token_expired():
    username = "testuser"
    # Create token with short expiry
    token_data = create_access_token(username, expires_delta=timedelta(seconds=1))
    token = token_data["access_token"]
    time.sleep(2)  # Wait for token to expire
    with pytest.raises(TokenExpiredException):
        verify_access_token(token)


def test_verify_access_token_invalid():
    # Invalid token string
    with pytest.raises(JWTError):
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
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    with pytest.raises(JWTError) as exc:
        verify_access_token(token)
    assert str(exc.value) == "Invalid token"

def test_verify_access_token_missing_sub():
    # Token missing 'sub'
    payload = {
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "type": "access_token"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    with pytest.raises(JWTError) as exc:
        verify_access_token(token)
    assert str(exc.value) == "Invalid token"

def test_verify_access_token_unexpected(monkeypatch):
    # Simulate unexpected exception in jwt.decode
    def bad_decode(*a, **kw):
        raise RuntimeError("boom")
    monkeypatch.setattr("src.controllers.token_utilis.jwt.decode", bad_decode)
    with pytest.raises(JWTError) as exc:
        verify_access_token("sometoken")
    assert "Token verification failed" in str(exc.value)

def test_decode_token_payload_valid():
    username = "testuser"
    token_data = create_access_token(username)
    token = token_data["access_token"]
    payload = decode_token_payload(token)
    assert payload["sub"] == username
    assert payload["type"] == "access_token"

def test_decode_token_payload_invalid():
    payload = decode_token_payload("not.a.valid.token")
    assert payload == {}

def test_decode_token_payload_unexpected(monkeypatch):
    def bad_decode(*a, **kw):
        raise RuntimeError("decode error")
    monkeypatch.setattr("src.controllers.token_utilis.jwt.decode", bad_decode)
    result = decode_token_payload("sometoken")
    assert result == {}

def test_is_token_expired_false():
    username = "testuser"
    token_data = create_access_token(username, expires_delta=timedelta(seconds=10))
    token = token_data["access_token"]
    assert is_token_expired(token) is False

def test_is_token_expired_true():
    username = "testuser"
    token_data = create_access_token(username, expires_delta=timedelta(seconds=1))
    token = token_data["access_token"]
    time.sleep(2)
    assert is_token_expired(token) is True

def test_is_token_expired_invalid():
    assert is_token_expired("not.a.valid.token") is True

def test_is_token_expired_missing_exp():
    # Token with no 'exp' field
    payload = {
        "sub": "testuser",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "type": "access_token"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    assert is_token_expired(token) is True

def test_is_token_expired_decode_error(monkeypatch):
    def bad_decode(*a, **kw):
        raise RuntimeError("decode error")
    monkeypatch.setattr("src.controllers.token_utilis.decode_token_payload", bad_decode)
    assert is_token_expired("sometoken") is True

def test_get_token_expiration_valid():
    username = "testuser"
    expires = timedelta(seconds=60)
    token_data = create_access_token(username, expires_delta=expires)
    token = token_data["access_token"]
    exp_dt = get_token_expiration(token)
    assert isinstance(exp_dt, datetime)
    assert exp_dt > datetime.now(timezone.utc)

def test_get_token_expiration_invalid():
    assert get_token_expiration("not.a.valid.token") is None

def test_get_token_expiration_missing_exp():
    payload = {
        "sub": "testuser",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "type": "access_token"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    assert get_token_expiration(token) is None

def test_get_token_expiration_decode_error(monkeypatch):
    def bad_decode(*a, **kw):
        raise RuntimeError("decode error")
    monkeypatch.setattr("src.controllers.token_utilis.decode_token_payload", bad_decode)
    assert get_token_expiration("sometoken") is None
