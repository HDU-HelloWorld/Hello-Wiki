# -*- coding: utf-8 -*-
# 编码修复: database.py - 已替换Unicode符号避免Windows编码问题
"""
数据库初始化模块
提供创建数据库表的函数
"""

import logging
from typing import Optional

from sqlmodel import SQLModel, create_engine

from .config import settings

logger = logging.getLogger(__name__)


def create_db_and_tables() -> None:
    """
    创建所有已注册的SQLModel表

    注意：此函数需要在导入所有模型后调用，以便它们注册到SQLModel.metadata中。
    """
    import os

    # 优先使用环境变量 HELLO_WIKI_DATABASE_URL，如果未设置则使用 settings.DATABASE_URL
    database_url = os.environ.get("HELLO_WIKI_DATABASE_URL", settings.DATABASE_URL)

    # 如果使用asyncpg，转换为同步的psycopg2 URL
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        logger.info("已转换异步PostgreSQL URL为同步URL: %s", database_url)
    elif database_url.startswith("sqlite+aiosqlite://"):
        database_url = database_url.replace("sqlite+aiosqlite://", "sqlite://")
        logger.info("已转换异步SQLite URL为同步URL: %s", database_url)

    logger.info("正在创建数据库表，使用URL: %s", database_url)

    try:
        # 创建同步engine
        engine = create_engine(database_url, echo=settings.DEBUG)

        # 创建所有表
        SQLModel.metadata.create_all(engine)

        logger.info("数据库表创建成功")
        print("[OK] 数据库表创建成功！")

    except Exception as e:
        logger.exception("数据库表创建失败: %s", e)
        raise


def get_engine() -> Optional[object]:
    """
    获取同步engine（供测试使用）

    返回:
        sqlmodel.Engine实例或None（如果无法创建）
    """
    try:
        database_url = settings.DATABASE_URL

        # 如果使用asyncpg，转换为同步的psycopg2 URL
        if database_url.startswith("postgresql+asyncpg://"):
            database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        elif database_url.startswith("sqlite+aiosqlite://"):
            database_url = database_url.replace("sqlite+aiosqlite://", "sqlite://")

        return create_engine(database_url, echo=settings.DEBUG)
    except Exception as e:
        logger.error("创建engine失败: %s", e)
        return None


# 导出engine变量供测试使用
# 注意：这是一个同步engine，仅用于初始化脚本
engine = get_engine()