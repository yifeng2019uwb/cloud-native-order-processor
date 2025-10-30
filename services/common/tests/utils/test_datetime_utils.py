import re
from datetime import datetime, timezone, timedelta

import pytest

from src.data.entities.datetime_utils import (
    safe_parse_datetime,
    get_current_utc,
)

ISO_Z = "2024-01-02T03:04:05Z"
ISO_OFFSET = "2024-01-02T03:04:05+00:00"


class TestSafeParseDatetime:
    def test_parse_none_returns_utc_now_like(self):
        before = datetime.now(timezone.utc)
        result = safe_parse_datetime(None)
        after = datetime.now(timezone.utc)

        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc
        # Ensure the result is within a reasonable window of "now"
        assert before - timedelta(seconds=1) <= result <= after + timedelta(seconds=1)

    def test_parse_valid_iso_z(self):
        result = safe_parse_datetime(ISO_Z)
        assert result == datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

    def test_parse_valid_iso_offset(self):
        result = safe_parse_datetime(ISO_OFFSET)
        assert result == datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

    def test_parse_invalid_returns_utc_now_like(self):
        before = datetime.now(timezone.utc)
        result = safe_parse_datetime("not-a-datetime")
        after = datetime.now(timezone.utc)

        assert isinstance(result, datetime)
        assert result.tzinfo == timezone.utc
        assert before - timedelta(seconds=1) <= result <= after + timedelta(seconds=1)


def test_get_current_utc_returns_utc_now_like():
    before = datetime.now(timezone.utc)
    result = get_current_utc()
    after = datetime.now(timezone.utc)

    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc
    assert before - timedelta(seconds=1) <= result <= after + timedelta(seconds=1)
