import pytest
from unittest.mock import Mock, patch
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from inventory_service.src.exceptions.secure_exceptions import (
    StandardErrorResponse,
    secure_internal_exception_handler,
    secure_common_exception_handler,
    secure_validation_exception_handler,
    secure_general_exception_handler,
    secure_http_exception_handler
)
from exceptions.internal_exceptions import (
    InternalAssetNotFoundError,
    InternalDatabaseError,
    InternalValidationError,
    InternalInventoryError
)
from common.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    EntityAlreadyExistsError,
    EntityValidationError,
    ConfigurationError,
    AWSError,
    EntityNotFoundError,
    BusinessRuleError
)


def test_standard_error_response_validation_error():
    response = StandardErrorResponse.validation_error()
    assert response["success"] is False
    assert response["error"] == "VALIDATION_ERROR"

def test_standard_error_response_asset_not_found():
    response = StandardErrorResponse.asset_not_found("BTC")
    assert response["success"] is False
    assert response["error"] == "ASSET_NOT_FOUND"
    assert "BTC" in response["message"]


class TestStandardErrorResponseComprehensive:
    """Comprehensive tests for StandardErrorResponse"""

    def test_validation_error_response_with_errors(self):
        """Test validation error response with specific errors"""
        errors = [{"field": "price", "message": "Must be positive"}]
        response = StandardErrorResponse.validation_error(errors)

        assert response["success"] is False
        assert response["error"] == "VALIDATION_ERROR"
        assert response["validation_errors"] == errors

    def test_asset_not_found_response_no_asset_id(self):
        """Test asset not found response without asset ID"""
        response = StandardErrorResponse.asset_not_found()

        assert response["success"] is False
        assert response["error"] == "ASSET_NOT_FOUND"
        assert "The requested asset was not found" in response["message"]

    def test_service_unavailable_response(self):
        """Test service unavailable response creation"""
        response = StandardErrorResponse.service_unavailable()

        assert response["success"] is False
        assert response["error"] == "SERVICE_UNAVAILABLE"
        assert "Inventory service is temporarily unavailable" in response["message"]
        assert "timestamp" in response

    def test_internal_error_response(self):
        """Test internal error response creation"""
        response = StandardErrorResponse.internal_error()

        assert response["success"] is False
        assert response["error"] == "INTERNAL_ERROR"
        assert "An unexpected error occurred" in response["message"]
        assert "timestamp" in response

    def test_all_error_responses_have_required_fields(self):
        """Test that all error responses have the required fields"""
        responses = [
            StandardErrorResponse.validation_error(),
            StandardErrorResponse.asset_not_found("BTC"),
            StandardErrorResponse.service_unavailable(),
            StandardErrorResponse.internal_error()
        ]

        required_fields = {"success", "error", "message", "timestamp"}

        for response in responses:
            assert all(field in response for field in required_fields)
            assert response["success"] is False
            assert isinstance(response["timestamp"], str)

    def test_error_response_timestamps_are_iso_format(self):
        """Test that error response timestamps are in ISO format"""
        from datetime import datetime

        response = StandardErrorResponse.validation_error()
        timestamp = response["timestamp"]

        # Should be able to parse as ISO format
        parsed_time = datetime.fromisoformat(timestamp)
        assert isinstance(parsed_time, datetime)

    def test_validation_error_response_structure(self):
        """Test validation error response structure"""
        errors = [
            {"field": "price", "message": "Must be positive"},
            {"field": "name", "message": "Required field"}
        ]

        response = StandardErrorResponse.validation_error(errors)

        assert response["validation_errors"] == errors
        assert len(response["validation_errors"]) == 2

    def test_asset_not_found_response_message_variations(self):
        """Test asset not found response with different asset IDs"""
        response1 = StandardErrorResponse.asset_not_found("BTC")
        response2 = StandardErrorResponse.asset_not_found("ETH")
        response3 = StandardErrorResponse.asset_not_found()

        assert "BTC" in response1["message"]
        assert "ETH" in response2["message"]
        assert "The requested asset was not found" in response3["message"]
        assert "BTC" not in response3["message"]


class TestSecureInternalExceptionHandler:
    """Test the secure internal exception handler"""

    @pytest.mark.asyncio
    async def test_asset_not_found_handler(self):
        """Test handling asset not found exception"""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = "http://localhost:8000/assets/BTC"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        error = InternalAssetNotFoundError("BTC", {"active_only": True})

        with patch('inventory_service.src.exceptions.secure_exceptions.logger') as mock_logger:
            response = await secure_internal_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        content = response.body.decode()
        assert "ASSET_NOT_FOUND" in content
        assert "BTC" in content

        # Check that logging was called
        assert mock_logger.error.call_count >= 1

    @pytest.mark.asyncio
    async def test_database_error_handler(self):
        """Test handling database error exception"""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = "http://localhost:8000/assets"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        original_error = Exception("Database connection failed")
        error = InternalDatabaseError("get_asset", "assets", original_error)

        with patch('inventory_service.src.exceptions.secure_exceptions.logger') as mock_logger:
            response = await secure_internal_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        content = response.body.decode()
        assert "SERVICE_UNAVAILABLE" in content

        # Check that logging was called
        assert mock_logger.error.call_count >= 1

    @pytest.mark.asyncio
    async def test_validation_error_handler(self):
        """Test handling validation error exception"""
        request = Mock(spec=Request)
        request.method = "PUT"
        request.url = "http://localhost:8000/assets/BTC"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        error = InternalValidationError("price", -100, "positive", "Price must be positive")

        with patch('inventory_service.src.exceptions.secure_exceptions.logger') as mock_logger:
            response = await secure_internal_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        content = response.body.decode()
        assert "VALIDATION_ERROR" in content

        # Check that logging was called
        assert mock_logger.error.call_count >= 1

    @pytest.mark.asyncio
    async def test_unknown_error_handler(self):
        """Test handling unknown error exception"""
        request = Mock(spec=Request)
        request.method = "DELETE"
        request.url = "http://localhost:8000/assets/BTC"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        error = InternalInventoryError("Unknown error", "UNKNOWN_ERROR")

        with patch('inventory_service.src.exceptions.secure_exceptions.logger') as mock_logger:
            response = await secure_internal_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = response.body.decode()
        assert "INTERNAL_ERROR" in content

        # Check that logging was called
        assert mock_logger.error.call_count >= 1

    @pytest.mark.asyncio
    async def test_handler_with_no_client_info(self):
        """Test handler when client information is not available"""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = "http://localhost:8000/assets"
        request.client = None
        request.headers = {}

        error = InternalAssetNotFoundError("BTC")

        with patch('inventory_service.src.exceptions.secure_exceptions.logger') as mock_logger:
            response = await secure_internal_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Check that logging was called
        assert mock_logger.error.call_count >= 1


class TestSecureCommonExceptionHandler:
    """Test the secure common exception handler"""

    @pytest.mark.asyncio
    async def test_database_connection_error_handler(self):
        """Test handling common database connection error"""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = "http://localhost:8000/assets"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        common_error = DatabaseConnectionError("Connection failed", {"service": "dynamodb"})

        with patch('inventory_service.src.exceptions.secure_exceptions.secure_internal_exception_handler') as mock_handler:
            mock_handler.return_value = JSONResponse(status_code=503, content={"error": "test"})
            await secure_common_exception_handler(request, common_error)

        # Verify that the internal handler was called
        mock_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_operation_error_handler(self):
        """Test handling common database operation error"""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = "http://localhost:8000/assets"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        common_error = DatabaseOperationError("Operation failed", {"operation": "scan"})

        with patch('inventory_service.src.exceptions.secure_exceptions.secure_internal_exception_handler') as mock_handler:
            mock_handler.return_value = JSONResponse(status_code=503, content={"error": "test"})
            await secure_common_exception_handler(request, common_error)

        mock_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_entity_already_exists_error_handler(self):
        """Test handling common entity already exists error"""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = "http://localhost:8000/assets"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        common_error = EntityAlreadyExistsError("Asset exists", {"asset_id": "BTC"})

        with patch('inventory_service.src.exceptions.secure_exceptions.secure_internal_exception_handler') as mock_handler:
            mock_handler.return_value = JSONResponse(status_code=404, content={"error": "test"})
            await secure_common_exception_handler(request, common_error)

        mock_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_entity_validation_error_handler(self):
        """Test handling common entity validation error"""
        request = Mock(spec=Request)
        request.method = "PUT"
        request.url = "http://localhost:8000/assets/BTC"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        common_error = EntityValidationError("Validation failed", {"field": "name"})

        with patch('inventory_service.src.exceptions.secure_exceptions.secure_internal_exception_handler') as mock_handler:
            mock_handler.return_value = JSONResponse(status_code=422, content={"error": "test"})
            await secure_common_exception_handler(request, common_error)

        mock_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_configuration_error_handler(self):
        """Test handling common configuration error"""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = "http://localhost:8000/assets"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        common_error = ConfigurationError("Config error", {"config_key": "database_url"})

        with patch('inventory_service.src.exceptions.secure_exceptions.secure_internal_exception_handler') as mock_handler:
            mock_handler.return_value = JSONResponse(status_code=503, content={"error": "test"})
            await secure_common_exception_handler(request, common_error)

        mock_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_aws_error_handler(self):
        """Test handling common AWS error"""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = "http://localhost:8000/assets"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        common_error = AWSError("AWS error", {"service": "dynamodb"})

        with patch('inventory_service.src.exceptions.secure_exceptions.secure_internal_exception_handler') as mock_handler:
            mock_handler.return_value = JSONResponse(status_code=503, content={"error": "test"})
            await secure_common_exception_handler(request, common_error)

        mock_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_entity_not_found_error_handler(self):
        """Test handling common entity not found error"""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = "http://localhost:8000/assets/BTC"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        common_error = EntityNotFoundError("Not found", {"asset_id": "BTC"})

        with patch('inventory_service.src.exceptions.secure_exceptions.secure_internal_exception_handler') as mock_handler:
            mock_handler.return_value = JSONResponse(status_code=404, content={"error": "test"})
            await secure_common_exception_handler(request, common_error)

        mock_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_business_rule_error_handler(self):
        """Test handling common business rule error"""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = "http://localhost:8000/assets"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        common_error = BusinessRuleError("Business rule violation", {"rule": "max_assets"})

        with patch('inventory_service.src.exceptions.secure_exceptions.secure_internal_exception_handler') as mock_handler:
            mock_handler.return_value = JSONResponse(status_code=422, content={"error": "test"})
            await secure_common_exception_handler(request, common_error)

        mock_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_unknown_common_error_handler(self):
        """Test handling unknown common package error"""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = "http://localhost:8000/assets"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        # Create a mock exception that's not in our known types
        class UnknownCommonError(Exception):
            pass

        unknown_error = UnknownCommonError("Unknown error")

        with patch('inventory_service.src.exceptions.secure_exceptions.secure_internal_exception_handler') as mock_handler:
            mock_handler.return_value = JSONResponse(status_code=503, content={"error": "test"})
            await secure_common_exception_handler(request, unknown_error)

        mock_handler.assert_called_once()


class TestSecureValidationExceptionHandler:
    """Test the secure validation exception handler"""

    @pytest.mark.asyncio
    async def test_validation_error_handler(self):
        """Test handling validation error"""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = "http://localhost:8000/assets"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        # Create a validation error
        from pydantic import ValidationError
        errors = [
            {
                "loc": ("price",),
                "msg": "ensure this value is greater than 0",
                "type": "value_error"
            }
        ]
        exc = RequestValidationError(errors=errors)

        with patch('inventory_service.src.exceptions.secure_exceptions.logger') as mock_logger:
            response = await secure_validation_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        content = response.body.decode()
        assert "VALIDATION_ERROR" in content

        # Check that logging was called
        assert mock_logger.warning.call_count >= 1

    @pytest.mark.asyncio
    async def test_validation_error_handler_with_multiple_errors(self):
        """Test handling validation error with multiple field errors"""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = "http://localhost:8000/assets"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        # Create a validation error with multiple fields
        errors = [
            {
                "loc": ("name",),
                "msg": "field required",
                "type": "value_error"
            },
            {
                "loc": ("price",),
                "msg": "ensure this value is greater than 0",
                "type": "value_error"
            }
        ]
        exc = RequestValidationError(errors=errors)

        with patch('inventory_service.src.exceptions.secure_exceptions.logger') as mock_logger:
            response = await secure_validation_exception_handler(request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        content = response.body.decode()
        assert "VALIDATION_ERROR" in content

        # Check that logging was called
        assert mock_logger.warning.call_count >= 1


class TestSecureGeneralExceptionHandler:
    """Test the secure general exception handler"""

    @pytest.mark.asyncio
    async def test_general_exception_handler(self):
        """Test handling general exception"""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = "http://localhost:8000/assets"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        general_error = Exception("Unexpected error occurred")

        with patch('inventory_service.src.exceptions.secure_exceptions.logger') as mock_logger:
            response = await secure_general_exception_handler(request, general_error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = response.body.decode()
        assert "INTERNAL_ERROR" in content

        # Check that logging was called
        assert mock_logger.error.call_count >= 1

    @pytest.mark.asyncio
    async def test_general_exception_handler_with_custom_exception(self):
        """Test handling custom exception"""
        request = Mock(spec=Request)
        request.method = "DELETE"
        request.url = "http://localhost:8000/assets/BTC"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        class CustomException(Exception):
            pass

        custom_error = CustomException("Custom error message")

        with patch('inventory_service.src.exceptions.secure_exceptions.logger') as mock_logger:
            response = await secure_general_exception_handler(request, custom_error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        content = response.body.decode()
        assert "INTERNAL_ERROR" in content

        # Check that logging was called
        assert mock_logger.error.call_count >= 1


class TestSecureHttpExceptionHandler:
    """Test the secure HTTP exception handler"""

    @pytest.mark.asyncio
    async def test_http_exception_handler(self):
        """Test handling HTTP exception"""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url = "http://localhost:8000/assets"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        from fastapi import HTTPException
        http_error = HTTPException(status_code=400, detail="Bad request")

        with patch('inventory_service.src.exceptions.secure_exceptions.logger') as mock_logger:
            response = await secure_http_exception_handler(request, http_error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        content = response.body.decode()
        # The handler returns a generic error response, not the original detail
        assert "INTERNAL_ERROR" in content

        # Check that logging was called
        assert mock_logger.warning.call_count >= 1

    @pytest.mark.asyncio
    async def test_http_exception_handler_with_custom_detail(self):
        """Test handling HTTP exception with custom detail"""
        request = Mock(spec=Request)
        request.method = "POST"
        request.url = "http://localhost:8000/assets"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}

        from fastapi import HTTPException
        http_error = HTTPException(status_code=403, detail={"error": "Forbidden", "reason": "Insufficient permissions"})

        with patch('inventory_service.src.exceptions.secure_exceptions.logger') as mock_logger:
            response = await secure_http_exception_handler(request, http_error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 403
        content = response.body.decode()
        # The handler returns a generic error response, not the original detail
        assert "INTERNAL_ERROR" in content

        # Check that logging was called
        assert mock_logger.warning.call_count >= 1