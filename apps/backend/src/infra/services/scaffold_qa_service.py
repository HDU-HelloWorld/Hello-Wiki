from domain.ports.qa_port import QAPort


class ScaffoldQAService(QAPort):
    def answer(self, question: str) -> str:
        raise NotImplementedError("QA adapter is intentionally not implemented in MVP scaffold.")
