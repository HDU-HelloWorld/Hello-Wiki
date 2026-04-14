from typing import Protocol


class SearchPort(Protocol):
    def search(self, query: str) -> list[str]: ...
