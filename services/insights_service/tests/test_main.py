"""
Unit tests for main.py - FastAPI application entry point
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from common.shared.constants.api_constants import HTTPStatus
from common.exceptions import CNOPInternalServerException
from src.main import app, root
from src.api_info_enum import ServiceMetadata, ApiPaths, ApiTags
from src.constants import (
    RESPONSE_FIELD_SERVICE,
    RESPONSE_FIELD_VERSION,
    RESPONSE_FIELD_STATUS,
    RESPONSE_FIELD_TIMESTAMP,
    RESPONSE_FIELD_ENDPOINTS,
    RESPONSE_FIELD_DOCS,
    RESPONSE_FIELD_HEALTH,
    RESPONSE_FIELD_INSIGHTS
)

# Test constants
TEST_ERROR_MESSAGE = "Test error"
TEST_RESPONSE_FIELD_DETAIL = "detail"

# Patch path constants
PATCH_PATH_MAIN_LOGGER = "src.main.logger"


class TestMainApplication:
    """Test the main FastAPI application"""

    def test_app_creation(self):
        """Test that the FastAPI app is created correctly"""
        assert app.title == ServiceMetadata.NAME.value
        assert app.description == ServiceMetadata.DESCRIPTION.value
        assert app.version == ServiceMetadata.VERSION.value
        assert app.docs_url == ApiPaths.DOCS.value
        assert app.redoc_url == ApiPaths.REDOC.value

    def test_cors_middleware_configured(self):
        """Test that CORS middleware is configured"""
        middleware_found = False
        for middleware in app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                middleware_found = True
                break
        assert middleware_found, "CORS middleware should be configured"

    def test_required_routers_included(self):
        """Test that required routers are included"""
        # Check if health router is included
        health_routes = [
            route for route in app.routes
            if hasattr(route, 'path') and ApiPaths.HEALTH.value in str(route.path)
        ]
        assert len(health_routes) > 0

        # Check if insights router is included
        insights_routes = [
            route for route in app.routes
            if hasattr(route, 'path') and ApiPaths.PORTFOLIO_INSIGHTS.value in str(route.path)
        ]
        assert len(insights_routes) > 0


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_endpoint_response(self):
        """Test the root endpoint returns correct information"""
        response = root()

        assert response[RESPONSE_FIELD_SERVICE] == ServiceMetadata.NAME.value
        assert response[RESPONSE_FIELD_VERSION] == ServiceMetadata.VERSION.value
        assert response[RESPONSE_FIELD_STATUS] == ServiceMetadata.STATUS_RUNNING.value
        assert RESPONSE_FIELD_TIMESTAMP in response
        assert RESPONSE_FIELD_ENDPOINTS in response

    def test_root_endpoint_endpoints_structure(self):
        """Test endpoints structure in root response"""
        response = root()
        endpoints = response[RESPONSE_FIELD_ENDPOINTS]

        assert endpoints[RESPONSE_FIELD_DOCS] == ApiPaths.DOCS.value
        assert endpoints[RESPONSE_FIELD_HEALTH] == ApiPaths.HEALTH.value
        assert endpoints[RESPONSE_FIELD_INSIGHTS] == ApiPaths.PORTFOLIO_INSIGHTS.value

    def test_root_endpoint_timestamp_format(self):
        """Test that timestamp is in correct ISO format"""
        response = root()
        timestamp = response[RESPONSE_FIELD_TIMESTAMP]

        # Verify timestamp is in ISO format (contains T and Z or timezone)
        assert 'T' in timestamp
        assert timestamp.endswith('Z') or '+' in timestamp or timestamp.count('T') == 1


class TestHealthEndpoint:
    """Test health endpoint via FastAPI client"""

    def test_health_endpoint(self):
        """Test health endpoint returns 200"""
        client = TestClient(app)
        health_path = ApiPaths.HEALTH.value
        response = client.get(health_path)

        expected_status_code = HTTPStatus.OK
        assert response.status_code == expected_status_code
        
        response_json = response.json()
        status_field = "status"
        assert status_field in response_json
        
        expected_status = "healthy"
        assert response_json[status_field] == expected_status


class TestExceptionHandler:
    """Test exception handlers"""

    def test_internal_exception_handler_registered(self):
        """Test that internal exception handler is registered"""
        # Check if exception handler is registered
        exception_handlers = app.exception_handlers
        assert CNOPInternalServerException in exception_handlers
        
        # Test the handler function directly
        handler_func = exception_handlers[CNOPInternalServerException]
        
        mock_request = MagicMock()
        mock_exc = CNOPInternalServerException(TEST_ERROR_MESSAGE)
        
        with patch(PATCH_PATH_MAIN_LOGGER) as mock_logger:
            response = handler_func(mock_request, mock_exc)
            
            assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
            response_body = response.body.decode() if hasattr(response.body, 'decode') else str(response.body)
            assert TEST_RESPONSE_FIELD_DETAIL in response_body or TEST_ERROR_MESSAGE in response_body
            mock_logger.error.assert_called_once()
