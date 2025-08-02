"""
Balance API Models for User Service

Defines request and response models for balance management operations.

Layer 1: Model validation (field format, basic sanitization)
Layer 2: Business validation (in service layer)
"""

from datetime import datetime
from decimal import Decimal
from typing import List
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Import centralized field validation functions
from validation.field_validators import (
    validate_amount
)

# Import custom exceptions
from user_exceptions import UserValidationException


class BalanceResponse(BaseModel):
    """Response model for getting current balance"""
    current_balance: Decimal
    updated_at: datetime


class DepositRequest(BaseModel):
    """Request model for depositing funds"""
    amount: Decimal = Field(..., gt=0, description="Deposit amount")

    @field_validator('amount')
    @classmethod
    def validate_amount_format(cls, v: Decimal) -> Decimal:
        """Layer 1: Basic format validation for amount"""
        return validate_amount(v)


class DepositResponse(BaseModel):
    """Response model for deposit operation"""
    success: bool
    message: str
    transaction_id: str
    timestamp: datetime


class WithdrawRequest(BaseModel):
    """Request model for withdrawing funds"""
    amount: Decimal = Field(..., gt=0, description="Withdrawal amount")

    @field_validator('amount')
    @classmethod
    def validate_amount_format(cls, v: Decimal) -> Decimal:
        """Layer 1: Basic format validation for amount"""
        return validate_amount(v)


class WithdrawResponse(BaseModel):
    """Response model for withdrawal operation"""
    success: bool
    message: str
    transaction_id: str
    timestamp: datetime


class TransactionResponse(BaseModel):
    """Response model for individual transaction"""
    transaction_id: str
    transaction_type: str  # "deposit" or "withdrawal"
    amount: Decimal
    status: str
    created_at: datetime


class TransactionListResponse(BaseModel):
    """Response model for transaction history"""
    transactions: List[TransactionResponse]
    total_count: int