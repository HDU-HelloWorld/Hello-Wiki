from src.domain.wiki.entities import WikiPage


class RuleBasedLLMAdapter:
    """LLM 适配器骨架示例。"""

    async def answer(self, question: str, context_pages: list[WikiPage]) -> str:
        # 占位：后续接入真实模型调用和提示词策略。
        return "llm adapter placeholder response"
