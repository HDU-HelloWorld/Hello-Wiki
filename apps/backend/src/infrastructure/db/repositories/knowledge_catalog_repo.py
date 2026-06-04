from __future__ import annotations

from uuid import UUID

import asyncpg

from src.core.config import settings
from src.domain.knowledge.catalog_port import KnowledgeCatalogPort
from src.domain.knowledge.catalog_vo import KnowledgeDomain
from src.domain.knowledge.entities import Tag


def _dsn() -> str:
    return settings.DATABASE_URL.replace("+asyncpg", "")


async def upsert_knowledge_domain_on_connection(
    conn: asyncpg.Connection,
    workspace_id: UUID,
    domain_id: str,
    *,
    label: str | None = None,
    description: str | None = None,
) -> None:
    """Ensure domain row exists before tag inserts (FK on tags)."""
    await conn.execute(
        """
        INSERT INTO knowledge_domains (
            workspace_id, domain_id, label, description, initialized_at
        )
        VALUES ($1, $2, $3, $4, NULL)
        ON CONFLICT (workspace_id, domain_id) DO UPDATE SET
            label = COALESCE(EXCLUDED.label, knowledge_domains.label),
            description = COALESCE(
                EXCLUDED.description, knowledge_domains.description
            )
        """,
        workspace_id,
        domain_id,
        label or domain_id,
        description,
    )


async def mark_knowledge_domain_initialized(
    conn: asyncpg.Connection,
    workspace_id: UUID,
    domain_id: str,
) -> None:
    await conn.execute(
        """
        UPDATE knowledge_domains
        SET initialized_at = COALESCE(initialized_at, now())
        WHERE workspace_id = $1 AND domain_id = $2
        """,
        workspace_id,
        domain_id,
    )


class KnowledgeCatalogRepository(KnowledgeCatalogPort):
    async def list_domains(self, workspace_id: UUID) -> list[KnowledgeDomain]:
        conn = await asyncpg.connect(_dsn())
        try:
            rows = await conn.fetch(
                """
                SELECT domain_id, label, initialized_at
                FROM knowledge_domains
                WHERE workspace_id = $1
                ORDER BY domain_id
                """,
                workspace_id,
            )
        finally:
            await conn.close()

        return [
            KnowledgeDomain(
                domain_id=row["domain_id"],
                label=row["label"],
                initialized=row["initialized_at"] is not None,
            )
            for row in rows
        ]

    async def domain_exists(self, workspace_id: UUID, domain_id: str) -> bool:
        conn = await asyncpg.connect(_dsn())
        try:
            row = await conn.fetchrow(
                """
                SELECT 1
                FROM knowledge_domains
                WHERE workspace_id = $1 AND domain_id = $2
                """,
                workspace_id,
                domain_id,
            )
        finally:
            await conn.close()
        return row is not None

    async def upsert_domain(
        self,
        workspace_id: UUID,
        domain_id: str,
        *,
        label: str | None = None,
        description: str | None = None,
    ) -> None:
        conn = await asyncpg.connect(_dsn())
        try:
            async with conn.transaction():
                await upsert_knowledge_domain_on_connection(
                    conn,
                    workspace_id,
                    domain_id,
                    label=label,
                    description=description,
                )
                await mark_knowledge_domain_initialized(conn, workspace_id, domain_id)
        finally:
            await conn.close()

    async def list_tags_for_domain(self, workspace_id: UUID, domain_id: str) -> list[Tag]:
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
        finally:
            await conn.close()

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
