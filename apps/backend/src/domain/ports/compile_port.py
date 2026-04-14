from typing import Protocol


class CompilePort(Protocol):
    def enqueue_compile(self, source_uri: str) -> str: ...
