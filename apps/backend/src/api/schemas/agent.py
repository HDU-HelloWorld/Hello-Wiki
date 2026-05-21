from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[dict[str, str]] = Field(default_factory=list)


class AgentResponse(BaseModel):
    reply: str
