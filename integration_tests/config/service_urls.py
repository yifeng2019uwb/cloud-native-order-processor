"""
Service URLs for Integration Tests
External Black Box Testing - Integration tests only interact through Gateway
No internal Docker/K8s details or environment detection
"""
from constants import ExternalServices, APIEndpoints

# Gateway is the only entry point for integration tests
GATEWAY_SERVICE_URL = ExternalServices.GATEWAY_BASE_URL
GATEWAY_API_BASE_URL = f"{ExternalServices.GATEWAY_BASE_URL}{APIEndpoints.GATEWAY_API_BASE}"

# All service calls go through Gateway - this is the correct external architecture
def get_user_service_url() -> str:
    """Get User Service URL through Gateway"""
    return f"{ExternalServices.GATEWAY_BASE_URL}{APIEndpoints.SERVICE_VERSION}"

def get_inventory_service_url() -> str:
    """Get Inventory Service URL through Gateway"""
    return f"{ExternalServices.GATEWAY_BASE_URL}{APIEndpoints.SERVICE_VERSION}"

def get_order_service_url() -> str:
    """Get Order Service URL through Gateway"""
    return f"{ExternalServices.GATEWAY_BASE_URL}{APIEndpoints.SERVICE_VERSION}"

def get_frontend_service_url() -> str:
    """Get Frontend Service URL (for end-to-end tests if needed)"""
    return ExternalServices.FRONTEND_URL

# Service URLs (all through Gateway)
USER_SERVICE_URL = get_user_service_url()
INVENTORY_SERVICE_URL = get_inventory_service_url()
ORDER_SERVICE_URL = get_order_service_url()
FRONTEND_SERVICE_URL = get_frontend_service_url()

# Print configuration
print(f"🔧 Integration Test Configuration (External Black Box):")
print(f"   Gateway Service: {GATEWAY_SERVICE_URL}")
print(f"   Gateway API Base: {GATEWAY_API_BASE_URL}")
print(f"   Service Version: {APIEndpoints.SERVICE_VERSION}")
print(f"   All Services: {USER_SERVICE_URL} (via Gateway)")
print(f"   Frontend Service: {FRONTEND_SERVICE_URL}")
print(f"   Architecture: External Black Box Testing (Gateway only)")
print(f"   Internal Knowledge: None - Pure external consumer perspective")
print(f"   Service Access: Through Gateway API only")
print(f"   Port Knowledge: Only Gateway port {ExternalServices.GATEWAY_PORT}")