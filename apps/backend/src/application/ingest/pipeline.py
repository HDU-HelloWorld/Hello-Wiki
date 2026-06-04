"""Ingest pipeline use case — 3-step orchestrator."""

from datetime import datetime
from typing import Protocol
from uuid import UUID, uuid4

from src.application.ingest.commands import IngestDocumentCommand
from src.application.ingest.embedding_service import EmbeddingBackfillService
from src.domain.knowledge.entities import (
    Page,
    PageTimeline,
    PageVersion,
    RawChunk,
    Tag,
)
from src.domain.knowledge.repository import KnowledgeRepositoryPort
from src.infrastructure.ai.extraction_adapter import ExtractedKnowledge, TsExtractionAdapter
from src.infrastructure.parser.chunker import RecursiveChunker
from src.infrastructure.parser.document_loader import DocumentLoaderAdapter


class ExtractionAdapterPort(Protocol):
    async def extract(
        self,
        domain: str,
        chunk_text: str,
        tag_tree: str,
        source_document: str = "",
        source_page: str = "",
        chunk_index: int = 0,
        total_chunks: int = 1,
    ) -> ExtractedKnowledge: ...


class IngestPipelineUseCase:
    """Three-step ingest pipeline:
    1. Parse document → text
    2. Chunk text → list of chunks
    3. For each chunk: LLM extract → persist to DB
    """

    def __init__(
        self,
        repository: KnowledgeRepositoryPort,
        extractor: ExtractionAdapterPort | None = None,
        chunk_size: int = 1500,
        chunk_overlap: int = 150,
        embedding_service: EmbeddingBackfillService | None = None,
    ) -> None:
        self._repo = repository
        self._loader = DocumentLoaderAdapter()
        self._chunker = RecursiveChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self._extractor = extractor or TsExtractionAdapter()
        self._embedding_service = embedding_service

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

        workspace_id = UUID(command.workspace_id)
        domain_id = command.domain

        for chunk_text, meta in chunks:
            try:
                tag_rows = await self._repo.get_tags_for_domain(workspace_id, domain_id)
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

                effective_range = _effective_range_tuple(extracted)
                chunk = RawChunk.create(
                    original_text=chunk_text,
                    workspace_id=workspace_id,
                    domain_id=domain_id,
                    summary=extracted.chunk_summary,
                    source_document=source_document,
                    source_page=str(meta.source_page or ""),
                    effective_range=effective_range,
                )
                page = Page.create(
                    raw_id=chunk.id,
                    workspace_id=workspace_id,
                    domain_id=domain_id,
                    title=extracted.page_title,
                    compiled_truth=extracted.compiled_truth,
                    effective_range=effective_range,
                )
                tags = [
                    Tag(
                        workspace_id=workspace_id,
                        domain_id=domain_id,
                        name=t.name,
                        label=t.label,
                        description=t.description,
                        level=t.parent_hint.count(".") + 1 if t.parent_hint else 0,
                        path=f"{t.parent_hint}.{t.name}" if t.parent_hint else t.name,
                        is_leaf=True,
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
                    page_state={
                        "title": page.title,
                        "effective_range": extracted.effective_range.model_dump(),
                    },
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
                if self._embedding_service is not None:
                    await self._embedding_service.backfill_page_and_chunk(
                        page_id=page.id,
                        chunk_id=chunk.id,
                        compiled_truth=page.compiled_truth,
                        summary=chunk.summary,
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


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _effective_range_tuple(
    extracted: ExtractedKnowledge,
) -> tuple[datetime | None, datetime | None] | None:
    start = _parse_date(extracted.effective_range.start)
    end = _parse_date(extracted.effective_range.end)
    if start is None and end is None:
        return None
    return (start, end)
