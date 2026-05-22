# -*- coding: utf-8 -*-
# 编码修复: scaffold_qa_service.py - 已替换Unicode符号避免Windows编码问题
from domain.ports.qa_port import QAPort


class ScaffoldQAService(QAPort):
    def answer(self, question: str) -> str:
        raise NotImplementedError("QA adapter is intentionally not implemented in MVP scaffold.")
