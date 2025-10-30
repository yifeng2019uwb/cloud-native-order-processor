import pytest

from validation.field_validators import validate_limit
from inventory_exceptions import CNOPAssetValidationException


class TestValidateLimit:
    def test_accepts_int_within_bounds(self):
        assert validate_limit(1) == 1
        assert validate_limit(250) == 250

    def test_converts_string_numeric(self):
        assert validate_limit("10") == 10

    def test_raises_on_non_numeric(self):
        with pytest.raises(CNOPAssetValidationException):
            validate_limit("not-a-number")

    def test_raises_when_too_small(self):
        with pytest.raises(CNOPAssetValidationException):
            validate_limit(0)

    def test_raises_when_too_large(self):
        with pytest.raises(CNOPAssetValidationException):
            validate_limit(251)
