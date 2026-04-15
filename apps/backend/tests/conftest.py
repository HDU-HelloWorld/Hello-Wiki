"""
pytest 配置文件
添加项目根目录到 Python 路径
"""

import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# 也可以在这里添加 fixtures
import pytest
from sqlmodel import Session, SQLModel, create_engine
from src.repositories.wiki import WikiRepository


@pytest.fixture
def session():
    """创建测试数据库会话（内存数据库）"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
    
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def repo(session):
    """创建 WikiRepository 实例"""
    return WikiRepository(session)