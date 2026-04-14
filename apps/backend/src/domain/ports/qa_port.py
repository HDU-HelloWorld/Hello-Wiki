# -*- coding: utf-8 -*-
# 编码修复: qa_port.py - 已替换Unicode符号避免Windows编码问题
from typing import Protocol


class QAPort(Protocol):
    def answer(self, question: str) -> str: ...
