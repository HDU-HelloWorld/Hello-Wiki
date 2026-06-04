from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

import pytest

from src.application.ingest.commands import IngestDocumentCommand
from src.application.ingest.pipeline import IngestPipelineUseCase
from src.domain.knowledge.entities import Page, PageTag, PageTimeline, PageVersion, RawChunk, Tag
from src.domain.knowledge.repository import KnowledgeRepositoryPort
from src.infrastructure.ai.extraction_adapter import (
    EffectiveRange,
    ExtractedKnowledge,
    SuggestedTag,
)


class FakeKnowledgeRepository(KnowledgeRepositoryPort):
    def __init__(self) -> None:
        self.chunk: RawChunk | None = None
        self.page: Page | None = None
        self.tags: list[Tag] = []
        self.timeline: PageTimeline | None = None
        self.version: PageVersion | None = None

    async def save_raw_chunk(self, chunk: RawChunk) -> UUID:
        self.chunk = chunk
        return chunk.id

    async def get_raw_chunk(self, chunk_id: UUID) -> RawChunk | None:
        return self.chunk if self.chunk and self.chunk.id == chunk_id else None

    async def save_page(self, page: Page) -> UUID:
        self.page = page
        return page.id

    async def get_page(self, page_id: UUID) -> Page | None:
        return self.page if self.page and self.page.id == page_id else None

    async def find_or_create_tags(self, tags: list[Tag]) -> list[Tag]:
        self.tags = tags
        return [Tag(id=index + 1, name=tag.name, label=tag.label) for index, tag in enumerate(tags)]

    async def get_tags_for_domain(self, workspace_id, domain_id: str) -> list[Tag]:  # noqa: ANN001
        return [
            Tag(name="functional_area", label="Functional Area", level=0, is_leaf=False),
            Tag(name="registration_course", label="选课注册", level=1, is_leaf=True),
        ]

    async def assign_tags_to_page(self, page_tags: list[PageTag]) -> None:
        return None

    async def insert_timeline_event(self, event: PageTimeline) -> UUID:
        self.timeline = event
        return event.id

    async def insert_page_version(self, version: PageVersion) -> UUID:
        self.version = version
        return version.id

    async def transactional_extraction_persist(
        self,
        chunk: RawChunk,
        page: Page,
        tags: list[Tag],
        timeline: PageTimeline,
        version: PageVersion,
    ) -> None:
        self.chunk = chunk
        self.page = page
        self.tags = tags
        self.timeline = timeline
        self.version = version


@dataclass
class FakeExtractor:
    async def extract(
        self,
        domain: str,
        chunk_text: str,
        tag_tree: str,
        source_document: str = "",
        source_page: str = "",
        chunk_index: int = 0,
        total_chunks: int = 1,
    ) -> ExtractedKnowledge:
        return ExtractedKnowledge(
            chunk_summary=f"summary:{domain}:{chunk_index}/{total_chunks}",
            page_title="Course Registration",
            compiled_truth="Students may register for courses.",
            suggested_tags=[
                SuggestedTag(
                    name="registration_course",
                    label="选课注册",
                    parent_hint="functional_area",
                ),
                SuggestedTag(
                    name="academic_affairs",
                    label="教务管理",
                    parent_hint="functional_area",
                ),
            ],
            effective_range=EffectiveRange(
                start="2024-09-01",
                end=None,
                description="2024 academic year",
                stale_risk="medium",
            ),
        )


def test_ingest_pipeline_uses_documented_chunk_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, int] = {}

    class CapturingChunker:
        def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
            captured["chunk_size"] = chunk_size
            captured["chunk_overlap"] = chunk_overlap

    monkeypatch.setattr("src.application.ingest.pipeline.RecursiveChunker", CapturingChunker)

    IngestPipelineUseCase(repository=FakeKnowledgeRepository(), extractor=FakeExtractor())

    assert captured == {"chunk_size": 1500, "chunk_overlap": 150}


@pytest.mark.asyncio
async def test_ingest_pipeline_maps_effective_range_to_entities(tmp_path: Path) -> None:
    source = tmp_path / "policy.txt"
    source.write_text("Students may register for courses.", encoding="utf-8")
    repo = FakeKnowledgeRepository()
    pipeline = IngestPipelineUseCase(repository=repo, extractor=FakeExtractor())

    result = await pipeline.execute(
        IngestDocumentCommand(
            workspace_id="00000000-0000-0000-0000-000000000001",
            file_path=str(source),
            domain="general",
        )
    )

    assert result["successful"] == 1
    assert repo.chunk is not None
    assert repo.page is not None
    assert repo.version is not None
    assert repo.chunk.effective_range is not None
    assert repo.page.effective_range is not None
    assert repo.chunk.effective_range[0] is not None
    assert repo.chunk.effective_range[0].isoformat().startswith("2024-09-01")
    assert repo.version.page_state["effective_range"]["start"] == "2024-09-01"
