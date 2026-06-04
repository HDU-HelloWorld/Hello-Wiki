from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.knowledge.entities import Page, PageTag, PageTimeline, PageVersion, RawChunk, Tag


class KnowledgeRepositoryPort(ABC):
    """Async repository port for knowledge aggregates."""

    # -- RawChunk --
    @abstractmethod
    async def save_raw_chunk(self, chunk: RawChunk) -> UUID: ...

    @abstractmethod
    async def get_raw_chunk(self, chunk_id: UUID) -> RawChunk | None: ...

    # -- Page --
    @abstractmethod
    async def save_page(self, page: Page) -> UUID: ...

    @abstractmethod
    async def get_page(self, page_id: UUID) -> Page | None: ...

    # -- Tag --
    @abstractmethod
    async def find_or_create_tags(self, tags: list[Tag]) -> list[Tag]: ...

    @abstractmethod
    async def get_tags_for_domain(self, workspace_id: UUID, domain_id: str) -> list[Tag]: ...

    # -- PageTag --
    @abstractmethod
    async def assign_tags_to_page(self, page_tags: list[PageTag]) -> None: ...

    # -- PageTimeline --
    @abstractmethod
    async def insert_timeline_event(self, event: PageTimeline) -> UUID: ...

    # -- PageVersion --
    @abstractmethod
    async def insert_page_version(self, version: PageVersion) -> UUID: ...

    # -- Transactional --
    @abstractmethod
    async def transactional_extraction_persist(
        self,
        chunk: RawChunk,
        page: Page,
        tags: list[Tag],
        timeline: PageTimeline,
        version: PageVersion,
    ) -> None: ...
