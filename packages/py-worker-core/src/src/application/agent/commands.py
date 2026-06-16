from dataclasses import dataclass


@dataclass(frozen=True)
class AgentCommand:
    user_input: str
    workspace_id: str = "default"
    session_id: str = "default"
    chat_history: list[dict[str, str]] | None = None
