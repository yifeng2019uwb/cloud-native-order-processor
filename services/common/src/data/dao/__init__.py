"""
DAO package - Import individual DAOs only when needed
"""

# ❌ DON'T do this - causes circular imports
# from .user import UserDAO, BalanceDAO
# from .inventory import AssetDAO
# from .order import OrderDAO

# ✅ DO this - let services import what they need
from .base_dao import BaseDAO

__all__ = [
    "BaseDAO"
]

# Services should import directly:
# from common.data.dao.user import UserDAO
# from common.data.dao.inventory import AssetDAO