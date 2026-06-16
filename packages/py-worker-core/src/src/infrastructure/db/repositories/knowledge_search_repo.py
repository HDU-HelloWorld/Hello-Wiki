from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import asyncpg

from src.core.config import settings
from src.domain.knowledge.catalog_vo import KnowledgePartition
from src.domain.knowledge.retrieve_vo import ScoredRow, SearchHit
from src.domain.knowledge.scorers.tag_scorer import tag_score
from src.domain.knowledge.scorers.time_scorer import time_overlap_score
from src.domain.knowledge.search_port import KnowledgeSearchPort


def _dsn() -> str:
    return settings.DATABASE_URL.replace("+asyncpg", "")


def _vector_literal(values: list[float]) -> str:
    return "[" + ",".join(str(v) for v in values) + "]"


class KnowledgeSearchRepository(KnowledgeSearchPort):
    async def search_by_tags(
        self, partition: KnowledgePartition, target_tags: list[str], limit: int
    ) -> list[ScoredRow]:
        conn = await asyncpg.connect(_dsn())
        try:
            rows = await conn.fetch(
                """
                SELECT p.id AS page_id, array_agg(t.path::text) AS tag_paths
                FROM pages p
                JOIN page_tags pt ON p.id = pt.page_id
                JOIN tags t ON pt.tag_id = t.id
                WHERE p.workspace_id = $1
                  AND p.domain_id = $2
                  AND t.workspace_id = $1
                  AND t.domain_id = $2
                  AND p.deleted_at IS NULL
                  AND p.status = 'active'
                GROUP BY p.id
                """,
                partition.workspace_id,
                partition.domain_id,
            )
        finally:
            await conn.close()

        if not target_tags:
            return []

        scored: list[ScoredRow] = []
        for row in rows:
            tag_paths = list(row["tag_paths"] or [])
            score = tag_score(target_tags, tag_paths)
            if score > 0:
                scored.append(ScoredRow(page_id=row["page_id"], score=score))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:limit]

    async def search_by_vector_pages(
        self, partition: KnowledgePartition, embedding: list[float], limit: int
    ) -> list[ScoredRow]:
        conn = await asyncpg.connect(_dsn())
        try:
            rows = await conn.fetch(
                """
                SELECT id AS page_id,
                       1 - (truth_embedding <=> $1::vector) AS score
                FROM pages
                WHERE workspace_id = $2
                  AND domain_id = $3
                  AND truth_embedding IS NOT NULL
                  AND deleted_at IS NULL
                  AND status = 'active'
                ORDER BY truth_embedding <=> $1::vector
                LIMIT $4
                """,
                _vector_literal(embedding),
                partition.workspace_id,
                partition.domain_id,
                limit,
            )
        finally:
            await conn.close()

        return [ScoredRow(page_id=row["page_id"], score=float(row["score"])) for row in rows]

    async def search_by_vector_chunks(
        self, partition: KnowledgePartition, embedding: list[float], limit: int
    ) -> list[ScoredRow]:
        """Phase 2 chunk-level semantic search (summary_vector); not used in MVP."""
        conn = await asyncpg.connect(_dsn())
        try:
            rows = await conn.fetch(
                """
                SELECT p.id AS page_id,
                       1 - (rc.summary_vector <=> $1::vector) AS score
                FROM raw_chunks rc
                JOIN pages p ON p.raw_id = rc.id
                WHERE rc.workspace_id = $2
                  AND rc.domain_id = $3
                  AND p.workspace_id = $2
                  AND p.domain_id = $3
                  AND rc.summary_vector IS NOT NULL
                  AND rc.deleted_at IS NULL
                  AND p.deleted_at IS NULL
                  AND p.status = 'active'
                ORDER BY rc.summary_vector <=> $1::vector
                LIMIT $4
                """,
                _vector_literal(embedding),
                partition.workspace_id,
                partition.domain_id,
                limit,
            )
        finally:
            await conn.close()

        return [ScoredRow(page_id=row["page_id"], score=float(row["score"])) for row in rows]

    async def search_by_fulltext(
        self, partition: KnowledgePartition, query: str, limit: int
    ) -> list[ScoredRow]:
        conn = await asyncpg.connect(_dsn())
        try:
            rows = await conn.fetch(
                """
                SELECT p.id AS page_id,
                       ts_rank(rc.fulltext_search, q) AS score
                FROM raw_chunks rc
                JOIN pages p ON p.raw_id = rc.id,
                plainto_tsquery('zhparser', $1) q
                WHERE rc.fulltext_search @@ q
                  AND rc.workspace_id = $2
                  AND rc.domain_id = $3
                  AND p.workspace_id = $2
                  AND p.domain_id = $3
                  AND rc.deleted_at IS NULL
                  AND p.deleted_at IS NULL
                  AND p.status = 'active'
                ORDER BY score DESC
                LIMIT $4
                """,
                query,
                partition.workspace_id,
                partition.domain_id,
                limit,
            )
        finally:
            await conn.close()

        return [ScoredRow(page_id=row["page_id"], score=float(row["score"])) for row in rows]

    async def search_by_time_range(
        self,
        partition: KnowledgePartition,
        start: datetime | None,
        end: datetime | None,
        limit: int,
    ) -> list[ScoredRow]:
        conn = await asyncpg.connect(_dsn())
        try:
            if start is None and end is None:
                rows = await conn.fetch(
                    """
                    SELECT id AS page_id, effective_range
                    FROM pages
                    WHERE workspace_id = $1
                      AND domain_id = $2
                      AND deleted_at IS NULL
                      AND status = 'active'
                    LIMIT $3
                    """,
                    partition.workspace_id,
                    partition.domain_id,
                    limit,
                )
            else:
                lower = start or datetime.min.replace(tzinfo=UTC)
                upper = end or datetime.max.replace(tzinfo=UTC)
                rows = await conn.fetch(
                    """
                    SELECT id AS page_id, effective_range
                    FROM pages
                    WHERE workspace_id = $1
                      AND domain_id = $2
                      AND deleted_at IS NULL
                      AND status = 'active'
                      AND (
                        effective_range IS NULL
                        OR effective_range && tstzrange($3::timestamptz, $4::timestamptz, '[)')
                      )
                    LIMIT $5
                    """,
                    partition.workspace_id,
                    partition.domain_id,
                    lower,
                    upper,
                    limit,
                )
        finally:
            await conn.close()

        scored: list[ScoredRow] = []
        for row in rows:
            page_start, page_end = _range_bounds(row["effective_range"])
            score = time_overlap_score(start, end, page_start, page_end)
            scored.append(ScoredRow(page_id=row["page_id"], score=score))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:limit]

    async def fetch_hits_by_page_ids(
        self, partition: KnowledgePartition, page_ids: list[UUID]
    ) -> list[SearchHit]:
        if not page_ids:
            return []

        conn = await asyncpg.connect(_dsn())
        try:
            rows = await conn.fetch(
                """
                SELECT p.id AS page_id,
                       p.title,
                       p.compiled_truth,
                       rc.summary,
                       COALESCE(
                         array_agg(t.path::text) FILTER (WHERE t.path IS NOT NULL),
                         '{}'
                       ) AS tag_paths
                FROM pages p
                JOIN raw_chunks rc ON rc.id = p.raw_id
                LEFT JOIN page_tags pt ON pt.page_id = p.id
                LEFT JOIN tags t ON t.id = pt.tag_id
                    AND t.workspace_id = p.workspace_id
                    AND t.domain_id = p.domain_id
                WHERE p.workspace_id = $1
                  AND p.domain_id = $2
                  AND p.id = ANY($3::uuid[])
                GROUP BY p.id, p.title, p.compiled_truth, rc.summary
                """,
                partition.workspace_id,
                partition.domain_id,
                page_ids,
            )
        finally:
            await conn.close()

        return [
            SearchHit(
                page_id=row["page_id"],
                score=0.0,
                title=row["title"],
                compiled_truth=row["compiled_truth"],
                summary=row["summary"],
                tag_paths=list(row["tag_paths"] or []),
                score_breakdown={},
            )
            for row in rows
        ]

    async def has_any_embeddings(self, partition: KnowledgePartition) -> bool:
        """MVP: only pages.truth_embedding enables the semantic retrieval channel."""
        conn = await asyncpg.connect(_dsn())
        try:
            row = await conn.fetchrow(
                """
                SELECT EXISTS (
                  SELECT 1 FROM pages
                  WHERE workspace_id = $1
                    AND domain_id = $2
                    AND truth_embedding IS NOT NULL
                    AND deleted_at IS NULL
                ) AS has_embeddings
                """,
                partition.workspace_id,
                partition.domain_id,
            )
        finally:
            await conn.close()

        return bool(row and row["has_embeddings"])

    async def update_page_embedding(self, page_id: UUID, embedding: list[float]) -> None:
        conn = await asyncpg.connect(_dsn())
        try:
            await conn.execute(
                "UPDATE pages SET truth_embedding = $1::vector WHERE id = $2",
                _vector_literal(embedding),
                page_id,
            )
        finally:
            await conn.close()

    async def update_chunk_embedding(self, chunk_id: UUID, embedding: list[float]) -> None:
        conn = await asyncpg.connect(_dsn())
        try:
            await conn.execute(
                "UPDATE raw_chunks SET summary_vector = $1::vector WHERE id = $2",
                _vector_literal(embedding),
                chunk_id,
            )
        finally:
            await conn.close()


def _range_bounds(value: asyncpg.Range[datetime] | None) -> tuple[datetime | None, datetime | None]:
    if value is None:
        return None, None
    lower = value.lower
    upper = value.upper
    return lower, upper
