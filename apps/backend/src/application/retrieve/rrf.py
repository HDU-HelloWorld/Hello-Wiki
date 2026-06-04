from uuid import UUID

from src.domain.knowledge.retrieve_vo import RrfWeights, ScoredRow


def rrf_fusion(
    tag_results: list[ScoredRow],
    semantic_results: list[ScoredRow],
    bm25_results: list[ScoredRow],
    time_results: list[ScoredRow],
    *,
    k: int = 60,
    weights: RrfWeights | None = None,
) -> list[tuple[UUID, float]]:
    """Reciprocal Rank Fusion with weighted scores."""
    w = weights or RrfWeights()
    scores: dict[UUID, float] = {}

    for rank, row in enumerate(tag_results, 1):
        scores[row.page_id] = scores.get(row.page_id, 0.0) + w.tag * (1.0 / (k + rank))

    for rank, row in enumerate(semantic_results, 1):
        scores[row.page_id] = scores.get(row.page_id, 0.0) + w.semantic * (1.0 / (k + rank))

    for rank, row in enumerate(bm25_results, 1):
        scores[row.page_id] = scores.get(row.page_id, 0.0) + w.bm25 * (1.0 / (k + rank))

    for rank, row in enumerate(time_results, 1):
        scores[row.page_id] = scores.get(row.page_id, 0.0) + w.time * (1.0 / (k + rank))

    return sorted(scores.items(), key=lambda item: item[1], reverse=True)
