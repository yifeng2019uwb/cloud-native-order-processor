import pytest
from src.exceptions.internal_exceptions import (
    InternalAuthError, InternalUserExistsError, InternalDatabaseError, InternalValidationError,
    raise_user_exists, raise_database_error, raise_validation_error
)

class DummyError(Exception):
    pass

def test_internal_auth_error_attributes():
    err = InternalAuthError("msg", "CODE", {"foo": "bar"})
    assert err.message == "msg"
    assert err.error_code == "CODE"
    assert err.context == {"foo": "bar"}
    assert isinstance(err.error_id, str)
    assert hasattr(err, "timestamp")
    assert str(err) == "msg"

def test_internal_user_exists_error():
    err = InternalUserExistsError("a@b.com", existing_user_id="123")
    assert err.email == "a@b.com"
    assert err.existing_user_id == "123"
    assert "a@b.com" in err.message
    assert err.error_code == "USER_EXISTS_DETAILED"
    assert "attempted_email" in err.context
    assert err.context["existing_user_id"] == "123"

def test_internal_database_error():
    orig = DummyError("fail")
    err = InternalDatabaseError("create", "users", orig)
    assert err.operation == "create"
    assert err.table_name == "users"
    assert err.original_error is orig
    assert "create" in err.message
    assert "users" in err.message
    assert "fail" in err.message
    assert err.error_code == "DATABASE_ERROR_DETAILED"
    assert err.context["operation"] == "create"
    assert err.context["table_name"] == "users"
    assert err.context["original_error_type"] == "DummyError"
    assert err.context["original_error_message"] == "fail"
    assert err.context["database_driver"] == "dynamodb"
    assert err.context["retry_recommended"] is True

def test_internal_validation_error_short_value():
    err = InternalValidationError("field", "val", "rule", "details")
    assert err.field == "field"
    assert err.value == "val"
    assert err.rule == "rule"
    assert "field" in err.message
    assert err.error_code == "VALIDATION_ERROR_DETAILED"
    assert err.context["field"] == "field"
    assert err.context["attempted_value_preview"] == "val"
    assert err.context["validation_rule"] == "rule"
    assert err.context["validation_details"] == "details"
    assert err.context["validation_source"] == "business_rules"

def test_internal_validation_error_long_value():
    long_val = "x" * 100
    err = InternalValidationError("field", long_val, "rule", "details")
    assert err.context["attempted_value_preview"].startswith("x" * 50)
    assert err.context["attempted_value_preview"].endswith("...")

def test_raise_user_exists():
    with pytest.raises(InternalUserExistsError):
        raise_user_exists("a@b.com", existing_user_id="123")

def test_raise_database_error():
    with pytest.raises(InternalDatabaseError):
        raise_database_error("op", "tbl", DummyError("fail"))

def test_raise_validation_error():
    with pytest.raises(InternalValidationError):
        raise_validation_error("f", "v", "r", "d")