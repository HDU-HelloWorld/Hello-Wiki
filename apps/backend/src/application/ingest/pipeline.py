"""Ingest pipeline use case — 3-step orchestrator."""

from uuid import uuid4

from src.application.ingest.commands import IngestDocumentCommand
from src.domain.ai.provider import LLMProviderPort
from src.domain.knowledge.entities import (
    Page,
    PageTimeline,
    PageVersion,
    RawChunk,
    Tag,
)
from src.domain.knowledge.repository import KnowledgeRepositoryPort
from src.infrastructure.ai.extraction_adapter import StructuredExtractionAdapter
from src.infrastructure.parser.chunker import RecursiveChunker
from src.infrastructure.parser.document_loader import DocumentLoaderAdapter


class IngestPipelineUseCase:
    """Three-step ingest pipeline:
    1. Parse document → text
    2. Chunk text → list of chunks
    3. For each chunk: LLM extract → persist to DB
    """

    def __init__(
        self,
        provider: LLMProviderPort,
        repository: KnowledgeRepositoryPort,
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
    ) -> None:
        self._provider = provider
        self._repo = repository
        self._loader = DocumentLoaderAdapter()
        self._chunker = RecursiveChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self._extractor = StructuredExtractionAdapter(provider)

    async def execute(self, command: IngestDocumentCommand) -> dict[str, object]:
        texts = self._loader.load(command.file_path)
        raw_text = "\n".join(texts)
        source_document = command.file_path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        print(f"[pipeline] file={source_document} pages={len(texts)} chars={len(raw_text)}")
        if not raw_text.strip():
            return {
                "total_chunks": 0,
                "successful": 0,
                "failed": 0,
                "results": [],
                "errors": [{"error": "PDF contained no extractable text (scanned document?)"}],
            }

        chunks = self._chunker.split(raw_text, source_document=source_document)
        total = len(chunks)
        results: list[dict[str, object]] = []
        errors: list[dict[str, object]] = []

        for chunk_text, meta in chunks:
            try:
                tag_rows = await self._repo.get_all_tags_ordered_by_path()
                tag_tree = _serialize(tag_rows)

                extracted = await self._extractor.extract(
                    domain=command.domain,
                    chunk_text=chunk_text,
                    tag_tree=tag_tree,
                    source_document=source_document,
                    source_page=str(meta.source_page or ""),
                    chunk_index=meta.chunk_index,
                    total_chunks=total,
                )

                chunk = RawChunk.create(
                    original_text=chunk_text,
                    summary=extracted.chunk_summary,
                    source_document=source_document,
                    source_page=str(meta.source_page or ""),
                )
                page = Page.create(
                    raw_id=chunk.id,
                    title=extracted.page_title,
                    compiled_truth=extracted.compiled_truth,
                )
                tags = [
                    Tag.create_leaf(
                        name=t.name,
                        label=t.label,
                        parent_path=t.parent_hint,
                        description=t.description,
                    )
                    for t in extracted.suggested_tags
                ]
                timeline = PageTimeline.create_creation_event(
                    page_id=page.id,
                    source_description=extracted.chunk_summary,
                )
                version = PageVersion(
                    id=uuid4(),
                    page_id=page.id,
                    version=1,
                    compiled_truth=extracted.compiled_truth,
                    timeline_id=timeline.id,
                    page_state={"title": page.title},
                    timeline_state={
                        "event_type": timeline.event_type.value,
                        "summary": timeline.summary,
                    },
                )
                await self._repo.transactional_extraction_persist(
                    chunk,
                    page,
                    tags,
                    timeline,
                    version,
                )
                results.append({"chunk_index": meta.chunk_index, "page_id": str(page.id)})
            except Exception as exc:
                errors.append({"chunk_index": meta.chunk_index, "error": str(exc)})

        return {
            "total_chunks": total,
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors,
        }


def _serialize(tags: list[Tag]) -> str:
    from src.infrastructure.db.repositories.tag_serializer import (
        TagRow,
        serialize_tag_tree,
    )

    rows = [TagRow(name=t.name, label=t.label, level=t.level, is_leaf=t.is_leaf) for t in tags]
    return serialize_tag_tree(rows)
