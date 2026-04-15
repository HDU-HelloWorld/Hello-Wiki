from collections.abc import Iterator

from src.application.chat.chat_executor import AskResult, ChatExecutor
from src.application.chat.queries import AskChatQuery, StreamChatQuery
from src.application.chat.stream_handler import sse_event


class AskChatHandler:
    """Chat 读路径应用服务（Query Handler）。"""

    def __init__(self, executor: ChatExecutor) -> None:
        self._executor = executor

    async def handle(self, query: AskChatQuery) -> AskResult:
        return await self._executor.ask(query)


class StreamChatHandler:
    """Chat SSE 读路径应用服务（Query Handler）。"""

    def __init__(self, executor: ChatExecutor) -> None:
        self._executor = executor

    async def handle(self, query: StreamChatQuery) -> Iterator[str]:
        # 当前仍是占位流，后续可替换为真实 token streaming。
        return iter(
            [
                sse_event("start", {"workspace_id": str(query.workspace_id)}),
                sse_event("end", {"done": True}),
            ]
        )
