from typing import Protocol


class CompileService(Protocol):
    def enqueue_compile(self, source_uri: str) -> str: ...
