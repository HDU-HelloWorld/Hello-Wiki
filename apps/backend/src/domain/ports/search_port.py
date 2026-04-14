# -*- coding: utf-8 -*-
# 编码修复: search_port.py - 已替换Unicode符号避免Windows编码问题
from typing import Protocol


class SearchPort(Protocol):
    def search(self, query: str) -> list[str]: ...
