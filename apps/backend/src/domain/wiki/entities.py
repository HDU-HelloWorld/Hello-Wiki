from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class WikiStatus(StrEnum):
    ARCHIVED = "ARCHIVED"
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    DISPUTED = "DISPUTED"


class ReferenceType(StrEnum):
    DIRECT = "DIRECT"
    INFERRED = "INFERRED"
    CONFLICT = "CONFLICT"


@dataclass
class WikiFact:
    key: str
    value: str
    confidence: float


@dataclass
class WikiParseReference:
    source_document_id: str
    reference_type: str = ReferenceType.DIRECT


@dataclass
class WikiPage:
    wiki_id: UUID
    workspace_id: UUID
    title: str
    category: str
    summary: str
    content: str
    status: WikiStatus
    facts: list[WikiFact] = field(default_factory=list)
    parse_references: list[WikiParseReference] = field(default_factory=list)
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @staticmethod
    def create_or_update(
        workspace_id: UUID,
        title: str,
        category: str,
        summary: str,
        content: str,
        facts: list[WikiFact],
        parse_references: list[WikiParseReference],
        status: WikiStatus,
        existing_id: UUID | None = None,
    ) -> "WikiPage":
        return WikiPage(
            wiki_id=existing_id or uuid4(),
            workspace_id=workspace_id,
            title=title,
            category=category,
            summary=summary,
            content=content,
            facts=facts,
            parse_references=parse_references,
            status=status,
            updated_at=datetime.now(UTC),
        )
