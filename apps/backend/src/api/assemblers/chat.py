from uuid import UUID

from src.api.schemas.chat import AskRequest, AskResponse
from src.application.chat.chat_executor import AskResult
from src.application.chat.queries import AskChatQuery, StreamChatQuery


def to_ask_chat_query(request: AskRequest, workspace_id: UUID) -> AskChatQuery:
    return AskChatQuery(
        workspace_id=workspace_id,
        question=request.question,
        top_k=request.top_k,
    )


def to_stream_chat_query(request: AskRequest, workspace_id: UUID) -> StreamChatQuery:
    return StreamChatQuery(
        workspace_id=workspace_id,
        question=request.question,
        top_k=request.top_k,
    )


def to_ask_response(result: AskResult) -> AskResponse:
    return AskResponse(answer=result.answer, citations=result.citations)
