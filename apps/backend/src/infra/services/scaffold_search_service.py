from domain.ports.search_port import SearchPort


class ScaffoldSearchService(SearchPort):
    def search(self, query: str) -> list[str]:
        raise NotImplementedError("Search adapter is intentionally not implemented in MVP scaffold.")
