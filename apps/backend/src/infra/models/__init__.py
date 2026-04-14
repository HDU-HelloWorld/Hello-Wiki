# -*- coding: utf-8 -*-
# 编码修复: __init__.py - 已替换Unicode符号避免Windows编码问题
from infra.models.models import ParsingResultDB, WikiPageDB

__all__ = ["WikiPageDB", "ParsingResultDB"]