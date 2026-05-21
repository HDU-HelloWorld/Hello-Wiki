from langchain_core.tools import BaseTool, tool

from src.application.ingest.commands import IngestDocumentCommand
from src.application.ingest.handlers import IngestDocumentHandler


def create_ingest_tool(handler: IngestDocumentHandler) -> BaseTool:
    @tool
    async def ingest_document(file_path: str, domain: str = "general") -> str:
        """导入文档并提取结构化知识。

        将 PDF、Word、Markdown 或 TXT 文件导入知识库。
        系统会自动解析、分块、提取结构化知识并写入数据库。

        Args:
            file_path: 文档文件的完整路径
            domain: 知识领域，如 'general' 或 'university_policy'
        """
        command = IngestDocumentCommand(
            workspace_id="default",
            file_path=file_path,
            domain=domain,
        )
        result = await handler.handle(command)
        return (
            f"文档导入完成。\n"
            f"总块数: {result['total_chunks']}\n"
            f"成功: {result['successful']}\n"
            f"失败: {result['failed']}"
        )

    return ingest_document
