from uuid import UUID

from src.core.observability import start_observability_span
from src.domain.wiki.entities import WikiFact, WikiPage, WikiParseReference, WikiStatus
from src.infrastructure.storage.file_system import JsonFileStore


class FileSystemWikiRepository:
    def __init__(self, base_path: str) -> None:
        self._store = JsonFileStore(base_path)
        self._index_file = "wiki/index.json"

    def upsert(self, page: WikiPage) -> WikiPage:
        pages = self.list_by_workspace(page.workspace_id)
        replaced = False

        for idx, existing in enumerate(pages):
            same_id = existing.wiki_id == page.wiki_id
            same_title = existing.title == page.title
            if same_id or same_title:
                page = WikiPage.create_or_update(
                    workspace_id=page.workspace_id,
                    title=page.title,
                    category=page.category,
                    summary=page.summary,
                    content=page.content,
                    facts=page.facts,
                    parse_references=page.parse_references,
                    status=page.status,
                    existing_id=existing.wiki_id,
                )
                pages[idx] = page
                replaced = True
                break

        if not replaced:
            pages.append(page)

        self._save_workspace_pages(page.workspace_id, pages)
        return page

    def get_by_id(self, workspace_id: UUID, wiki_id: UUID) -> WikiPage | None:
        for page in self.list_by_workspace(workspace_id):
            if page.wiki_id == wiki_id:
                return page
        return None

    def get_by_title(self, workspace_id: UUID, title: str) -> WikiPage | None:
        for page in self.list_by_workspace(workspace_id):
            if page.title == title:
                return page
        return None

    def list_by_workspace(self, workspace_id: UUID) -> list[WikiPage]:
        with start_observability_span(
            "llamaindex.repository",
            "filesystem.list_by_workspace",
            workspace_id=workspace_id,
            extra_attributes={
                "llamaindex.repository.name": "filesystem_wiki_repository",
                "llamaindex.repository.index_file": self._index_file,
                "llamaindex.repository.workspace_id": str(workspace_id),
            },
        ):
            index_payload = self._store.read_json(self._index_file)
            workspace_raw = index_payload.get(str(workspace_id), [])
            if not isinstance(workspace_raw, list):
                return []

            pages: list[WikiPage] = []
            for item in workspace_raw:
                if isinstance(item, dict):
                    pages.append(self._deserialize(item))
            return pages

    def delete(self, workspace_id: UUID, wiki_id: UUID) -> bool:
        pages = self.list_by_workspace(workspace_id)
        remaining = [page for page in pages if page.wiki_id != wiki_id]
        if len(remaining) == len(pages):
            return False

        self._save_workspace_pages(workspace_id, remaining)
        return True

    def count_by_workspace(self, workspace_id: UUID) -> int:
        return len(self.list_by_workspace(workspace_id))

    def _save_workspace_pages(self, workspace_id: UUID, pages: list[WikiPage]) -> None:
        index_payload = self._store.read_json(self._index_file)
        index_payload[str(workspace_id)] = [self._serialize(page) for page in pages]
        self._store.write_json(self._index_file, index_payload)

    @staticmethod
    def _serialize(page: WikiPage) -> dict[str, object]:
        return {
            "wiki_id": str(page.wiki_id),
            "workspace_id": str(page.workspace_id),
            "title": page.title,
            "category": page.category,
            "summary": page.summary,
            "content": page.content,
            "status": page.status.value,
            "updated_at": page.updated_at.isoformat(),
            "facts": [
                {
                    "key": fact.key,
                    "value": fact.value,
                    "confidence": fact.confidence,
                }
                for fact in page.facts
            ],
            "parse_references": [
                {
                    "source_document_id": ref.source_document_id,
                    "reference_type": ref.reference_type,
                }
                for ref in page.parse_references
            ],
        }

    @staticmethod
    def _deserialize(data: dict[str, object]) -> WikiPage:
        facts_raw = data.get("facts", [])
        references_raw = data.get("parse_references", [])
        facts_data = facts_raw if isinstance(facts_raw, list) else []
        references_data = references_raw if isinstance(references_raw, list) else []

        facts = [
            WikiFact(
                key=str(item["key"]),
                value=str(item["value"]),
                confidence=float(item["confidence"]),
            )
            for item in facts_data
            if isinstance(item, dict)
        ]
        references = [
            WikiParseReference(
                source_document_id=str(item["source_document_id"]),
                reference_type=str(item["reference_type"]),
            )
            for item in references_data
            if isinstance(item, dict)
        ]

        return WikiPage(
            wiki_id=UUID(str(data["wiki_id"])),
            workspace_id=UUID(str(data["workspace_id"])),
            title=str(data["title"]),
            category=str(data["category"]),
            summary=str(data["summary"]),
            content=str(data["content"]),
            status=WikiStatus(str(data["status"])),
            facts=facts,
            parse_references=references,
        )
