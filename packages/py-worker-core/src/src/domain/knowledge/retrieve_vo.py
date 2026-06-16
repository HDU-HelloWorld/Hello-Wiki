from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class QueryTemplate:
    sanitize_query_for_prompt: str
    target_tags: list[str] = field(default_factory=list)
    time_range_start: datetime | None = None
    time_range_end: datetime | None = None


@dataclass(frozen=True)
class ScoredRow:
    page_id: UUID
    score: float


@dataclass(frozen=True)
class RrfWeights:
    tag: float = 0.30
    semantic: float = 0.35
    bm25: float = 0.20
    time: float = 0.15


@dataclass
class SearchHit:
    page_id: UUID
    score: float
    title: str | None
    compiled_truth: str
    summary: str | None
    tag_paths: list[str]
    score_breakdown: dict[str, float | int | None]
