from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class WorkspaceStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"


@dataclass
class Workspace:
    workspace_id: UUID
    name: str
    slug: str
    status: WorkspaceStatus
    created_at: datetime

    @staticmethod
    def create(name: str, slug: str) -> "Workspace":
        return Workspace(
            workspace_id=uuid4(),
            name=name,
            slug=slug,
            status=WorkspaceStatus.ACTIVE,
            created_at=datetime.now(UTC),
        )
