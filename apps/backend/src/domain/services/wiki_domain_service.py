# -*- coding: utf-8 -*-
# 编码修复: wiki_domain_service.py - 已替换Unicode符号避免Windows编码问题
from domain.entities.wiki import WikiPageEntity


class WikiDomainService:
    """Domain-level wiki rules independent from transport and infrastructure."""

    def filter_accessible_pages(self, pages: list[WikiPageEntity]) -> list[WikiPageEntity]:
        return [page for page in pages if page.status != "archived"]
