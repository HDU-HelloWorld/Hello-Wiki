from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.knowledge.catalog_vo import KnowledgeDomain
from src.domain.knowledge.entities import Tag


class KnowledgeCatalogPort(ABC):
    @abstractmethod
    async def list_domains(self, workspace_id: UUID) -> list[KnowledgeDomain]: ...

    @abstractmethod
    async def domain_exists(self, workspace_id: UUID, domain_id: str) -> bool: ...

    @abstractmethod
    async def upsert_domain(
        self,
        workspace_id: UUID,
        domain_id: str,
        *,
        label: str | None = None,
        description: str | None = None,
    ) -> None: ...

    @abstractmethod
    async def list_tags_for_domain(self, workspace_id: UUID, domain_id: str) -> list[Tag]: ...
