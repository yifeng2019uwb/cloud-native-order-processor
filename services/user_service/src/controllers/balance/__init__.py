"""
Balance Router - User Service Balance Operations

This module provides the balance router that includes all balance-related endpoints:
- GET /balance - Get current balance
- POST /balance/deposit - Deposit funds
- POST /balance/withdraw - Withdraw funds
- GET /balance/transactions - Get transaction history
"""

from fastapi import APIRouter

from .get_balance import router as get_balance_router
from .deposit import router as deposit_router
from .withdraw import router as withdraw_router
from .transactions import router as transactions_router

# Create the main balance router
router = APIRouter()

# Include all balance-related routers
router.include_router(get_balance_router)
router.include_router(deposit_router)
router.include_router(withdraw_router)
router.include_router(transactions_router)