"""
Dependency path constants for unit tests.

This module provides centralized constants for dependency injection paths
used in unit tests, avoiding hardcoded dependency paths.
"""

# =============================================================================
# PORTFOLIO CONTROLLER DEPENDENCIES
# =============================================================================

VALIDATE_USER_PERMISSIONS = "src.controllers.portfolio.portfolio_controller.validate_user_permissions"

# =============================================================================
# PORTFOLIO CONTROLLER METHOD DEPENDENCIES
# =============================================================================

GET_USER_PORTFOLIO = "src.controllers.portfolio.portfolio_controller.get_user_portfolio"
GET_ASSET_BALANCE = "src.controllers.portfolio.asset_balance_controller.get_user_asset_balance"

# =============================================================================
# AUTH SECURITY DEPENDENCIES
# =============================================================================

AUDIT_LOGGER_CLASS = "common.auth.security.audit_logger.AuditLogger"

# =============================================================================
# METRICS DEPENDENCIES
# =============================================================================

GET_METRICS_RESPONSE = "src.main.get_metrics_response"

# Prometheus client paths
PROMETHEUS_INFO = "prometheus_client.Info"
PROMETHEUS_COUNTER = "prometheus_client.Counter"
PROMETHEUS_GAUGE = "prometheus_client.Gauge"
PROMETHEUS_HISTOGRAM = "prometheus_client.Histogram"
