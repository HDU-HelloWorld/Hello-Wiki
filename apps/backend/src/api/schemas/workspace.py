from uuid import UUID

from pydantic import BaseModel


class WorkspaceContextResponse(BaseModel):
    workspace_id: UUID
    trace_id: str
