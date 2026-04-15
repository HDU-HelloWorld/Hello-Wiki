from dataclasses import dataclass
from uuid import UUID

from src.api.deps import get_container
from src.application.wiki.wiki_commands import WikiCommandService
from src.application.wiki.wiki_queries import WikiQueryService


@dataclass
class WikiApplicationService:
    """
    Wiki应用服务，聚合Wiki命令和查询服务，并添加版本管理功能
    """
    wiki_commands: WikiCommandService
    wiki_queries: WikiQueryService

    def get_page_versions(self, page_id: UUID, workspace_id: UUID, limit: int = 10, offset: int = 0) -> list:
        """
        获取Wiki页面的版本列表
        TODO: 需要实现版本存储和查询逻辑
        """
        raise NotImplementedError("get_page_versions not implemented yet")

    def get_version_by_id(self, version_id: UUID, workspace_id: UUID) -> dict:
        """
        根据ID获取特定版本
        TODO: 需要实现版本详情查询逻辑
        """
        raise NotImplementedError("get_version_by_id not implemented yet")

    def compare_versions(self, version_a_id: UUID, version_b_id: UUID, workspace_id: UUID) -> dict:
        """
        比较两个版本之间的差异
        TODO: 需要实现版本比较逻辑
        """
        raise NotImplementedError("compare_versions not implemented yet")

    def rollback_to_version(self, version_id: UUID, workspace_id: UUID) -> dict:
        """
        将Wiki页面回滚到指定版本
        TODO: 需要实现回滚逻辑
        """
        raise NotImplementedError("rollback_to_version not implemented yet")


def get_wiki_application_service() -> WikiApplicationService:
    """
    获取Wiki应用服务实例
    """
    container = get_container()
    return WikiApplicationService(
        wiki_commands=container.wiki_commands,
        wiki_queries=container.wiki_queries,
    )