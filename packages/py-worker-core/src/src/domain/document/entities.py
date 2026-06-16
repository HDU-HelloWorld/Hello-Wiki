from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class DocStatus(StrEnum):
    UPLOADED = "UPLOADED"
    PARSING = "PARSING"
    PARSED = "PARSED"
    COMPILING = "COMPILING"
    COMPILED = "COMPILED"
    FAILED = "FAILED"


@dataclass
class RawDocument:
    doc_id: UUID
    workspace_id: UUID
    origin_name: str
    file_hash: str
    file_size: int
    status: DocStatus
    created_at: datetime

    @staticmethod
    def create(
        workspace_id: UUID, origin_name: str, file_hash: str, file_size: int
    ) -> "RawDocument":
        return RawDocument(
            doc_id=uuid4(),
            workspace_id=workspace_id,
            origin_name=origin_name,
            file_hash=file_hash,
            file_size=file_size,
            status=DocStatus.UPLOADED,
            created_at=datetime.now(UTC),
        )
