"""Backfill truth_embedding and summary_vector for existing knowledge rows."""

import asyncio

import asyncpg

from src.application.ingest.embedding_service import EmbeddingBackfillService
from src.core.config import settings
from src.infrastructure.ai.embedding_adapter import OpenAICompatibleEmbeddingAdapter
from src.infrastructure.db.repositories.knowledge_search_repo import KnowledgeSearchRepository


def _dsn() -> str:
    return settings.DATABASE_URL.replace("+asyncpg", "")


async def _backfill() -> None:
    service = EmbeddingBackfillService(
        embedding_port=OpenAICompatibleEmbeddingAdapter(),
        search_repo=KnowledgeSearchRepository(),
    )
    conn = await asyncpg.connect(_dsn())
    try:
        rows = await conn.fetch(
            """
            SELECT p.id AS page_id,
                   rc.id AS chunk_id,
                   p.compiled_truth,
                   rc.summary
            FROM pages p
            JOIN raw_chunks rc ON rc.id = p.raw_id
            WHERE p.deleted_at IS NULL
              AND (
                p.truth_embedding IS NULL
                OR rc.summary_vector IS NULL
              )
            """
        )
    finally:
        await conn.close()

    for row in rows:
        await service.backfill_page_and_chunk(
            page_id=row["page_id"],
            chunk_id=row["chunk_id"],
            compiled_truth=row["compiled_truth"],
            summary=row["summary"],
        )
        print(f"backfilled page={row['page_id']} chunk={row['chunk_id']}")

    print(f"done: {len(rows)} rows")


def main() -> None:
    asyncio.run(_backfill())


if __name__ == "__main__":
    main()
