from langchain_core.tools import BaseTool, tool

from src.application.init.commands import InitTagsCommand
from src.application.init.handlers import InitTagsHandler


def create_init_tags_tool(handler: InitTagsHandler) -> BaseTool:
    @tool
    async def init_tags(domain: str, description: str, language: str = "zh") -> str:
        """初始化知识库标签体系。

        在创建新知识库时调用此工具。根据领域描述生成多维度层级标签树，
        包括文档类型、适用对象、职能领域、时效性等维度。

        Args:
            domain: 领域标识符，如 'general' 或 'university_policy'
            description: 知识库内容描述，例如 "中国高校行政管理制度"
            language: 标签语言，默认 'zh'
        """
        command = InitTagsCommand(domain=domain, description=description, language=language)
        result = await handler.handle(command)
        total_leaves = sum(len(c.leaves) for c in result.categories)
        return (
            f"标签初始化完成。\n"
            f"领域: {result.domain}\n"
            f"分类维度: {len(result.categories)} 个\n"
            f"叶子标签: {total_leaves} 个\n"
            f"维度列表: {', '.join(c.label for c in result.categories)}"
        )

    return init_tags
