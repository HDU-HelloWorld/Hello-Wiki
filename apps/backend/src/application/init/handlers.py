import asyncpg

from src.application.init.commands import InitTagsCommand
from src.application.init.init_tags import InitTagsUseCase, TagTreeSchema
from src.core.config import settings


class InitTagsHandler:
    """Application service for tag initialization.

    Generates the domain tag hierarchy via LLM, then persists it to the tags table.
    """

    def __init__(self, use_case: InitTagsUseCase) -> None:
        self._use_case = use_case

    async def handle(self, command: InitTagsCommand) -> TagTreeSchema:
        tree = await self._use_case.execute(command)
        await self._persist(tree)
        return tree

    async def _persist(self, tree: TagTreeSchema) -> None:
        dsn = settings.DATABASE_URL.replace("+asyncpg", "")
        conn = await asyncpg.connect(dsn)
        try:
            for category in tree.categories:
                await conn.execute(
                    "INSERT INTO tags (name, label, description, parent_id, level, path, is_leaf) "
                    "VALUES ($1, $2, $3, NULL, 0, $4::ltree, false) "
                    "ON CONFLICT (path) DO NOTHING",
                    category.name,
                    category.label,
                    category.description,
                    category.name,
                )
                parent_id = await conn.fetchval(
                    "SELECT id FROM tags WHERE path = $1::ltree", category.name
                )
                if parent_id is None:
                    continue
                for leaf in category.leaves:
                    leaf_path = f"{category.name}.{leaf.name}"
                    await conn.execute(
                        "INSERT INTO tags (name, label, description, "
                        "parent_id, level, path, is_leaf) "
                        "VALUES ($1, $2, $3, $4, 1, $5::ltree, true) "
                        "ON CONFLICT (path) DO NOTHING",
                        leaf.name,
                        leaf.label,
                        leaf.description,
                        parent_id,
                        leaf_path,
                    )
        finally:
            await conn.close()
