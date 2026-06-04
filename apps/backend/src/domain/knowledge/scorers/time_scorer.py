from datetime import UTC, datetime


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def time_overlap_score(
    query_start: datetime | None,
    query_end: datetime | None,
    page_start: datetime | None,
    page_end: datetime | None,
) -> float:
    """Score temporal overlap between query range and page effective range."""
    if page_start is None and page_end is None:
        return 0.3

    if query_start is None and query_end is None:
        return 0.3

    q_start = _ensure_utc(query_start) if query_start else datetime.min.replace(tzinfo=UTC)
    q_end = _ensure_utc(query_end) if query_end else datetime.max.replace(tzinfo=UTC)
    p_start = _ensure_utc(page_start) if page_start else datetime.min.replace(tzinfo=UTC)
    p_end = _ensure_utc(page_end) if page_end else datetime.max.replace(tzinfo=UTC)

    overlap_start = max(q_start, p_start)
    overlap_end = min(q_end, p_end)
    if overlap_start >= overlap_end:
        return 0.0

    query_span = max((q_end - q_start).total_seconds(), 1.0)
    page_span = max((p_end - p_start).total_seconds(), 1.0)
    overlap_span = (overlap_end - overlap_start).total_seconds()

    if p_start >= q_start and p_end <= q_end:
        return 1.0

    overlap_ratio = overlap_span / min(query_span, page_span)
    return 0.5 + overlap_ratio * 0.5
