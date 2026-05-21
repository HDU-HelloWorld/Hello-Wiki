from dataclasses import dataclass


@dataclass(frozen=True)
class AgentCommand:
    user_input: str
    chat_history: list[dict[str, str]] | None = None
