"""
DAO package - Import individual DAOs only when needed
"""

# Import individual DAOs only when needed to avoid circular imports
from .base_dao import BaseDAO

__all__ = [
    "BaseDAO"
]
