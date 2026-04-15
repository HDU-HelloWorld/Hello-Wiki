from __future__ import annotations

from collections.abc import Iterator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from src.api.assemblers.chat import (
    to_ask_chat_query,
    to_ask_response,
    to_stream_chat_query,
)
from src.api.deps import (
    get_chat_ask_handler,
    get_chat_stream_handler,
    get_required_workspace_id,
)
from src.api.schemas.chat import AskRequest, AskResponse
from src.application.chat.handlers import AskChatHandler, StreamChatHandler

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=AskResponse)
async def ask(
    request: AskRequest,
    workspace_id: UUID = Depends(get_required_workspace_id),
    handler: AskChatHandler = Depends(get_chat_ask_handler),
) -> AskResponse:
    try:
        result = await handler.handle(to_ask_chat_query(request=request, workspace_id=workspace_id))
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=501,
            detail="chat ask endpoint is not implemented yet",
        ) from exc

    return to_ask_response(result)


@router.post("/stream")
async def stream_ask(
    request: AskRequest,
    workspace_id: UUID = Depends(get_required_workspace_id),
    handler: StreamChatHandler = Depends(get_chat_stream_handler),
) -> StreamingResponse:
    events = await handler.handle(to_stream_chat_query(request=request, workspace_id=workspace_id))

    def event_generator() -> Iterator[str]:
        yield from events

    return StreamingResponse(event_generator(), media_type="text/event-stream")
