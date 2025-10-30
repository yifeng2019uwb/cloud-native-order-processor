from unittest.mock import patch, MagicMock

import pytest

from src.shared.health.redis_health import (
    RedisHealthChecker,
    get_redis_health_checker,
    check_redis_health,
)

PATCH_TEST_CONN = "src.shared.health.redis_health.test_redis_connection"
PATCH_LOGGER = "src.shared.health.redis_health.logger"
EXCEPTION_MESSAGE = "test-error"

@patch(PATCH_TEST_CONN, return_value=True)
@patch(PATCH_LOGGER)
def test_is_healthy_true(mock_logger: MagicMock, mock_test_conn: MagicMock):
    checker = RedisHealthChecker()
    assert checker.is_healthy() is True
    mock_test_conn.assert_called_once()
    # Should log info on success
    assert mock_logger.info.called


@patch(PATCH_TEST_CONN, return_value=False)
@patch(PATCH_LOGGER)
def test_is_healthy_false(mock_logger: MagicMock, mock_test_conn: MagicMock):
    checker = RedisHealthChecker()
    assert checker.is_healthy() is False
    mock_test_conn.assert_called_once()
    # Should log warning on failure
    assert mock_logger.warning.called


@patch(PATCH_TEST_CONN, side_effect=RuntimeError(EXCEPTION_MESSAGE))
@patch(PATCH_LOGGER)
def test_is_healthy_exception(mock_logger: MagicMock, mock_test_conn: MagicMock):
    checker = RedisHealthChecker()
    assert checker.is_healthy() is False
    mock_test_conn.assert_called_once()
    # Should log error on exception
    assert mock_logger.error.called


def test_singleton_getter_returns_single_instance():
    # Ensure global singleton returns same instance
    first = get_redis_health_checker()
    second = get_redis_health_checker()
    assert first is second


@patch(PATCH_TEST_CONN, return_value=True)
def test_check_redis_health_wrapper(_mock_test_conn: MagicMock):
    # Wrapper should delegate to singleton checker
    assert check_redis_health() is True
