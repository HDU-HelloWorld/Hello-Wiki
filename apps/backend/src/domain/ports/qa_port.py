from typing import Protocol


class QAPort(Protocol):
    def answer(self, question: str) -> str: ...
