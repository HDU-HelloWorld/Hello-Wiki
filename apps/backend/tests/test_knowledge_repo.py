from datetime import UTC, datetime

import asyncpg

from src.infrastructure.db.repositories.knowledge_repo import _tstzrange


def test_tstzrange_returns_asyncpg_range_with_utc_bounds() -> None:
    start = datetime(2025, 2, 1)
    end = datetime(2025, 8, 31)

    value = _tstzrange(start, end)

    assert isinstance(value, asyncpg.Range)
    assert value.lower == datetime(2025, 2, 1, tzinfo=UTC)
    assert value.upper == datetime(2025, 8, 31, tzinfo=UTC)
    assert value.lower_inc is True
    assert value.upper_inc is False


def test_tstzrange_allows_open_end() -> None:
    value = _tstzrange(datetime(2024, 9, 1, tzinfo=UTC), None)

    assert value.lower == datetime(2024, 9, 1, tzinfo=UTC)
    assert value.upper is None
