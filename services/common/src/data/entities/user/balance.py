"""
Balance-related entities for user service.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict

from .balance_enums import TransactionType, TransactionStatus, DEFAULT_TRANSACTION_STATUS


class Balance(BaseModel):
    """User account balance entity."""

    Pk: str = Field(..., description="Primary key (username)")
    Sk: str = Field(..., description="Sort key (BALANCE)")
    username: str = Field(..., description="Username for easy access")
    current_balance: Decimal = Field(default=Decimal('0.00'), description="Current account balance")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Balance creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    entity_type: str = Field(default="balance", description="Entity type identifier")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
    )


class BalanceTransaction(BaseModel):
    """Balance transaction entity."""

    Pk: str = Field(..., description="Primary key (TRANS#{username})")
    username: str = Field(..., description="Username for easy access")
    Sk: str = Field(..., description="Sort key (ISO timestamp string)")
    transaction_id: UUID = Field(default_factory=uuid4, description="Unique transaction ID")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    amount: Decimal = Field(..., description="Transaction amount (positive for deposits, negative for withdrawals)")
    description: str = Field(..., description="Transaction description")
    status: TransactionStatus = Field(default=DEFAULT_TRANSACTION_STATUS, description="Transaction status")
    reference_id: Optional[str] = Field(None, description="External reference ID (e.g., order ID)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Transaction creation timestamp")
    entity_type: str = Field(default="balance_transaction", description="Entity type identifier")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
            UUID: lambda v: str(v)
        }
    )


class BalanceCreate(BaseModel):
    """Request model for creating a balance."""

    username: str = Field(..., description="Username")
    initial_balance: Decimal = Field(default=Decimal('0.00'), description="Initial balance amount")


class BalanceTransactionCreate(BaseModel):
    """Request model for creating a balance transaction."""

    username: str = Field(..., description="Username")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    amount: Decimal = Field(..., description="Transaction amount")
    description: str = Field(..., description="Transaction description")
    reference_id: Optional[str] = Field(None, description="External reference ID")


class BalanceResponse(BaseModel):
    """Response model for balance information."""

    username: str = Field(..., description="Username")
    current_balance: Decimal = Field(..., description="Current account balance")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
    )


class BalanceTransactionResponse(BaseModel):
    """Response model for balance transaction."""

    transaction_id: UUID = Field(..., description="Unique transaction ID")
    username: str = Field(..., description="Username")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    amount: Decimal = Field(..., description="Transaction amount")
    description: str = Field(..., description="Transaction description")
    status: TransactionStatus = Field(..., description="Transaction status")
    reference_id: Optional[str] = Field(None, description="External reference ID")
    created_at: datetime = Field(..., description="Transaction creation timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
            UUID: lambda v: str(v)
        }
    )


class BalanceTransactionListResponse(BaseModel):
    """Response model for list of balance transactions."""

    transactions: list[BalanceTransactionResponse] = Field(..., description="List of transactions")
    total_count: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")