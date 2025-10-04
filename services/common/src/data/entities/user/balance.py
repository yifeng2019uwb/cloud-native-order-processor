"""
Balance-related entities for user service.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.models import Model

from ..entity_constants import AWSConfig, BalanceFields, TableNames, TransactionFields, UserConstants
from ..datetime_utils import get_current_utc
from .balance_enums import (DEFAULT_TRANSACTION_STATUS, TransactionStatus,
                            TransactionType)


class Balance(BaseModel):
    """User account balance entity - pure business entity without database fields"""

    username: str = Field(..., description="Username for easy access")
    current_balance: Decimal = Field(default=Decimal('0.00'), description="Current account balance")
    created_at: datetime = Field(default_factory=get_current_utc, description="Balance creation timestamp")
    updated_at: datetime = Field(default_factory=get_current_utc, description="Last update timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: str
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
    created_at: datetime = Field(default_factory=get_current_utc, description="Transaction creation timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: str,
            UUID: str
        }
    )


# ==================== PYNAMODB MODELS ====================

class BalanceItem(Model):
    """Balance PynamoDB model - handles DynamoDB operations for user balances"""

    class Meta:
        """Meta class for BalanceItem"""
        table_name = os.getenv(UserConstants.USERS_TABLE_ENV_VAR, TableNames.USERS)
        region = os.getenv(AWSConfig.AWS_REGION_ENV_VAR, AWSConfig.DEFAULT_REGION)
        billing_mode = AWSConfig.BILLING_MODE_PAY_PER_REQUEST

    # Primary Key
    Pk = UnicodeAttribute(hash_key=True)
    Sk = UnicodeAttribute(range_key=True, default=BalanceFields.SK_VALUE)

    # Balance fields
    username = UnicodeAttribute()
    current_balance = UnicodeAttribute()  # Store as string for Decimal precision
    entity_type = UnicodeAttribute(default=BalanceFields.DEFAULT_ENTITY_TYPE)

    # Timestamps
    created_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))
    updated_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_balance(cls, balance: Balance) -> BalanceItem:
        """Create BalanceItem from Balance domain model"""
        balance_item = cls()
        balance_item.Pk = balance.username
        balance_item.Sk = BalanceFields.SK_VALUE
        balance_item.username = balance.username
        balance_item.current_balance = str(balance.current_balance)
        balance_item.created_at = balance.created_at
        balance_item.updated_at = balance.updated_at
        return balance_item

    def to_balance(self) -> Balance:
        """Convert BalanceItem to Balance domain model"""
        return Balance(
            username=self.username,
            current_balance=Decimal(self.current_balance),
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def save(self, condition=None, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = get_current_utc()
        return super().save(condition=condition, **kwargs)


class BalanceTransactionItem(Model):
    """Balance Transaction PynamoDB model - handles DynamoDB operations for balance transactions"""

    class Meta:
        """Meta class for BalanceTransactionItem"""
        table_name = os.getenv(UserConstants.USERS_TABLE_ENV_VAR, TableNames.USERS)
        region = os.getenv(AWSConfig.AWS_REGION_ENV_VAR, AWSConfig.DEFAULT_REGION)
        billing_mode = AWSConfig.BILLING_MODE_PAY_PER_REQUEST

    # Primary Key
    Pk = UnicodeAttribute(hash_key=True)  # TRANS#{username}
    Sk = UnicodeAttribute(range_key=True)  # ISO timestamp

    # Transaction fields
    username = UnicodeAttribute()
    transaction_id = UnicodeAttribute()
    transaction_type = UnicodeAttribute()
    amount = UnicodeAttribute()  # Store as string for Decimal precision
    description = UnicodeAttribute()
    status = UnicodeAttribute()
    reference_id = UnicodeAttribute(null=True)
    entity_type = UnicodeAttribute(default=TransactionFields.DEFAULT_ENTITY_TYPE)

    # Timestamps
    created_at = UTCDateTimeAttribute(default=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_balance_transaction(cls, transaction: BalanceTransaction) -> BalanceTransactionItem:
        """Create BalanceTransactionItem from BalanceTransaction domain model"""
        transaction_item = cls()
        transaction_item.Pk = f"{TransactionFields.PK_PREFIX}{transaction.username}"
        transaction_item.Sk = transaction.created_at.isoformat()
        transaction_item.username = transaction.username
        transaction_item.transaction_id = str(transaction.transaction_id)
        transaction_item.transaction_type = transaction.transaction_type.value
        transaction_item.amount = str(transaction.amount)
        transaction_item.description = transaction.description
        transaction_item.status = transaction.status.value
        transaction_item.reference_id = transaction.reference_id
        transaction_item.created_at = transaction.created_at
        return transaction_item

    def to_balance_transaction(self) -> BalanceTransaction:
        """Convert BalanceTransactionItem to BalanceTransaction domain model"""
        return BalanceTransaction(
            username=self.username,
            transaction_id=UUID(self.transaction_id),
            transaction_type=TransactionType(self.transaction_type),
            amount=Decimal(self.amount),
            description=self.description,
            status=TransactionStatus(self.status),
            reference_id=self.reference_id,
            created_at=self.created_at
        )