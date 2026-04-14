# -*- coding: utf-8 -*-
# 编码修复: wiki_repository_port.py - 已替换Unicode符号避免Windows编码问题
from typing import Protocol

from domain.entities.wiki import WikiPageEntity


class WikiRepositoryPort(Protocol):
    def list_pages(self, workspace_id: str) -> list[WikiPageEntity]: ...
