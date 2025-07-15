import pytest
from inventory_service.src.exceptions.secure_exceptions import StandardErrorResponse

def test_standard_error_response_validation_error():
    response = StandardErrorResponse.validation_error()
    assert response["success"] is False
    assert response["error"] == "INVALID_INPUT"

def test_standard_error_response_asset_not_found():
    response = StandardErrorResponse.asset_not_found("BTC")
    assert response["success"] is False
    assert response["error"] == "ASSET_NOT_FOUND"
    assert "BTC" in response["message"]