from uuid import UUID

from src.domain.knowledge.catalog_port import KnowledgeCatalogPort
from src.infrastructure.db.repositories.tag_serializer import TagRow, serialize_tag_tree


class ListRetrieveDomainsHandler:
    def __init__(self, catalog: KnowledgeCatalogPort) -> None:
        self._catalog = catalog

    async def handle(self, workspace_id: UUID) -> tuple[list[dict[str, object]], int]:
        domains = await self._catalog.list_domains(workspace_id)
        items = [
            {
                "id": d.domain_id,
                "label": d.label or d.domain_id,
                "initialized": d.initialized,
            }
            for d in domains
        ]
        return items, len(items)


class GetDomainTagTreeHandler:
    def __init__(self, catalog: KnowledgeCatalogPort) -> None:
        self._catalog = catalog

    async def handle(self, workspace_id: UUID, domain_id: str) -> str | None:
        if not await self._catalog.domain_exists(workspace_id, domain_id):
            return None
        tags = await self._catalog.list_tags_for_domain(workspace_id, domain_id)
        rows = [TagRow(name=t.name, label=t.label, level=t.level, is_leaf=t.is_leaf) for t in tags]
        return serialize_tag_tree(rows)
