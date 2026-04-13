from typing import Protocol


class SearchService(Protocol):
    def search(self, query: str) -> list[str]: ...
