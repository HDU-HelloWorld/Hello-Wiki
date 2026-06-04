from uuid import UUID

from src.application.retrieve.rrf import rrf_fusion
from src.domain.knowledge.retrieve_vo import ScoredRow


def _id(value: str) -> UUID:
    return UUID(value)


def test_rrf_fusion_prefers_documents_ranked_high_in_multiple_channels() -> None:
    tag = [
        ScoredRow(page_id=_id("00000000-0000-0000-0000-000000000001"), score=1.0),
        ScoredRow(page_id=_id("00000000-0000-0000-0000-000000000002"), score=0.5),
    ]
    semantic = [
        ScoredRow(page_id=_id("00000000-0000-0000-0000-000000000001"), score=0.9),
        ScoredRow(page_id=_id("00000000-0000-0000-0000-000000000003"), score=0.8),
    ]
    bm25 = [
        ScoredRow(page_id=_id("00000000-0000-0000-0000-000000000002"), score=0.7),
    ]
    time_results: list[ScoredRow] = []

    fused = rrf_fusion(tag, semantic, bm25, time_results)

    assert fused[0][0] == _id("00000000-0000-0000-0000-000000000001")
    assert fused[0][1] > fused[1][1]


def test_rrf_fusion_returns_empty_for_no_results() -> None:
    assert rrf_fusion([], [], [], []) == []
