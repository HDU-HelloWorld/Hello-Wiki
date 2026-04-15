"""
数据库核心配置
负责数据库连接、初始化、FTS5全文搜索配置
"""

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
import os

# 数据库路径配置
DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./wiki.db")

# 创建数据库引擎
engine = create_engine(
    DB_PATH,
    connect_args={"check_same_thread": False} if "sqlite:///" in DB_PATH else {},
    echo=False
)


def init_db() -> None:
    """
    初始化数据库
    1. 创建所有表
    2. 创建 FTS5 虚拟表（全文搜索）
    3. 创建触发器（自动同步 FTS 索引）
    """
    
    # 导入模型，确保 SQLModel 能发现它们
    from src.models import WikiPage, PageVersion, ParsingResult  # noqa: F401
    
    # 1. 创建普通表
    SQLModel.metadata.create_all(engine)
    print("✅ 普通表创建完成")
    
    # 2. 创建 FTS5 虚拟表和触发器
    with engine.connect() as conn:
        # 启用外键约束 - 使用 text() 包装
        conn.execute(text("PRAGMA foreign_keys = ON;"))
        
        # 创建 FTS5 虚拟表
        conn.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts 
            USING fts5(title, content, content=pages);
        """))
        print("✅ FTS5 虚拟表创建完成")
        
        # 创建触发器：插入时同步到 FTS
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS pages_ai AFTER INSERT ON pages
            BEGIN
                INSERT INTO pages_fts(rowid, title, content) 
                VALUES (new.id, new.title, new.content);
            END;
        """))
        
        # 创建触发器：删除时从 FTS 移除
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS pages_ad AFTER DELETE ON pages
            BEGIN
                INSERT INTO pages_fts(pages_fts, rowid, title, content) 
                VALUES('delete', old.id, old.title, old.content);
            END;
        """))
        
        # 创建触发器：更新时同步到 FTS
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS pages_au AFTER UPDATE ON pages
            BEGIN
                INSERT INTO pages_fts(pages_fts, rowid, title, content) 
                VALUES('delete', old.id, old.title, old.content);
                INSERT INTO pages_fts(rowid, title, content) 
                VALUES (new.id, new.title, new.content);
            END;
        """))
        
        conn.commit()
        print("✅ FTS5 同步触发器创建完成")
    
    print("🎉 数据库初始化完成！")


def get_session() -> Session:
    """获取数据库会话（用于依赖注入）"""
    with Session(engine) as session:
        yield session


def get_engine():
    """获取数据库引擎"""
    return engine