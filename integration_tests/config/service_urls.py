"""
Service URLs for Integration Tests
Automatic detection of Docker vs Kubernetes services with fallback
"""
import os
import requests
from typing import Optional

def check_service_health(url: str, timeout: int = 2) -> bool:
    """Check if a service is healthy by calling its health endpoint"""
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        return response.status_code == 200
    except (requests.RequestException, requests.Timeout, requests.ConnectionError):
        return False

def detect_service_url(service_name: str, docker_port: int, k8s_port: int) -> str:
    """Detect service URL with fallback from Docker to Kubernetes"""
    # Try environment variable first
    env_url = os.getenv(f'{service_name.upper()}_SERVICE_URL')
    if env_url:
        return env_url

    # Try Docker port first (default for local development)
    docker_url = f"http://localhost:{docker_port}"
    if check_service_health(docker_url):
        print(f"✅ {service_name} service detected on Docker port {docker_port}")
        return docker_url

    # Fallback to Kubernetes NodePort
    k8s_url = f"http://localhost:{k8s_port}"
    if check_service_health(k8s_url):
        print(f"✅ {service_name} service detected on Kubernetes NodePort {k8s_port}")
        return k8s_url

    # Default to Docker port (for error messages)
    print(f"⚠️  {service_name} service not detected on Docker ({docker_port}) or K8s ({k8s_port})")
    return docker_url

def get_user_service_url() -> str:
    """Get User Service URL with automatic detection"""
    return detect_service_url("user", docker_port=8000, k8s_port=30001)

def get_inventory_service_url() -> str:
    """Get Inventory Service URL with automatic detection"""
    return detect_service_url("inventory", docker_port=8001, k8s_port=30002)

def get_order_service_url() -> str:
    """Get Order Service URL with automatic detection"""
    return detect_service_url("order", docker_port=8002, k8s_port=30003)

# Service URLs (detected at import time)
USER_SERVICE_URL = get_user_service_url()
INVENTORY_SERVICE_URL = get_inventory_service_url()
ORDER_SERVICE_URL = get_order_service_url()

# Print detected configuration
print(f"🔧 Integration Test Configuration:")
print(f"   User Service: {USER_SERVICE_URL}")
print(f"   Inventory Service: {INVENTORY_SERVICE_URL}")
print(f"   Order Service: {ORDER_SERVICE_URL}")