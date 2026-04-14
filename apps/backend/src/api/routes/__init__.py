# -*- coding: utf-8 -*-
# 编码修复: __init__.py - 已替换Unicode符号避免Windows编码问题
"""API route modules."""

from . import compile, health, qa, root, wiki

__all__ = ["root", "health", "wiki", "compile", "qa"]
