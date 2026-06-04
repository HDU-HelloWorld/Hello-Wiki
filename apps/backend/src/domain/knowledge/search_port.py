from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.knowledge.catalog_vo import KnowledgePartition
from src.domain.knowledge.retrieve_vo import ScoredRow, SearchHit


class KnowledgeSearchPort(ABC):
    @abstractmethod
    async def search_by_tags(
        self, partition: KnowledgePartition, target_tags: list[str], limit: int
    ) -> list[ScoredRow]: ...

    @abstractmethod
    async def search_by_vector_pages(
        self, partition: KnowledgePartition, embedding: list[float], limit: int
    ) -> list[ScoredRow]: ...

    @abstractmethod
    async def search_by_vector_chunks(
        self, partition: KnowledgePartition, embedding: list[float], limit: int
    ) -> list[ScoredRow]: ...

    @abstractmethod
    async def search_by_fulltext(
        self, partition: KnowledgePartition, query: str, limit: int
    ) -> list[ScoredRow]: ...

    @abstractmethod
    async def search_by_time_range(
        self,
        partition: KnowledgePartition,
        start: datetime | None,
        end: datetime | None,
        limit: int,
    ) -> list[ScoredRow]: ...

    @abstractmethod
    async def fetch_hits_by_page_ids(
        self, partition: KnowledgePartition, page_ids: list[UUID]
    ) -> list[SearchHit]: ...

    @abstractmethod
    async def has_any_embeddings(self, partition: KnowledgePartition) -> bool: ...

    @abstractmethod
    async def update_page_embedding(self, page_id: UUID, embedding: list[float]) -> None: ...

    @abstractmethod
    async def update_chunk_embedding(self, chunk_id: UUID, embedding: list[float]) -> None: ...
