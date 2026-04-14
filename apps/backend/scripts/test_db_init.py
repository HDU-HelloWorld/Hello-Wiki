#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 编码修复: test_db_init.py - 已替换Unicode符号避免Windows编码问题
"""
数据库初始化脚本测试
"""
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_database_creation() -> None:
    """测试数据库创建和表结构"""
    # 使用临时数据库文件
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        # 设置环境变量使用临时数据库
        os.environ["HELLO_WIKI_DATABASE_URL"] = f"sqlite:///{db_path}"

        # 动态导入，以便环境变量生效
        import importlib
        import core.database as db_module
        from core.database import engine

        # 重新加载模块以使环境变量生效
        importlib.reload(db_module)

        # 导入模型（需要在create_db_and_tables之前）
        from infra.models.models import ParsingResultDB, WikiPageDB

        # 创建表
        db_module.create_db_and_tables()

        # 验证数据库文件已创建
        assert os.path.exists(db_path), "数据库文件未创建"

        # 使用sqlite3直接检查表是否存在
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查wiki_pages表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wiki_pages';")
        wiki_table = cursor.fetchone()
        assert wiki_table is not None, "wiki_pages表未创建"

        # 检查parsing_results表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parsing_results';")
        parsing_table = cursor.fetchone()
        assert parsing_table is not None, "parsing_results表未创建"

        # 检查表结构（列）
        cursor.execute("PRAGMA table_info(wiki_pages);")
        wiki_columns = {row[1] for row in cursor.fetchall()}
        expected_wiki_columns = {"id", "workspace_id", "title", "content", "status",
                                 "created_by", "updated_by", "created_at", "updated_at", "published_at"}
        assert expected_wiki_columns.issubset(wiki_columns), f"wiki_pages表缺少列: {expected_wiki_columns - wiki_columns}"

        cursor.execute("PRAGMA table_info(parsing_results);")
        parsing_columns = {row[1] for row in cursor.fetchall()}
        expected_parsing_columns = {"id", "original_filename", "document_type", "file_size", "file_hash",
                                   "extracted_text", "title", "author", "page_count", "language",
                                   "metadata_json", "status", "error_message", "workspace_id",
                                   "uploaded_by", "wiki_page_id", "created_at", "updated_at", "processed_at"}
        assert expected_parsing_columns.issubset(parsing_columns), f"parsing_results表缺少列: {expected_parsing_columns - parsing_columns}"
        conn.close()
        print("[OK] 数据库初始化测试通过！")
        print(f"   数据库文件: {db_path}")
        print(f"   表创建成功: wiki_pages, parsing_results")

    except ImportError as e:
        print(f"[WARN] 导入错误（可能缺少依赖）: {e}")
        print("   请运行: pip install -e .")
        sys.exit(77)  # 跳过测试的退出码
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 清理临时文件
        try:
            if 'conn' in locals():
                conn.close()
        except:
            pass

        if os.path.exists(db_path):
            try:
                os.unlink(db_path)
            except PermissionError:
                print(f"[WARN] 无法删除临时文件 {db_path}，可能仍有连接未关闭")
        # 恢复环境变量
        if "HELLO_WIKI_DATABASE_URL" in os.environ:
            del os.environ["HELLO_WIKI_DATABASE_URL"]


if __name__ == "__main__":
    print("运行数据库初始化测试...")
    test_database_creation()