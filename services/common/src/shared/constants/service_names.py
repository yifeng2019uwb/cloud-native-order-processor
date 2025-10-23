"""
Centralized Service Names and Related Constants for all services
"""
from enum import Enum


class ServiceNames(str, Enum):
    """Service names used across all services"""

    # Core services
    GATEWAY = "gateway"
    AUTH_SERVICE = "auth-service"
    USER_SERVICE = "user-service"
    ORDER_SERVICE = "order-service"
    INVENTORY_SERVICE = "inventory-service"

    # Service identifiers for validation
    SOURCE_GATEWAY = "gateway"
    AUTH_SERVICE_NAME = "auth-service"


class ServiceValidation:
    """Service validation constants"""

    # Expected source validation
    EXPECTED_SOURCE = "gateway"
    EXPECTED_AUTH_SERVICE = "auth-service"

    # Service roles
    SERVICE_ROLE_GATEWAY = "gateway"
    SERVICE_ROLE_AUTH = "auth"
    SERVICE_ROLE_USER = "user"
    SERVICE_ROLE_ORDER = "order"
    SERVICE_ROLE_INVENTORY = "inventory"


class ServiceVersions:
    """Service version constants"""

    DEFAULT_VERSION = "1.0.0"
