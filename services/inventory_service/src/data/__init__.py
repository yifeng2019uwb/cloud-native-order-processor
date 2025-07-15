"""
Data initialization package for inventory service
"""

from .init_inventory import (
    initialize_inventory_data,
    startup_inventory_initialization
)

__all__ = [
    "initialize_inventory_data",
    "startup_inventory_initialization"
]