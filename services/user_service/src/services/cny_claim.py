"""
CNY Claim Service - Loads phrases from cny_phrases.json in __init__,
checks one claim per user per day, and credits reward via balance_dao.

Path: services/user_service/src/services/cny_claim.py
"""
import json
import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from common.data.entities.user import BalanceTransaction, TransactionStatus, TransactionType
from common.data.entities.entity_constants import TransactionFields, TimestampFields
from common.core.utils import UserLock, LockType
from common.exceptions import CNOPDatabaseOperationException
from common.shared.logging import LogDefault

from user_exceptions import CNOPAlreadyClaimedTodayException

CNY_DESCRIPTION_PREFIX = "CNY "
CNY_RED_POCKET_PREFIX = "CNY_RED_POCKET "  # Red pocket - blocks further claims today
DEFAULT_REWARD_AMOUNT = Decimal("8.88")  # Small amount for any phrase not in config
CNY_CONFIG_SECRET_WORDS = "secret_words"
CNY_CONFIG_AMOUNTS = "amounts"


def _get_phrases_path() -> str:
    """Get absolute path to cny_phrases.json relative to this file."""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(this_dir, "..", "..", "..", "config", "cny_phrases.json")


class CNYClaimService:
    """
    CNY claim service - loads phrase config once at init.
    """

    def __init__(self, config_path: str | None = None):
        self._secret_words: list[Any] = []
        self._amounts: list[Any] = []
        self._load_phrases(config_path or _get_phrases_path())

    def _load_phrases(self, path: str) -> None:
        """Load secret_words and amounts lists from JSON file."""
        try:
            with open(path, "r", encoding=LogDefault.FILE_ENCODING) as f:
                data = json.load(f)
            words = data.get(CNY_CONFIG_SECRET_WORDS) or []
            self._secret_words = [str(p).strip() for p in words]
            self._amounts = data.get(CNY_CONFIG_AMOUNTS) or []
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            self._secret_words = []
            self._amounts = []

    def _has_claimed_red_pocket_today(self, balance_dao: Any, username: str) -> bool:
        """
        Check if user has already claimed the red pocket today.

        Only red pocket blocks further claims. Default rewards do not.
        """
        target_date = datetime.now(timezone.utc).date()
        last_key = None

        while True:
            transactions, last_key = balance_dao.get_user_transactions(
                username, limit=100, start_key=last_key
            )
            for t in transactions:
                if not (t.description and t.description.startswith(CNY_RED_POCKET_PREFIX)):
                    continue
                t_date = t.created_at.date() if hasattr(t.created_at, TimestampFields.DATE_ATTR) else t.created_at
                if t_date == target_date:
                    return True
            if last_key is None:
                break

        return False

    async def claim_reward(
        self,
        balance_dao: Any,
        username: str,
        phrase: str,
    ) -> tuple[str, Decimal, bool]:
        """
        Check already claimed today, determine reward amount, and credit.

        If phrase is in config with valid amount, use it and got_red_pocket=True.
        Otherwise give DEFAULT_REWARD_AMOUNT and got_red_pocket=False.

        Returns:
            Tuple of (transaction_id, amount, got_red_pocket)

        Raises:
            CNOPAlreadyClaimedTodayException: User already claimed red pocket today
        """
        phrase = phrase.strip()

        if self._has_claimed_red_pocket_today(balance_dao, username):
            raise CNOPAlreadyClaimedTodayException(
                "You already claimed today. Come back tomorrow for another surprise!"
            )

        got_red_pocket = False
        amount = DEFAULT_REWARD_AMOUNT
        try:
            idx = self._secret_words.index(phrase)
            if idx < len(self._amounts):
                parsed = Decimal(str(self._amounts[idx]))
                if parsed > 0:
                    amount = parsed
                    got_red_pocket = True
        except (ValueError, TypeError, InvalidOperation):
            pass

        description = f"{CNY_RED_POCKET_PREFIX if got_red_pocket else CNY_DESCRIPTION_PREFIX}{phrase}"

        async with UserLock(username, LockType.DEPOSIT):
            transaction = BalanceTransaction(
                Pk=f"{TransactionFields.PK_PREFIX}{username}",
                username=username,
                Sk=datetime.now(timezone.utc).isoformat(),
                transaction_type=TransactionType.DEPOSIT,
                amount=amount,
                description=description,
                status=TransactionStatus.COMPLETED,
                entity_type=TransactionFields.DEFAULT_ENTITY_TYPE,
            )

            created_transaction = balance_dao.create_transaction(transaction)

            try:
                balance_dao._update_balance_from_transaction(created_transaction)
            except Exception as e:
                balance_dao.cleanup_failed_transaction(username, created_transaction.transaction_id)
                raise CNOPDatabaseOperationException(f"Transaction failed: {str(e)}") from e

        return str(created_transaction.transaction_id), amount, got_red_pocket
