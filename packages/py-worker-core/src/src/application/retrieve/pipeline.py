import asyncio
from typing import Protocol
from uuid import UUID

from src.application.retrieve.commands import SearchKnowledgeCommand
from src.application.retrieve.rrf import rrf_fusion
from src.domain.ai.embedding_port import EmbeddingPort
from src.domain.knowledge.catalog_vo import KnowledgePartition
from src.domain.knowledge.retrieve_vo import ScoredRow, SearchHit
from src.domain.knowledge.search_port import KnowledgeSearchPort

SEARCH_CANDIDATE_LIMIT = 50


class SearchKnowledgePipeline(Protocol):
    async def execute(
        self, command: SearchKnowledgeCommand
    ) -> tuple[list[SearchHit], list[str]]: ...


class RetrieveSearchUseCase:
    """Orchestrate retrieval channels and RRF fusion (no LLM).

    MVP semantic path: query embedding vs pages.truth_embedding only.
    raw_chunks.summary_vector is stored for future use but not searched here.
    """

    def __init__(
        self,
        search_repo: KnowledgeSearchPort,
        embedding_port: EmbeddingPort | None = None,
    ) -> None:
        self._search_repo = search_repo
        self._embedding_port = embedding_port

    async def execute(self, command: SearchKnowledgeCommand) -> tuple[list[SearchHit], list[str]]:
        degraded: list[str] = []
        query = command.query
        limit = SEARCH_CANDIDATE_LIMIT
        exclude = command.exclude_page_ids
        partition = KnowledgePartition(
            workspace_id=command.workspace_id,
            domain_id=command.domain_id,
        )

        tag_task = self._search_repo.search_by_tags(partition, query.target_tags, limit)
        bm25_task = self._search_repo.search_by_fulltext(
            partition, query.sanitize_query_for_prompt, limit
        )

        has_time_range = query.time_range_start is not None or query.time_range_end is not None
        if has_time_range:
            time_task = self._search_repo.search_by_time_range(
                partition,
                query.time_range_start,
                query.time_range_end,
                limit,
            )
        else:
            degraded.append("time_channel_skipped")
            time_task = None

        has_embeddings = await self._search_repo.has_any_embeddings(partition)
        semantic_results: list[ScoredRow] = []

        if has_embeddings and self._embedding_port is not None:
            embedding = await self._embedding_port.embed(query.sanitize_query_for_prompt)
            semantic_results = await self._search_repo.search_by_vector_pages(
                partition, embedding, limit
            )
        elif not has_embeddings:
            degraded.append("semantic_disabled_no_embeddings")
        elif self._embedding_port is None:
            degraded.append("semantic_disabled_no_embedding_provider")

        if time_task is None:
            tag_results, bm25_results = await asyncio.gather(tag_task, bm25_task)
            time_results: list[ScoredRow] = []
        else:
            tag_results, bm25_results, time_results = await asyncio.gather(
                tag_task, bm25_task, time_task
            )

        fused = rrf_fusion(tag_results, semantic_results, bm25_results, time_results)
        top_ids = _select_top_page_ids(fused, command.top_k, exclude)
        if not top_ids:
            return [], degraded

        hits = await self._search_repo.fetch_hits_by_page_ids(partition, top_ids)
        score_map = {page_id: score for page_id, score in fused}
        rank_maps = {
            "tag_rank": _rank_map(tag_results),
            "semantic_rank": _rank_map(semantic_results),
            "bm25_rank": _rank_map(bm25_results),
            "time_rank": _rank_map(time_results),
        }

        ordered: list[SearchHit] = []
        hit_by_id = {hit.page_id: hit for hit in hits}
        for page_id in top_ids:
            hit = hit_by_id.get(page_id)
            if hit is None:
                continue
            hit.score = score_map.get(page_id, 0.0)
            hit.score_breakdown = {
                "tag_rank": rank_maps["tag_rank"].get(page_id),
                "semantic_rank": rank_maps["semantic_rank"].get(page_id),
                "bm25_rank": rank_maps["bm25_rank"].get(page_id),
                "time_rank": rank_maps["time_rank"].get(page_id),
            }
            ordered.append(hit)

        return ordered, degraded


def _select_top_page_ids(
    fused: list[tuple[UUID, float]],
    top_k: int,
    exclude: frozenset[UUID],
) -> list[UUID]:
    selected: list[UUID] = []
    for page_id, _score in fused:
        if page_id in exclude:
            continue
        selected.append(page_id)
        if len(selected) >= top_k:
            break
    return selected


def _rank_map(rows: list[ScoredRow]) -> dict[UUID, int]:
    return {row.page_id: rank for rank, row in enumerate(rows, 1)}
