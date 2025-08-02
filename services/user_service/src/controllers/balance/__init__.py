"""
Balance routes package
Path: cloud-native-order-processor/services/user-service/src/controllers/balance/__init__.py
"""

from fastapi import APIRouter

# Create main balance router that combines all balance-related endpoints
router = APIRouter(tags=["balance"])

# Import and include individual route modules
try:
    from .get_balance import router as get_balance_router
    router.include_router(get_balance_router)
    print("✅ Get balance router included successfully")
except ImportError as e:
    print(f"❌ Could not include get balance router: {e}")

try:
    from .deposit import router as deposit_router
    router.include_router(deposit_router)
    print("✅ Deposit router included successfully")
except ImportError as e:
    print(f"❌ Could not include deposit router: {e}")

try:
    from .withdraw import router as withdraw_router
    router.include_router(withdraw_router)
    print("✅ Withdraw router included successfully")
except ImportError as e:
    print(f"❌ Could not include withdraw router: {e}")

try:
    from .transactions import router as transactions_router
    router.include_router(transactions_router)
    print("✅ Transactions router included successfully")
except ImportError as e:
    print(f"❌ Could not include transactions router: {e}")

__all__ = ["router"]