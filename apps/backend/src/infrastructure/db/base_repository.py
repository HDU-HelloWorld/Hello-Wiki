"""Base repository providing generic CRUD operations over SQLModel."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Generic, TypeVar, cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import Delete
from sqlmodel import SQLModel, select

# 泛型类型参数：任何继承自 SQLModel 的实体都可以作为 T
T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    """通用异步 Repository，提供基础 CRUD 操作与事务管理。

    使用示例（单条操作，自动 commit）:
        await wiki_repo.create(page)

    使用示例（多条操作，需要事务）:
        async with wiki_repo.transaction():
            page1 = await wiki_repo.create(page1)
            page2 = await wiki_repo.create(page2)
            # 异常时自动 rollback，成功时自动 commit
    """

    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        """初始化 Repository。

        参数:
            session: 异步数据库会话
            model: SQLModel 实体类
        """
        self._session = session
        self._model = model

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        """异步事务上下文管理器。

        用法:
            async with repo.transaction():
                await repo.create(obj1)
                await repo.create(obj2)
            # 异常则自动 rollback，成功则自动 commit

        Yields:
            None

        Raises:
            Exception: 如果事务中任何操作失败
        """
        try:
            async with self._session.begin():
                yield
        except Exception:
            await self._session.rollback()
            raise

    async def commit(self) -> None:
        """显式提交当前事务。

        通常不需要直接调用，除非在 transaction() 上下文之外需要手动管理。
        """
        await self._session.commit()

    async def rollback(self) -> None:
        """显式回滚当前事务。

        通常不需要直接调用，除非在 transaction() 上下文之外需要手动管理。
        """
        await self._session.rollback()

    async def create(self, obj: T) -> T:
        """创建并返回一条记录。

        参数:
            obj: 待创建的实体实例

        返回:
            刷新后的完整实体（包含 ID 等自动生成字段）

        说明:
            - 在 transaction() 上下文外：自动 commit
            - 在 transaction() 上下文内：由上下文管理 commit
        """
        self._session.add(obj)
        if not self._session.in_transaction():
            await self._session.commit()
        await self._session.refresh(obj)
        return obj

    async def get_by_id(self, obj_id: UUID | str | int) -> T | None:
        """按 ID 查询单条记录。

        参数:
            obj_id: 实体主键

        返回:
            实体实例或 None
        """
        return await self._session.get(self._model, obj_id)

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """分页查询全部记录。

        参数:
            skip: 跳过数量（分页偏移）
            limit: 单页数量

        返回:
            实体列表
        """
        statement = select(self._model).offset(skip).limit(limit)
        result = await self._session.execute(statement)
        return cast(list[T], list(result.scalars().all()))

    async def update(self, obj: T) -> T:
        """更新单条记录。

        参数:
            obj: 待更新的实体实例（需要包含 ID）

        返回:
            刷新后的完整实体

        说明:
            - 在 transaction() 上下文外：自动 commit
            - 在 transaction() 上下文内：由上下文管理 commit
        """
        self._session.add(obj)
        if not self._session.in_transaction():
            await self._session.commit()
        await self._session.refresh(obj)
        return obj

    async def delete(self, obj_id: UUID | str | int) -> bool:
        """按 ID 删除单条记录。

        参数:
            obj_id: 实体主键

        返回:
            是否删除成功（True 表示删除了至少一条记录）

        说明:
            - 在 transaction() 上下文外：自动 commit
            - 在 transaction() 上下文内：由上下文管理 commit
        """
        obj = await self._session.get(self._model, obj_id)
        if obj:
            await self._session.delete(obj)
            if not self._session.in_transaction():
                await self._session.commit()
            return True
        return False

    async def delete_many(self, statement: Delete) -> int:
        """按条件批量删除。

        参数:
            statement: SQLAlchemy delete 语句

        返回:
            删除的记录数

        说明:
            - 在 transaction() 上下文外：自动 commit
            - 在 transaction() 上下文内：由上下文管理 commit
        """
        result = await self._session.execute(statement)
        if not self._session.in_transaction():
            await self._session.commit()
        rowcount = cast(Any, result).rowcount
        return int(rowcount or 0)

    async def count(self) -> int:
        """统计全部记录数。

        返回:
            记录总数
        """
        statement = select(self._model)
        result = await self._session.execute(statement)
        return len(cast(list[Any], result.scalars().all()))

    async def exists(self, obj_id: UUID | str | int) -> bool:
        """检查记录是否存在。

        参数:
            obj_id: 实体主键

        返回:
            是否存在
        """
        obj = await self._session.get(self._model, obj_id)
        return obj is not None
