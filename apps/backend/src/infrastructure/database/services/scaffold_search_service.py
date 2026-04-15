# -*- coding: utf-8 -*-
# 编码修复: scaffold_search_service.py - 已替换Unicode符号避免Windows编码问题
from domain.ports.search_port import SearchPort


class ScaffoldSearchService(SearchPort):
    def search(self, query: str) -> list[str]:
        raise NotImplementedError("Search adapter is intentionally not implemented in MVP scaffold.")
