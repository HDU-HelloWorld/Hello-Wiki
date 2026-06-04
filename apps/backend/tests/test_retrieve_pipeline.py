from uuid import UUID

import pytest

from src.application.retrieve.commands import SearchKnowledgeCommand
from src.application.retrieve.pipeline import RetrieveSearchUseCase, _select_top_page_ids
from src.domain.knowledge.catalog_vo import KnowledgePartition
from src.domain.knowledge.retrieve_vo import QueryTemplate, ScoredRow, SearchHit


def _id(value: str) -> UUID:
    return UUID(value)


def _partition(ws: str = "00000000-0000-0000-0000-000000000001") -> KnowledgePartition:
    return KnowledgePartition(workspace_id=_id(ws), domain_id="general")


def test_select_top_page_ids_skips_excluded_and_fills_top_k() -> None:
    fused = [
        (_id("00000000-0000-0000-0000-000000000001"), 1.0),
        (_id("00000000-0000-0000-0000-000000000002"), 0.9),
        (_id("00000000-0000-0000-0000-000000000003"), 0.8),
    ]
    exclude = frozenset({_id("00000000-0000-0000-0000-000000000001")})

    top = _select_top_page_ids(fused, top_k=2, exclude=exclude)

    assert top == [
        _id("00000000-0000-0000-0000-000000000002"),
        _id("00000000-0000-0000-0000-000000000003"),
    ]


@pytest.mark.asyncio
async def test_retrieve_use_case_skips_time_channel_without_range() -> None:
    page_id = _id("00000000-0000-0000-0000-000000000010")

    class FakeRepo:
        async def search_by_tags(
            self, partition: KnowledgePartition, target_tags: list[str], limit: int
        ) -> list[ScoredRow]:
            return []

        async def search_by_fulltext(
            self, partition: KnowledgePartition, query: str, limit: int
        ) -> list[ScoredRow]:
            return [ScoredRow(page_id=page_id, score=1.0)]

        async def search_by_time_range(
            self, partition: KnowledgePartition, start, end, limit: int
        ) -> list[ScoredRow]:
            raise AssertionError("time channel should be skipped")

        async def search_by_vector_pages(
            self, partition: KnowledgePartition, embedding: list[float], limit: int
        ) -> list[ScoredRow]:
            return []

        async def search_by_vector_chunks(
            self, partition: KnowledgePartition, embedding: list[float], limit: int
        ) -> list[ScoredRow]:
            return []

        async def has_any_embeddings(self, partition: KnowledgePartition) -> bool:
            return False

        async def fetch_hits_by_page_ids(
            self, partition: KnowledgePartition, page_ids: list[UUID]
        ) -> list[SearchHit]:
            return [
                SearchHit(
                    page_id=page_id,
                    score=0.0,
                    title="T",
                    compiled_truth="truth",
                    summary="s",
                    tag_paths=[],
                    score_breakdown={},
                )
            ]

        async def update_page_embedding(self, page_id: UUID, embedding: list[float]) -> None:
            pass

        async def update_chunk_embedding(self, chunk_id: UUID, embedding: list[float]) -> None:
            pass

    use_case = RetrieveSearchUseCase(search_repo=FakeRepo(), embedding_port=None)
    command = SearchKnowledgeCommand(
        workspace_id=_id("00000000-0000-0000-0000-000000000001"),
        domain_id="general",
        query=QueryTemplate(
            sanitize_query_for_prompt="辅修选课",
            target_tags=[],
            time_range_start=None,
            time_range_end=None,
        ),
        top_k=5,
    )

    hits, degraded = await use_case.execute(command)

    assert len(hits) == 1
    assert "time_channel_skipped" in degraded
    assert "semantic_disabled_no_embeddings" in degraded


@pytest.mark.asyncio
async def test_retrieve_use_case_excludes_page_ids_from_results() -> None:
    excluded = _id("00000000-0000-0000-0000-000000000001")
    other = _id("00000000-0000-0000-0000-000000000002")

    class FakeRepo:
        async def search_by_tags(
            self, partition: KnowledgePartition, target_tags: list[str], limit: int
        ) -> list[ScoredRow]:
            return []

        async def search_by_fulltext(
            self, partition: KnowledgePartition, query: str, limit: int
        ) -> list[ScoredRow]:
            return [
                ScoredRow(page_id=excluded, score=1.0),
                ScoredRow(page_id=other, score=0.5),
            ]

        async def search_by_time_range(
            self, partition: KnowledgePartition, start, end, limit: int
        ) -> list[ScoredRow]:
            return []

        async def search_by_vector_pages(
            self, partition: KnowledgePartition, embedding: list[float], limit: int
        ) -> list[ScoredRow]:
            return []

        async def search_by_vector_chunks(
            self, partition: KnowledgePartition, embedding: list[float], limit: int
        ) -> list[ScoredRow]:
            return []

        async def has_any_embeddings(self, partition: KnowledgePartition) -> bool:
            return False

        async def fetch_hits_by_page_ids(
            self, partition: KnowledgePartition, page_ids: list[UUID]
        ) -> list[SearchHit]:
            return [
                SearchHit(
                    page_id=pid,
                    score=0.0,
                    title="T",
                    compiled_truth="truth",
                    summary=None,
                    tag_paths=[],
                    score_breakdown={},
                )
                for pid in page_ids
            ]

        async def update_page_embedding(self, page_id: UUID, embedding: list[float]) -> None:
            pass

        async def update_chunk_embedding(self, chunk_id: UUID, embedding: list[float]) -> None:
            pass

    use_case = RetrieveSearchUseCase(search_repo=FakeRepo(), embedding_port=None)
    command = SearchKnowledgeCommand(
        workspace_id=_id("00000000-0000-0000-0000-000000000104"),
        domain_id="general",
        query=QueryTemplate(
            sanitize_query_for_prompt="query",
            target_tags=[],
            time_range_start=None,
            time_range_end=None,
        ),
        top_k=1,
        exclude_page_ids=frozenset({excluded}),
    )

    hits, degraded = await use_case.execute(command)

    assert len(hits) == 1
    assert hits[0].page_id == other
    assert "time_channel_skipped" in degraded
