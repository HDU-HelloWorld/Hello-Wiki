# -*- coding: utf-8 -*-
# 编码修复: __init__.py - 已替换Unicode符号避免Windows编码问题
"""Async worker layer and task orchestration boundaries."""

from workers.tasks import register_tasks

__all__ = ["register_tasks"]
