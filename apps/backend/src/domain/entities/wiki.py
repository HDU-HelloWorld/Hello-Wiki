# -*- coding: utf-8 -*-
# 编码修复: wiki.py - 已替换Unicode符号避免Windows编码问题
from dataclasses import dataclass


@dataclass(frozen=True)
class WikiPageEntity:
    id: int | None
    workspace_id: str
    title: str
    status: str = "draft"
