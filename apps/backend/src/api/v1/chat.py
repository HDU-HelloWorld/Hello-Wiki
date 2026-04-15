from __future__ import annotations

from collections.abc import Iterator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from src.api.deps import get_chat_ask_handler, get_chat_stream_handler, get_workspace_id
from src.api.schemas.chat import AskRequest, AskResponse
from src.application.chat.handlers import AskChatHandler, StreamChatHandler
from src.application.chat.queries import AskChatQuery, StreamChatQuery

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=AskResponse)
async def ask(
    request: AskRequest,
    workspace_id: UUID | None = Depends(get_workspace_id),
    handler: AskChatHandler = Depends(get_chat_ask_handler),
) -> AskResponse:
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    try:
        result = await handler.handle(
            AskChatQuery(
                workspace_id=workspace_id,
                question=request.question,
                top_k=request.top_k,
            )
        )
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=501,
            detail="chat ask endpoint is not implemented yet",
        ) from exc

    return AskResponse(answer=result.answer, citations=result.citations)


@router.post("/stream")
async def stream_ask(
    request: AskRequest,
    workspace_id: UUID | None = Depends(get_workspace_id),
    handler: StreamChatHandler = Depends(get_chat_stream_handler),
) -> StreamingResponse:
    if workspace_id is None:
        raise HTTPException(status_code=400, detail="workspace_id is required")

    events = await handler.handle(
        StreamChatQuery(
            workspace_id=workspace_id,
            question=request.question,
            top_k=request.top_k,
        )
    )

    def event_generator() -> Iterator[str]:
        yield from events

    return StreamingResponse(event_generator(), media_type="text/event-stream")
