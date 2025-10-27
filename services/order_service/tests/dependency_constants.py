"""
Dependency constants for order service unit tests
Path: services/order_service/tests/dependency_constants.py

Centralized constants for module paths, function names, and configuration used in tests
"""

# =============================================================================
# MODULE PATHS FOR PATCHING
# =============================================================================

MODULE_PATH_CREATE_ORDER = 'src.controllers.create_order'
MODULE_PATH_DEPENDENCIES = 'src.controllers.dependencies'
MODULE_PATH_GET_ORDER = 'src.controllers.get_order'
MODULE_PATH_LIST_ORDERS = 'src.controllers.list_orders'
MODULE_PATH_ASSET_TRANSACTION = 'src.controllers.asset_transaction'
MODULE_PATH_MIDDLEWARE = 'src.middleware'
MODULE_PATH_METRICS = 'src.metrics'
MODULE_PATH_GET_CURRENT_MARKET_PRICE = 'controllers.dependencies.get_current_market_price'

# =============================================================================
# FUNCTION NAMES FOR PATCHING
# =============================================================================

FUNCTION_VALIDATE_ORDER_CREATION = 'validate_order_creation_business_rules'
FUNCTION_GET_CURRENT_MARKET_PRICE = 'get_current_market_price'
FUNCTION_GET_CURRENT_USER = 'get_current_user'
FUNCTION_GET_ASSET_TRANSACTION_DAO_DEPENDENCY = 'get_asset_transaction_dao_dependency'
FUNCTION_VALIDATE_ORDER_HISTORY_BUSINESS_RULES = 'validate_order_history_business_rules'
FUNCTION_GET_DYNAMODB_MANAGER = 'get_dynamodb_manager'

# =============================================================================
# ROUTER CONFIGURATION
# =============================================================================

ROUTER_TAG_ORDERS = "orders"
ROUTER_TAG_HEALTH = "health"
ROUTER_TAG_ASSET_TRANSACTIONS = "asset transactions"

# =============================================================================
# API PATHS
# =============================================================================

API_PATH_ROOT = "/"
API_PATH_ORDER_BY_ID = "/{order_id}"

# =============================================================================
# HTTP METHODS
# =============================================================================

HTTP_METHOD_GET = "GET"
HTTP_METHOD_POST = "POST"
HTTP_METHOD_PUT = "PUT"
HTTP_METHOD_DELETE = "DELETE"

# =============================================================================
# FULL PATHS FOR PATCHES (module_path.function_name)
# =============================================================================

PATCH_VALIDATE_ORDER_CREATION = 'controllers.create_order.validate_order_creation_business_rules'
PATCH_GET_CURRENT_MARKET_PRICE = 'controllers.dependencies.get_current_market_price'
PATCH_GET_CURRENT_USER = 'src.controllers.dependencies.get_current_user'
PATCH_GET_ASSET_TRANSACTION_DAO = 'src.controllers.dependencies.get_asset_transaction_dao_dependency'
PATCH_VALIDATE_ORDER_HISTORY = 'src.controllers.asset_transaction.validate_order_history_business_rules'
PATCH_GET_DYNAMODB_MANAGER = 'common.data.database.dynamodb_connection.get_dynamodb_manager'
PATCH_METRICS_COLLECTOR = 'src.middleware.metrics_collector'
PATCH_METRICS_GET_METRICS = 'src.metrics.metrics_collector.get_metrics'

# Main app patches
PATCH_MAIN_GET_METRICS_RESPONSE = 'src.main.get_metrics_response'

# Asset transaction specific patches
PATCH_ASSET_TRANSACTION_GET_ASSET_DAO = 'src.controllers.dependencies.get_asset_dao_dependency'
PATCH_ASSET_TRANSACTION_GET_USER_DAO = 'src.controllers.dependencies.get_user_dao_dependency'
PATCH_ASSET_TRANSACTION_DAO_CLASS = 'src.controllers.asset_transaction.AssetTransactionDAO'
PATCH_ASSET_DAO_CLASS = 'src.controllers.asset_transaction.AssetDAO'
PATCH_USER_DAO_CLASS = 'src.controllers.asset_transaction.UserDAO'

# Exception paths
PATCH_CNOP_DATABASE_OP_EXCEPTION = 'src.controllers.asset_transaction.CNOPDatabaseOperationException'
PATCH_CNOP_ENTITY_NOT_FOUND = 'src.controllers.asset_transaction.CNOPEntityNotFoundException'
PATCH_CNOP_INTERNAL_SERVER = 'src.controllers.asset_transaction.CNOPInternalServerException'
PATCH_CNOP_ASSET_NOT_FOUND = 'src.controllers.asset_transaction.CNOPAssetNotFoundException'
PATCH_CNOP_ORDER_VALIDATION = 'src.controllers.asset_transaction.CNOPOrderValidationException'

# External library dependencies (prometheus_client)
PATCH_PROMETHEUS_INFO = 'prometheus_client.Info'
PATCH_PROMETHEUS_COUNTER = 'prometheus_client.Counter'
PATCH_PROMETHEUS_GAUGE = 'prometheus_client.Gauge'
PATCH_PROMETHEUS_HISTOGRAM = 'prometheus_client.Histogram'
