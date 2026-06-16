from src.application.agent.agent_loop import AgentLoop
from src.application.agent.commands import AgentCommand


class AgentHandler:
    """Application service wrapping the AgentLoop."""

    def __init__(self, agent_loop: AgentLoop) -> None:
        self._loop = agent_loop

    async def handle(self, command: AgentCommand) -> str:
        return await self._loop.run(command)
