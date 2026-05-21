from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import BaseTool

from src.application.agent.commands import AgentCommand
from src.domain.ai.provider import LLMProviderPort

SYSTEM_PROMPT = """\
你是 Hello-Wiki 的知识库管理助手。你可以通过工具调用来帮助用户管理知识库。

你的职责:
- 初始化知识库标签体系 (init_tags)
- 导入文档并提取结构化知识 (ingest_document, 待实现)
- 回答关于知识库内容的问题 (search_knowledge, 待实现)

规则:
- 用户说"初始化标签"或"创建知识库"时,调用 init_tags
- 先询问用户知识库的领域和内容描述,再调用工具
- 工具返回结果后,用中文向用户总结
- 如果用户请求的功能尚未实现,如实告知
"""


class AgentLoop:
    """Main agent loop wrapping a LangChain create_agent graph."""

    def __init__(self, provider: LLMProviderPort, tools: list[BaseTool]) -> None:
        llm = provider.as_runnable()
        self._agent = create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)  # type: ignore[arg-type]

    async def run(self, command: AgentCommand) -> str:
        messages: list[BaseMessage] = []
        for h in command.chat_history or []:
            role = h.get("role", "")
            content = h.get("content", "")
            if role == "assistant":
                messages.append(AIMessage(content=content))
            else:
                messages.append(HumanMessage(content=content))
        messages.append(HumanMessage(content=command.user_input))
        result = await self._agent.ainvoke({"messages": messages})  # type: ignore[call-overload]
        last = result["messages"][-1]
        return str(last.content)
