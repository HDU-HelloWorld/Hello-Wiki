from domain.entities.wiki import WikiPageEntity


class WikiDomainService:
    """Domain-level wiki rules independent from transport and infrastructure."""

    def filter_accessible_pages(self, pages: list[WikiPageEntity]) -> list[WikiPageEntity]:
        return [page for page in pages if page.status != "archived"]
