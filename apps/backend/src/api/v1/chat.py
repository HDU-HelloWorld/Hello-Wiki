from __future__ import annotations

from collections.abc import Iterator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from src.api.deps import get_workspace_id
from src.api.schemas.chat import AskRequest, AskResponse

router = APIRouter(prefix="/chat", tags=["chat"])


def _format_sse_event(event: str, data: dict[str, object]) -> str:
    """框架层 SSE 事件格式化工具（占位实现）。"""
    import json

    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    workspace_id: UUID = Depends(get_workspace_id),
) -> AskResponse:
    # 占位：保留接口示例，不包含业务实现。
    raise HTTPException(status_code=501, detail="chat ask endpoint is not implemented yet")


@router.post("/stream")
def stream_ask(
    request: AskRequest,
    workspace_id: UUID = Depends(get_workspace_id),
) -> StreamingResponse:
    def event_generator() -> Iterator[str]:
        # 占位流示例：仅演示 SSE 结构。
        yield _format_sse_event("start", {"workspace_id": str(workspace_id)})
        yield _format_sse_event("end", {"done": True})

    return StreamingResponse(event_generator(), media_type="text/event-stream")
