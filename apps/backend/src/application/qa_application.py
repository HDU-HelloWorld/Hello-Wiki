# -*- coding: utf-8 -*-
# 编码修复: qa_application.py - 已替换Unicode符号避免Windows编码问题
from domain.ports.qa_port import QAPort


class QAApplicationService:
    def __init__(self, qa_port: QAPort) -> None:
        self._qa_port = qa_port

    def ask(self, question: str) -> str:
        try:
            return self._qa_port.answer(question)
        except NotImplementedError:
            return "MVP scaffold only, QA workflow is not implemented."
