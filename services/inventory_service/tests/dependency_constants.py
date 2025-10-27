"""
Dependency constants for inventory service unit tests
Path: services/inventory_service/tests/dependency_constants.py

Centralized constants for module paths, function names, and configuration used in tests
"""

# =============================================================================
# PATCH PATHS FOR TESTING
# =============================================================================

# Controller patches
PATCH_VALIDATE_ASSET_EXISTS = 'validation.business_validators.validate_asset_exists'
PATCH_GET_REQUEST_ID = 'controllers.assets.get_request_id_from_request'

# =============================================================================
# ROUTER CONFIGURATION
# =============================================================================

ROUTER_TAG_INVENTORY = "inventory"
ROUTER_TAG_HEALTH = "health"

# =============================================================================
# API PATHS
# =============================================================================

API_PATH_ROOT = "/"
API_PATH_ASSET_BY_ID = "/{asset_id}"

# =============================================================================
# HTTP METHODS
# =============================================================================

HTTP_METHOD_GET = "GET"
HTTP_METHOD_POST = "POST"
HTTP_METHOD_PUT = "PUT"
HTTP_METHOD_DELETE = "DELETE"

# =============================================================================
# MIDDLEWARE AND METRICS PATCHES
# =============================================================================

PATCH_METRICS_COLLECTOR = 'src.middleware.metrics_collector'
PATH_METRICS_COLLECTOR = 'src.middleware.metrics_collector'
PATCH_MAIN_GET_METRICS_RESPONSE = 'src.main.get_metrics_response'

# External library dependencies (prometheus_client)
PATCH_PROMETHEUS_INFO = 'prometheus_client.Info'
PATCH_PROMETHEUS_COUNTER = 'prometheus_client.Counter'
PATCH_PROMETHEUS_GAUGE = 'prometheus_client.Gauge'
PATCH_PROMETHEUS_HISTOGRAM = 'prometheus_client.Histogram'