from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from src.domain.knowledge.value_objects import ChunkStatus, EventType, PageStatus


@dataclass
class RawChunk:
    id: UUID
    original_text: str
    workspace_id: UUID | None = None
    domain_id: str = "general"
    source_id: str = "default"
    summary: str | None = None
    content_hash: str | None = None
    source_url: str | None = None
    source_page: str | None = None
    source_document: str | None = None
    extra_metadata: dict[str, Any] | None = None
    effective_range: tuple[datetime | None, datetime | None] | None = None
    status: ChunkStatus = ChunkStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, original_text: str, **kwargs: Any) -> "RawChunk":
        return cls(id=uuid4(), original_text=original_text, **kwargs)


@dataclass
class Tag:
    id: int | None = None
    workspace_id: UUID | None = None
    domain_id: str = "general"
    name: str = ""
    label: str = ""
    description: str = ""
    parent_id: int | None = None
    level: int = 0
    path: str = ""
    is_leaf: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create_category(cls, name: str, label: str, description: str = "") -> "Tag":
        return cls(
            name=name, label=label, description=description, level=0, path=name, is_leaf=False
        )

    @classmethod
    def create_leaf(cls, name: str, label: str, parent_path: str, description: str = "") -> "Tag":
        return cls(
            name=name,
            label=label,
            description=description,
            level=parent_path.count(".") + 1,
            path=f"{parent_path}.{name}",
            is_leaf=True,
        )


@dataclass
class PageTag:
    page_id: UUID
    tag_id: int
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PageTimeline:
    id: UUID
    page_id: UUID
    event_type: EventType
    summary: str
    event_at: datetime = field(default_factory=datetime.now)
    source_raw_id: UUID | None = None
    source_description: str | None = None

    @classmethod
    def create_creation_event(cls, page_id: UUID, source_description: str) -> "PageTimeline":
        return cls(
            id=uuid4(),
            page_id=page_id,
            event_type=EventType.CREATION,
            summary=f"Page created. {source_description[:100]}",
            source_description=source_description,
        )


@dataclass
class PageVersion:
    id: UUID
    page_id: UUID
    version: int
    compiled_truth: str
    timeline_id: UUID
    page_state: dict[str, Any] = field(default_factory=dict)
    timeline_state: dict[str, Any] = field(default_factory=dict)
    snapshot_at: datetime = field(default_factory=datetime.now)


@dataclass
class Page:
    """Page aggregate root."""

    id: UUID
    raw_id: UUID
    compiled_truth: str
    workspace_id: UUID | None = None
    domain_id: str = "general"
    title: str | None = None
    source_id: str = "default"
    open_threads: list[str] | None = None
    see_also: list[UUID] | None = None
    effective_range: tuple[datetime | None, datetime | None] | None = None
    status: PageStatus = PageStatus.ACTIVE
    version: int = 1
    last_timeline_id: UUID | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(
        cls,
        raw_id: UUID,
        compiled_truth: str,
        title: str | None = None,
        effective_range: tuple[datetime | None, datetime | None] | None = None,
        **kwargs: Any,
    ) -> "Page":
        return cls(
            id=uuid4(),
            raw_id=raw_id,
            compiled_truth=compiled_truth,
            title=title,
            effective_range=effective_range,
            **kwargs,
        )
