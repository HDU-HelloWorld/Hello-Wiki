# -*- coding: utf-8 -*-
# 编码修复: database.py - 已替换Unicode符号避免Windows编码问题
import os
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from core.config import settings

# 数据库URL，默认为SQLite
DATABASE_URL = os.getenv(
    "HELLO_WIKI_DATABASE_URL",
    f"sqlite:///{os.path.join(os.path.dirname(__file__), '../../hello_wiki.db')}"
)

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    """创建数据库和所有表（仅用于开发/测试）"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """获取数据库会话依赖项"""
    with Session(engine) as session:
        yield session


# FastAPI依赖类型别名
DBSession = Annotated[Session, Depends(get_session)]
