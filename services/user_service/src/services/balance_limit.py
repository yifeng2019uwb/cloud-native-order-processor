"""
Balance daily limit helper - service layer only (no common changes).
Computes daily totals from balance_dao.get_user_transactions.
"""
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from common.data.entities.user.balance_enums import TransactionType
from user_exceptions import CNOPDailyLimitExceededException

from constants import (
    DEFAULT_DAILY_DEPOSIT_LIMIT,
    DEFAULT_DAILY_WITHDRAW_LIMIT,
    ENV_DAILY_DEPOSIT_LIMIT,
    ENV_DAILY_WITHDRAW_LIMIT,
)


def get_daily_total(
    balance_dao: Any,
    username: str,
    transaction_type: TransactionType,
    date_utc: datetime | None = None,
) -> Decimal:
    """
    Get sum of deposit or withdraw transactions for a user on a given calendar day (UTC).
    Uses balance_dao.get_user_transactions and filters by date and type.

    Args:
        balance_dao: BalanceDAO instance (from common)
        username: Username
        transaction_type: TransactionType.DEPOSIT or TransactionType.WITHDRAW
        date_utc: Date in UTC (default: today). Only the date part is used.

    Returns:
        Sum of absolute amounts for that type on that day.
    """
    if date_utc is None:
        date_utc = datetime.now(timezone.utc)
    target_date = date_utc.date()

    total = Decimal("0")
    last_key = None

    while True:
        transactions, last_key = balance_dao.get_user_transactions(
            username, limit=100, start_key=last_key
        )
        for t in transactions:
            if t.transaction_type != transaction_type:
                continue
            t_date = t.created_at.date() if hasattr(t.created_at, "date") else t.created_at
            if t_date != target_date:
                continue
            amt = Decimal(str(t.amount)) if not isinstance(t.amount, Decimal) else t.amount
            total += abs(amt)
        if last_key is None:
            break

    return total


def validate_daily_deposit_limit(
    balance_dao: Any,
    username: str,
    amount: Decimal,
) -> None:
    """
    Validate that deposit amount does not exceed daily limit.
    Raises CNOPDailyLimitExceededException if limit would be exceeded.
    """
    daily_limit = Decimal(
        os.getenv(ENV_DAILY_DEPOSIT_LIMIT, DEFAULT_DAILY_DEPOSIT_LIMIT)
    )
    daily_total = get_daily_total(balance_dao, username, TransactionType.DEPOSIT)
    if daily_total + amount > daily_limit:
        raise CNOPDailyLimitExceededException(
            f"Daily deposit limit exceeded. Limit: ${daily_limit:,.2f}, "
            f"Already deposited today: ${daily_total:,.2f}, "
            f"Requested: ${amount:,.2f}. Try again tomorrow."
        )


def validate_daily_withdraw_limit(
    balance_dao: Any,
    username: str,
    amount: Decimal,
) -> None:
    """
    Validate that withdrawal amount does not exceed daily limit.
    Raises CNOPDailyLimitExceededException if limit would be exceeded.
    """
    daily_limit = Decimal(
        os.getenv(ENV_DAILY_WITHDRAW_LIMIT, DEFAULT_DAILY_WITHDRAW_LIMIT)
    )
    daily_total = get_daily_total(balance_dao, username, TransactionType.WITHDRAW)
    if daily_total + amount > daily_limit:
        raise CNOPDailyLimitExceededException(
            f"Daily withdrawal limit exceeded. Limit: ${daily_limit:,.2f}, "
            f"Already withdrawn today: ${daily_total:,.2f}, "
            f"Requested: ${amount:,.2f}. Try again tomorrow."
        )
