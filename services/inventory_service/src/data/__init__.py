"""
Data initialization package for inventory service
"""

from .init_inventory import (
    initialize_inventory_data,
    startup_inventory_initialization,
    get_inventory_summary,
    check_if_data_exists,
    create_sample_assets
)

__all__ = [
    "initialize_inventory_data",
    "startup_inventory_initialization",
    "get_inventory_summary",
    "check_if_data_exists",
    "create_sample_assets"
]