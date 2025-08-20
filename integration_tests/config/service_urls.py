"""
Service URLs for Integration Tests
Pure Gateway Testing Architecture - All service requests go through Gateway
"""
import os
import requests
from typing import Optional

# Service health check function (kept for potential future use)
def check_service_health(url: str, timeout: int = 2) -> bool:
    """Check if a service is healthy by calling its health endpoint"""
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        return response.status_code == 200
    except (requests.RequestException, requests.Timeout, requests.ConnectionError):
        return False

def get_user_service_url() -> str:
    """Get User Service URL through Gateway"""
    return get_gateway_api_base_url()

def get_inventory_service_url() -> str:
    """Get Inventory Service URL through Gateway"""
    return get_gateway_api_base_url()

def get_order_service_url() -> str:
    """Get Order Service URL through Gateway"""
    return get_gateway_api_base_url()

def get_gateway_service_url() -> str:
    """Get Gateway Service URL (Kubernetes NodePort)"""
    return "http://localhost:30002"

def get_frontend_service_url() -> str:
    """Get Frontend Service URL (Kubernetes NodePort)"""
    return "http://localhost:30003"

def get_grafana_service_url() -> str:
    """Get Grafana Service URL (Kubernetes NodePort)"""
    return "http://localhost:30001"

def get_redis_service_url() -> str:
    """Get Redis Service URL (Kubernetes ClusterIP)"""
    return "redis.order-processor.svc.cluster.local:6379"

def get_prometheus_service_url() -> str:
    """Get Prometheus Service URL (Kubernetes NodePort)"""
    return "http://localhost:30007"

def get_loki_service_url() -> str:
    """Get Loki Service URL (Kubernetes ClusterIP)"""
    return "loki.order-processor.svc.cluster.local:3100"

def get_promtail_service_url() -> str:
    """Get Promtail Service URL (Kubernetes ClusterIP)"""
    return "promtail.order-processor.svc.cluster.local:9080"

def get_gateway_api_base_url() -> str:
    """Get Gateway API Base URL for integration tests (single entry point)"""
    gateway_url = get_gateway_service_url()
    return f"{gateway_url}/api/v1"

# Service URLs (detected at import time)
USER_SERVICE_URL = get_user_service_url()
INVENTORY_SERVICE_URL = get_inventory_service_url()
ORDER_SERVICE_URL = get_order_service_url()
GATEWAY_SERVICE_URL = get_gateway_service_url()
GATEWAY_API_BASE_URL = get_gateway_api_base_url()
FRONTEND_SERVICE_URL = get_frontend_service_url()
GRAFANA_SERVICE_URL = get_grafana_service_url()
REDIS_SERVICE_URL = get_redis_service_url()
PROMETHEUS_SERVICE_URL = get_prometheus_service_url()
LOKI_SERVICE_URL = get_loki_service_url()
PROMTAIL_SERVICE_URL = get_promtail_service_url()

# Print configuration
print(f"🔧 Integration Test Configuration:")
print(f"   User Service: {USER_SERVICE_URL} (via Gateway)")
print(f"   Inventory Service: {INVENTORY_SERVICE_URL} (via Gateway)")
print(f"   Order Service: {ORDER_SERVICE_URL} (via Gateway)")
print(f"   Gateway Service: {GATEWAY_SERVICE_URL}")
print(f"   Gateway API Base: {GATEWAY_API_BASE_URL}")
print(f"   Frontend Service: {FRONTEND_SERVICE_URL}")
print(f"   Grafana Service: {GRAFANA_SERVICE_URL}")
print(f"   Redis Service: {REDIS_SERVICE_URL}")
print(f"   Prometheus Service: {PROMETHEUS_SERVICE_URL}")
print(f"   Loki Service: {LOKI_SERVICE_URL}")
print(f"   Promtail Service: {PROMTAIL_SERVICE_URL}")