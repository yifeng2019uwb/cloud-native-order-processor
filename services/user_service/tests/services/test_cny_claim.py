"""
Unit tests for CNYClaimService
"""
import json
import tempfile
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

from src.services.cny_claim import (
    CNYClaimService,
    CNY_DESCRIPTION_PREFIX,
    CNY_RED_POCKET_PREFIX,
    DEFAULT_REWARD_AMOUNT,
)
from user_exceptions import CNOPAlreadyClaimedTodayException


def _make_config(secret_words: list, amounts: list) -> str:
    """Create temp config file, return path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump({"secret_words": secret_words, "amounts": amounts}, f)
    f.close()
    return f.name


class TestCNYClaimServiceHasClaimedRedPocketToday:
    def test_returns_true_when_red_pocket_today(self):
        service = CNYClaimService(config_path="/nonexistent")
        mock_tx = MagicMock(description=f"{CNY_RED_POCKET_PREFIX}恭喜发财", created_at=datetime.now(timezone.utc))
        mock_dao = MagicMock()
        mock_dao.get_user_transactions.return_value = ([mock_tx], None)
        assert service._has_claimed_red_pocket_today(mock_dao, "user1") is True

    def test_returns_false_when_no_red_pocket_today(self):
        service = CNYClaimService(config_path="/nonexistent")
        mock_dao = MagicMock()
        mock_dao.get_user_transactions.return_value = ([], None)
        assert service._has_claimed_red_pocket_today(mock_dao, "user1") is False


class TestCNYClaimServiceClaimReward:
    @pytest.fixture
    def mock_dao(self):
        dao = MagicMock()
        dao.get_user_transactions.return_value = ([], None)
        mock_tx = MagicMock(transaction_id="tx-123")
        dao.create_transaction.return_value = mock_tx
        return dao

    @pytest.fixture
    def mock_lock(self):
        lock = AsyncMock()
        lock.__aenter__ = AsyncMock(return_value=None)
        lock.__aexit__ = AsyncMock(return_value=None)
        return lock

    @pytest.mark.asyncio
    async def test_red_pocket_success(self, mock_dao, mock_lock):
        path = _make_config(["恭喜发财"], [88.88])
        try:
            service = CNYClaimService(config_path=path)
            with patch("src.services.cny_claim.UserLock", return_value=mock_lock):
                tx_id, amount, got_red_pocket = await service.claim_reward(mock_dao, "user1", "恭喜发财")
            assert tx_id == "tx-123" and amount == Decimal("88.88") and got_red_pocket is True
        finally:
            Path(path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_default_when_phrase_not_in_config(self, mock_dao, mock_lock):
        path = _make_config(["恭喜发财"], [88.88])
        try:
            service = CNYClaimService(config_path=path)
            with patch("src.services.cny_claim.UserLock", return_value=mock_lock):
                _, amount, got_red_pocket = await service.claim_reward(mock_dao, "user1", "unknown")
            assert amount == DEFAULT_REWARD_AMOUNT and got_red_pocket is False
        finally:
            Path(path).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_raises_when_already_claimed_today(self, mock_dao, mock_lock):
        path = _make_config(["恭喜发财"], [88.88])
        try:
            service = CNYClaimService(config_path=path)
            mock_tx = MagicMock(description=f"{CNY_RED_POCKET_PREFIX}恭喜发财", created_at=datetime.now(timezone.utc))
            mock_dao.get_user_transactions.return_value = ([mock_tx], None)
            with patch("src.services.cny_claim.UserLock", return_value=mock_lock):
                with pytest.raises(CNOPAlreadyClaimedTodayException, match="You already claimed today"):
                    await service.claim_reward(mock_dao, "user1", "恭喜发财")
        finally:
            Path(path).unlink(missing_ok=True)
