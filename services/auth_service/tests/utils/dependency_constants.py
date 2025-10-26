"""
Dependency constants for auth service unit tests.

This file contains only the dependency paths used in mocking
for auth service unit tests to avoid hardcoded strings.
"""

# =============================================================================
# AUTH SERVICE MOCK PATHS
# =============================================================================

# Token manager mock path - patch where it's instantiated in the function
# Must patch at the exact location where TokenManager() is called
AUTH_SERVICE_TOKEN_MANAGER = "src.controllers.validate.TokenManager"

# Middleware metrics collector mock path
AUTH_SERVICE_MIDDLEWARE_METRICS = "src.middleware.metrics_collector"

# Prometheus client mock paths
PROMETHEUS_INFO = "prometheus_client.Info"
PROMETHEUS_COUNTER = "prometheus_client.Counter"
PROMETHEUS_GAUGE = "prometheus_client.Gauge"
PROMETHEUS_HISTOGRAM = "prometheus_client.Histogram"
