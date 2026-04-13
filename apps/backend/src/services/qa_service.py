from typing import Protocol


class QAService(Protocol):
    def answer(self, question: str) -> str: ...
