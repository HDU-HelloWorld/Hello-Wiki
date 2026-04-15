"""Wiki Repository Protocol - 定义 CQRS 风格的数据访问接口。"""

from typing import Protocol
from uuid import UUID

from src.domain.wiki.entities import WikiPage


class WikiCommandRepositoryPort(Protocol):
    """Wiki 写路径仓储接口（Command Port）。

    应用层 Command Handler 通过该接口完成状态变更与写入。
    """

    async def upsert(self, page: WikiPage) -> WikiPage:
        """创建或更新 Wiki 页面。"""
        ...

    async def delete(self, workspace_id: UUID, wiki_id: UUID) -> bool:
        """删除某个 Wiki 页面。"""
        ...


class WikiQueryRepositoryPort(Protocol):
    """Wiki 读路径仓储接口（Query Port）。

    业务逻辑通过这个接口访问 Wiki 数据，而不关心具体实现（文件系统、数据库等）。
    """

    async def get_by_id(self, workspace_id: UUID, wiki_id: UUID) -> WikiPage | None:
        """按 ID 查询单个 Wiki 页面。"""
        ...

    async def get_by_title(self, workspace_id: UUID, title: str) -> WikiPage | None:
        """按标题查询单个 Wiki 页面。"""
        ...

    async def list_by_workspace(
        self, workspace_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[WikiPage]:
        """分页查询某个租户的全部 Wiki 页面。"""
        ...

    async def count_by_workspace(self, workspace_id: UUID) -> int:
        """统计某个租户的 Wiki 页面总数。"""
        ...


class WikiRepositoryPort(WikiCommandRepositoryPort, WikiQueryRepositoryPort, Protocol):
    """兼容旧代码的组合接口。"""
