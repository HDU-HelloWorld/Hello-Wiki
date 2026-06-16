import asyncpg

from src.application.init.commands import InitTagsCommand
from src.application.init.init_tags import InitTagsUseCase, TagTreeSchema
from src.core.config import settings
from src.core.logging import get_logger
from src.infrastructure.db.repositories.knowledge_catalog_repo import (
    mark_knowledge_domain_initialized,
    upsert_knowledge_domain_on_connection,
)

logger = get_logger(__name__)


class InitTagsHandler:
    """Application service for tag initialization.

    Generates the domain tag hierarchy via LLM, then persists knowledge_domains + tags.
    """

    def __init__(self, use_case: InitTagsUseCase) -> None:
        self._use_case = use_case

    async def handle(self, command: InitTagsCommand) -> TagTreeSchema:
        tree = await self._use_case.execute(command)
        await self._persist(command, tree)
        logger.info(
            "init_tags persisted workspace=%s domain=%s categories=%s",
            command.workspace_id,
            command.domain,
            len(tree.categories),
        )
        return tree

    async def _persist(self, command: InitTagsCommand, tree: TagTreeSchema) -> None:
        dsn = settings.DATABASE_URL.replace("+asyncpg", "")
        conn = await asyncpg.connect(dsn)
        ws = command.workspace_id
        domain = command.domain
        label = tree.domain or command.domain
        try:
            async with conn.transaction():
                await upsert_knowledge_domain_on_connection(
                    conn,
                    ws,
                    domain,
                    label=label,
                    description=command.description,
                )
                for category in tree.categories:
                    await conn.execute(
                        "INSERT INTO tags (workspace_id, domain_id, name, label, description, "
                        "parent_id, level, path, is_leaf) "
                        "VALUES ($1, $2, $3, $4, $5, NULL, 0, $6::ltree, false) "
                        "ON CONFLICT (workspace_id, domain_id, path) DO NOTHING",
                        ws,
                        domain,
                        category.name,
                        category.label,
                        category.description,
                        category.name,
                    )
                    parent_id = await conn.fetchval(
                        """
                        SELECT id FROM tags
                        WHERE workspace_id = $1 AND domain_id = $2 AND path = $3::ltree
                        """,
                        ws,
                        domain,
                        category.name,
                    )
                    if parent_id is None:
                        continue
                    for leaf in category.leaves:
                        leaf_path = f"{category.name}.{leaf.name}"
                        await conn.execute(
                            "INSERT INTO tags (workspace_id, domain_id, name, label, description, "
                            "parent_id, level, path, is_leaf) "
                            "VALUES ($1, $2, $3, $4, $5, $6, 1, $7::ltree, true) "
                            "ON CONFLICT (workspace_id, domain_id, path) DO NOTHING",
                            ws,
                            domain,
                            leaf.name,
                            leaf.label,
                            leaf.description,
                            parent_id,
                            leaf_path,
                        )
                await mark_knowledge_domain_initialized(conn, ws, domain)
        finally:
            await conn.close()
