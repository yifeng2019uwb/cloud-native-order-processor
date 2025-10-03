"""
Balance-related entities for user service.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from .balance_enums import (DEFAULT_TRANSACTION_STATUS, TransactionStatus,
                            TransactionType)


class Balance(BaseModel):
    """User account balance entity - pure business entity without database fields"""

    username: str = Field(..., description="Username for easy access")
    current_balance: Decimal = Field(default=Decimal('0.00'), description="Current account balance")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Balance creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
    )


class BalanceTransaction(BaseModel):
    """Balance transaction entity - pure business entity without database fields"""

    username: str = Field(..., description="Username for easy access")
    transaction_id: UUID = Field(default_factory=uuid4, description="Unique transaction ID")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    amount: Decimal = Field(..., description="Transaction amount (positive for deposits, negative for withdrawals)")
    description: str = Field(..., description="Transaction description")
    status: TransactionStatus = Field(default=DEFAULT_TRANSACTION_STATUS, description="Transaction status")
    reference_id: Optional[str] = Field(None, description="External reference ID (e.g., order ID)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Transaction creation timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
            UUID: lambda v: str(v)
        }
    )


class BalanceItem(BaseModel):
    """Balance database item - includes DynamoDB-specific fields"""

    Pk: str = Field(..., description="Primary key (username)")
    Sk: str = Field(..., description="Sort key (BALANCE)")
    username: str = Field(..., description="Username for easy access")
    current_balance: Decimal = Field(default=Decimal('0.00'), description="Current account balance")
    created_at: str = Field(..., description="Balance creation timestamp (ISO string)")
    updated_at: str = Field(..., description="Last update timestamp (ISO string)")
    entity_type: str = Field(default="balance", description="Entity type identifier")

    @classmethod
    def from_entity(cls, balance: Balance) -> BalanceItem:
        """Convert Balance entity to BalanceItem for database storage"""
        return cls(
            Pk=balance.username,
            Sk="BALANCE",
            username=balance.username,
            current_balance=balance.current_balance,
            created_at=balance.created_at.isoformat(),
            updated_at=balance.updated_at.isoformat(),
            entity_type="balance"
        )

    def to_entity(self) -> Balance:
        """Convert BalanceItem to Balance entity"""
        return Balance(
            username=self.username,
            current_balance=self.current_balance,
            created_at=datetime.fromisoformat(self.created_at.replace('Z', '+00:00')) if self.created_at else datetime.utcnow(),
            updated_at=datetime.fromisoformat(self.updated_at.replace('Z', '+00:00')) if self.updated_at else datetime.utcnow()
        )

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
    )


class BalanceTransactionItem(BaseModel):
    """Balance transaction database item - includes DynamoDB-specific fields"""

    Pk: str = Field(..., description="Primary key (TRANS#{username})")
    Sk: str = Field(..., description="Sort key (ISO timestamp string)")
    username: str = Field(..., description="Username for easy access")
    transaction_id: str = Field(..., description="Unique transaction ID (UUID string)")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    amount: Decimal = Field(..., description="Transaction amount (positive for deposits, negative for withdrawals)")
    description: str = Field(..., description="Transaction description")
    status: TransactionStatus = Field(..., description="Transaction status")
    reference_id: Optional[str] = Field(None, description="External reference ID (e.g., order ID)")
    created_at: str = Field(..., description="Transaction creation timestamp (ISO string)")
    entity_type: str = Field(default="balance_transaction", description="Entity type identifier")

    @classmethod
    def from_entity(cls, transaction: BalanceTransaction) -> BalanceTransactionItem:
        """Convert BalanceTransaction entity to BalanceTransactionItem for database storage"""
        return cls(
            Pk=f"TRANS#{transaction.username}",
            Sk=transaction.created_at.isoformat(),
            username=transaction.username,
            transaction_id=str(transaction.transaction_id),
            transaction_type=transaction.transaction_type,
            amount=transaction.amount,
            description=transaction.description,
            status=transaction.status,
            reference_id=transaction.reference_id,
            created_at=transaction.created_at.isoformat(),
            entity_type="balance_transaction"
        )

    def to_entity(self) -> BalanceTransaction:
        """Convert BalanceTransactionItem to BalanceTransaction entity"""
        return BalanceTransaction(
            username=self.username,
            transaction_id=UUID(self.transaction_id),
            transaction_type=self.transaction_type,
            amount=self.amount,
            description=self.description,
            status=self.status,
            reference_id=self.reference_id,
            created_at=datetime.fromisoformat(self.created_at.replace('Z', '+00:00')) if self.created_at else datetime.utcnow()
        )

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
            UUID: lambda v: str(v)
        }
    )