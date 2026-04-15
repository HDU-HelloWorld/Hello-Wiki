#!/usr/bin/env python
"""
数据库初始化脚本
独立运行，创建所有表和 FTS5 虚拟表
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
# 注意：backend 目录的父目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 使用绝对导入
from src.core.database import init_db, engine
from sqlalchemy import text


def verify_tables():
    """验证表是否创建成功"""
    print("\n📋 验证数据库表...")
    
    with engine.connect() as conn:
        # 查询所有表
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name;
        """))
        tables = [row[0] for row in result]
        
        expected_tables = ['pages', 'page_versions', 'parsing_results', 'pages_fts']
        
        print(f"   现有表: {', '.join(tables)}")
        
        for table in expected_tables:
            if table in tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} 缺失")
        
        # 验证触发器
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='trigger';
        """))
        triggers = [row[0] for row in result]
        print(f"\n📋 触发器: {', '.join(triggers) if triggers else '无'}")


if __name__ == "__main__":
    print("🚀 开始初始化数据库...")
    print("=" * 40)
    
    try:
        init_db()
        print("\n" + "=" * 40)
        verify_tables()
        print("\n✅ 数据库初始化完成！")
        print("📁 数据库文件位置: wiki.db")
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)