from uuid import UUID

from src.api.schemas.retrieve import (
    ScoreBreakdownResponse,
    SearchHitResponse,
    SearchKnowledgeRequest,
    SearchKnowledgeResponse,
)
from src.application.retrieve.commands import SearchKnowledgeCommand
from src.domain.knowledge.retrieve_vo import QueryTemplate, SearchHit


def to_search_knowledge_command(
    request: SearchKnowledgeRequest,
    workspace_id: UUID,
) -> SearchKnowledgeCommand:
    time_range = request.query.time_range
    exclude_page_ids = frozenset(_parse_page_ids(request.exclude_page_ids))
    return SearchKnowledgeCommand(
        workspace_id=workspace_id,
        domain_id=request.domain,
        query=QueryTemplate(
            sanitize_query_for_prompt=request.query.sanitize_query_for_prompt,
            target_tags=list(request.query.target_tags),
            time_range_start=time_range.start if time_range else None,
            time_range_end=time_range.end if time_range else None,
        ),
        top_k=request.top_k,
        exclude_page_ids=exclude_page_ids,
    )


def _parse_page_ids(raw_ids: list[str]) -> list[UUID]:
    parsed: list[UUID] = []
    for index, raw_id in enumerate(raw_ids):
        try:
            parsed.append(UUID(raw_id))
        except ValueError as exc:
            raise ValueError(f"exclude_page_ids[{index}] is not a valid UUID") from exc
    return parsed


def to_search_knowledge_response(
    hits: list[SearchHit],
    degraded: list[str],
) -> SearchKnowledgeResponse:
    return SearchKnowledgeResponse(
        hits=[_to_hit_response(hit) for hit in hits],
        degraded=degraded,
    )


def _to_hit_response(hit: SearchHit) -> SearchHitResponse:
    breakdown = hit.score_breakdown or {}
    return SearchHitResponse(
        page_id=str(hit.page_id),
        score=hit.score,
        title=hit.title,
        compiled_truth=hit.compiled_truth,
        summary=hit.summary,
        tag_paths=list(hit.tag_paths),
        score_breakdown=ScoreBreakdownResponse(
            tag_rank=_as_int(breakdown.get("tag_rank")),
            semantic_rank=_as_int(breakdown.get("semantic_rank")),
            bm25_rank=_as_int(breakdown.get("bm25_rank")),
            time_rank=_as_int(breakdown.get("time_rank")),
        ),
    )


def _as_int(value: object) -> int | None:
    return value if isinstance(value, int) else None
