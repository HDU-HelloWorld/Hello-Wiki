# -*- coding: utf-8 -*-
# 编码修复: wiki_application.py - 已替换Unicode符号避免Windows编码问题
from domain.entities.wiki import WikiPageEntity
from domain.ports.wiki_repository_port import WikiRepositoryPort
from domain.services.wiki_domain_service import WikiDomainService


class WikiApplicationService:
    def __init__(self, repository: WikiRepositoryPort, domain_service: WikiDomainService) -> None:
        self._repository = repository
        self._domain_service = domain_service

    def list_pages(self, workspace_id: str) -> list[WikiPageEntity]:
        try:
            pages = self._repository.list_pages(workspace_id)
            return self._domain_service.filter_accessible_pages(pages)
        except NotImplementedError:
            return []
