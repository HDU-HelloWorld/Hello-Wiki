from src.core.observability import start_observability_span
from src.domain.wiki.entities import WikiPage


class KeywordSearchEngine:
    def search(self, pages: list[WikiPage], keyword: str, top_k: int) -> list[WikiPage]:
        with start_observability_span(
            "llamaindex.search_engine",
            "keyword.search",
            extra_attributes={
                "llamaindex.search_engine.keyword": keyword,
                "llamaindex.search_engine.top_k": top_k,
                "llamaindex.search_engine.page_count": len(pages),
            },
        ):
            # 占位：后续接入真实 BM25/索引检索策略。
            return []
