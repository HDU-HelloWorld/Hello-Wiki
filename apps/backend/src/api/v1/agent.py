from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.deps import get_agent_handler, get_required_workspace_id
from src.api.schemas.agent import AgentRequest, AgentResponse
from src.application.agent.commands import AgentCommand
from src.application.agent.handlers import AgentHandler

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=AgentResponse)
async def agent_chat(
    request: AgentRequest,
    workspace_id: UUID = Depends(get_required_workspace_id),
    handler: AgentHandler = Depends(get_agent_handler),
) -> AgentResponse:
    command = AgentCommand(
        user_input=request.message,
        workspace_id=str(workspace_id),
        session_id=request.session_id,
        chat_history=request.history,
    )
    reply = await handler.handle(command)
    return AgentResponse(reply=reply, session_id=request.session_id)
