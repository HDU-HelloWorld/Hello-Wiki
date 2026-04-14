# -*- coding: utf-8 -*-
# 编码修复: compile_port.py - 已替换Unicode符号避免Windows编码问题
from typing import Protocol


class CompilePort(Protocol):
    def enqueue_compile(self, source_uri: str) -> str: ...
