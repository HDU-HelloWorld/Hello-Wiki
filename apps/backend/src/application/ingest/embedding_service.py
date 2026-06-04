from uuid import UUID

from src.domain.ai.embedding_port import EmbeddingPort
from src.domain.knowledge.search_port import KnowledgeSearchPort


class EmbeddingBackfillService:
    """Generate and persist embeddings for pages and raw chunks."""

    def __init__(
        self,
        embedding_port: EmbeddingPort,
        search_repo: KnowledgeSearchPort,
    ) -> None:
        self._embedding_port = embedding_port
        self._search_repo = search_repo

    async def backfill_page_and_chunk(
        self,
        *,
        page_id: UUID,
        chunk_id: UUID,
        compiled_truth: str,
        summary: str | None,
    ) -> None:
        truth_embedding = await self._embedding_port.embed(compiled_truth)
        await self._search_repo.update_page_embedding(page_id, truth_embedding)

        # Placeholder: summary_vector for future chunk-level retrieval (not in MVP RRF).
        if summary and summary.strip():
            summary_embedding = await self._embedding_port.embed(summary)
            await self._search_repo.update_chunk_embedding(chunk_id, summary_embedding)
