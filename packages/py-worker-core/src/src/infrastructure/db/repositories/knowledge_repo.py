from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import asyncpg

from src.core.config import settings
from src.domain.knowledge.entities import Page, PageTag, PageTimeline, PageVersion, RawChunk, Tag
from src.domain.knowledge.repository import KnowledgeRepositoryPort


def _dsn() -> str:
    return settings.DATABASE_URL.replace("+asyncpg", "")


def _jsonb(val: object) -> str:
    import json

    return json.dumps(val, ensure_ascii=False, default=str)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _tstzrange(start: datetime | None, end: datetime | None) -> asyncpg.Range[datetime]:
    lower = _ensure_utc(start) if start is not None else None
    upper = _ensure_utc(end) if end is not None else None
    return asyncpg.Range(lower, upper, lower_inc=True, upper_inc=False)


class KnowledgeAsyncRepository(KnowledgeRepositoryPort):
    """Async PostgreSQL repository using asyncpg directly.

    Each public method accepts an optional conn parameter.
    When conn is provided (from transactional_extraction_persist),
    the operation runs on the shared connection inside the transaction.
    """

    # ── RawChunk ──────────────────────────────────────────────

    async def save_raw_chunk(self, chunk: RawChunk, conn: asyncpg.Connection | None = None) -> UUID:
        close = False
        if conn is None:
            conn = await asyncpg.connect(_dsn())
            close = True
        try:
            row = await conn.fetchrow(
                "INSERT INTO raw_chunks (id, workspace_id, domain_id, source_id, original_text, "
                "  summary, content_hash, source_url, source_page, source_document, "
                "  extra_metadata, effective_range, status) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11::jsonb, $12, $13) "
                "RETURNING id",
                chunk.id,
                chunk.workspace_id,
                chunk.domain_id,
                chunk.source_id,
                chunk.original_text,
                chunk.summary,
                chunk.content_hash,
                chunk.source_url,
                chunk.source_page,
                chunk.source_document,
                chunk.extra_metadata and _jsonb(chunk.extra_metadata),
                chunk.effective_range and _tstzrange(*chunk.effective_range),
                chunk.status.value,
            )
            return row["id"]  # type: ignore[no-any-return]
        finally:
            if close:
                await conn.close()

    async def get_raw_chunk(self, chunk_id: UUID) -> RawChunk | None:
        conn = await asyncpg.connect(_dsn())
        try:
            row = await conn.fetchrow("SELECT * FROM raw_chunks WHERE id = $1", chunk_id)
            if row is None:
                return None
            return RawChunk(
                id=row["id"],
                original_text=row["original_text"],
                summary=row["summary"],
                source_id=row["source_id"],
            )
        finally:
            await conn.close()

    # ── Page ───────────────────────────────────────────────────

    async def save_page(self, page: Page, conn: asyncpg.Connection | None = None) -> UUID:
        close = False
        if conn is None:
            conn = await asyncpg.connect(_dsn())
            close = True
        try:
            row = await conn.fetchrow(
                "INSERT INTO pages (id, workspace_id, domain_id, source_id, raw_id, title, "
                "  compiled_truth, open_threads, see_also, effective_range, status, version) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9::uuid[], $10, $11, $12) "
                "RETURNING id",
                page.id,
                page.workspace_id,
                page.domain_id,
                page.source_id,
                page.raw_id,
                page.title,
                page.compiled_truth,
                page.open_threads and _jsonb(page.open_threads),
                page.see_also or None,
                page.effective_range and _tstzrange(*page.effective_range),
                page.status.value,
                page.version,
            )
            return row["id"]  # type: ignore[no-any-return]
        finally:
            if close:
                await conn.close()

    async def get_page(self, page_id: UUID) -> Page | None:
        conn = await asyncpg.connect(_dsn())
        try:
            row = await conn.fetchrow("SELECT * FROM pages WHERE id = $1", page_id)
            if row is None:
                return None
            return Page(
                id=row["id"],
                raw_id=row["raw_id"],
                compiled_truth=row["compiled_truth"],
                title=row["title"],
            )
        finally:
            await conn.close()

    # ── Tag ────────────────────────────────────────────────────

    async def find_or_create_tags(
        self, tags: list[Tag], conn: asyncpg.Connection | None = None
    ) -> list[Tag]:
        close = False
        if conn is None:
            conn = await asyncpg.connect(_dsn())
            close = True
        try:
            result: list[Tag] = []
            for tag in tags:
                row = await conn.fetchrow(
                    "INSERT INTO tags (workspace_id, domain_id, name, label, description, "
                    "parent_id, level, path, is_leaf) "
                    "VALUES ($1, $2, $3, $4, $5, $6, $7, $8::ltree, $9) "
                    "ON CONFLICT (workspace_id, domain_id, path) DO UPDATE SET "
                    "  label = EXCLUDED.label "
                    "RETURNING id, name, label, description, level, path::text, is_leaf",
                    tag.workspace_id,
                    tag.domain_id,
                    tag.name,
                    tag.label,
                    tag.description,
                    tag.parent_id,
                    tag.level,
                    tag.path,
                    tag.is_leaf,
                )
                result.append(
                    Tag(
                        id=row["id"],
                        name=row["name"],
                        label=row["label"],
                        description=row["description"],
                        level=row["level"],
                        path=row["path"],
                        is_leaf=row["is_leaf"],
                    )
                )
            return result
        finally:
            if close:
                await conn.close()

    async def get_tags_for_domain(self, workspace_id: UUID, domain_id: str) -> list[Tag]:
        conn = await asyncpg.connect(_dsn())
        try:
            rows = await conn.fetch(
                """
                SELECT id, name, label, level, is_leaf, path::text
                FROM tags
                WHERE workspace_id = $1 AND domain_id = $2
                ORDER BY path
                """,
                workspace_id,
                domain_id,
            )
            return [
                Tag(
                    id=r["id"],
                    name=r["name"],
                    label=r["label"],
                    level=r["level"],
                    is_leaf=r["is_leaf"],
                    path=r["path"],
                )
                for r in rows
            ]
        finally:
            await conn.close()

    # ── PageTag ────────────────────────────────────────────────

    async def assign_tags_to_page(
        self, page_tags: list[PageTag], conn: asyncpg.Connection | None = None
    ) -> None:
        close = False
        if conn is None:
            conn = await asyncpg.connect(_dsn())
            close = True
        try:
            for pt in page_tags:
                sql = (
                    "INSERT INTO page_tags (page_id, tag_id) VALUES ($1, $2) ON CONFLICT DO NOTHING"
                )
                await conn.execute(
                    sql,
                    pt.page_id,
                    pt.tag_id,
                )
                await conn.execute(
                    "UPDATE tags SET document_count = document_count + 1 WHERE id = $1",
                    pt.tag_id,
                )
        finally:
            if close:
                await conn.close()

    # ── PageTimeline ───────────────────────────────────────────

    async def insert_timeline_event(
        self, event: PageTimeline, conn: asyncpg.Connection | None = None
    ) -> UUID:
        close = False
        if conn is None:
            conn = await asyncpg.connect(_dsn())
            close = True
        try:
            row = await conn.fetchrow(
                "INSERT INTO page_timeline (id, page_id, event_at, event_type, "
                "  source_raw_id, source_description, summary) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id",
                event.id,
                event.page_id,
                event.event_at,
                event.event_type.value,
                event.source_raw_id,
                event.source_description,
                event.summary,
            )
            return row["id"]  # type: ignore[no-any-return]
        finally:
            if close:
                await conn.close()

    # ── PageVersion ────────────────────────────────────────────

    async def insert_page_version(
        self, version: PageVersion, conn: asyncpg.Connection | None = None
    ) -> UUID:
        close = False
        if conn is None:
            conn = await asyncpg.connect(_dsn())
            close = True
        try:
            row = await conn.fetchrow(
                "INSERT INTO page_versions (id, page_id, version, compiled_truth, "
                "  page_state, timeline_id, timeline_state) "
                "VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7::jsonb) RETURNING id",
                version.id,
                version.page_id,
                version.version,
                version.compiled_truth,
                _jsonb(version.page_state),
                version.timeline_id,
                _jsonb(version.timeline_state),
            )
            return row["id"]  # type: ignore[no-any-return]
        finally:
            if close:
                await conn.close()

    # ── Transactional ──────────────────────────────────────────

    async def transactional_extraction_persist(
        self,
        chunk: RawChunk,
        page: Page,
        tags: list[Tag],
        timeline: PageTimeline,
        version: PageVersion,
    ) -> None:
        conn = await asyncpg.connect(_dsn())
        try:
            async with conn.transaction():
                await self.save_raw_chunk(chunk, conn=conn)
                await self.save_page(page, conn=conn)
                saved_tags = await self.find_or_create_tags(tags, conn=conn)
                await self.assign_tags_to_page(
                    [PageTag(page_id=page.id, tag_id=t.id) for t in saved_tags if t.id],
                    conn=conn,
                )
                await self.insert_timeline_event(timeline, conn=conn)
                await self.insert_page_version(version, conn=conn)
        finally:
            await conn.close()
