from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.deps import get_execution_context, get_workspace_id
from src.api.schemas.workspace import WorkspaceContextResponse
from src.core.context import ExecutionContext

router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.get("/context", response_model=WorkspaceContextResponse)
def current_workspace(
    workspace_id: UUID = Depends(get_workspace_id),
    execution_context: ExecutionContext | None = Depends(get_execution_context),
) -> WorkspaceContextResponse:
    trace_id = (
        execution_context.trace_id
        if execution_context and execution_context.trace_id
        else "no-trace-id"
    )
    return WorkspaceContextResponse(workspace_id=workspace_id, trace_id=trace_id)
