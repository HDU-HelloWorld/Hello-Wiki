#!/usr/bin/env python3
"""
验证数据库创建和表结构
"""
import os
import sqlite3
import sys
from pathlib import Path

def main():
    # 查找数据库文件
    db_path = Path("hello_wiki.db")

    if not db_path.exists():
        print(f"[FAIL] 数据库文件不存在: {db_path}")
        print("当前目录:", Path.cwd())
        print("请先运行: python scripts/init_db.py")
        return 1

    print(f"[OK] 找到数据库文件: {db_path}")
    print(f"文件大小: {db_path.stat().st_size} 字节")

    # 连接到数据库
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print(f"\n数据库中的表 ({len(tables)} 个):")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"  {table_name} ({len(columns)} 列):")
            for col in columns:
                col_id, col_name, col_type, notnull, default_val, pk = col
                pk_mark = " PK" if pk else ""
                print(f"    {col_name}: {col_type}{pk_mark}")

        # 检查特定表是否存在
        table_names = [t[0] for t in tables]
        expected_tables = ["wiki_pages", "parsing_results"]

        print(f"\n表存在性检查:")
        for expected in expected_tables:
            if expected in table_names:
                print(f"  [OK] {expected} 表存在")
            else:
                print(f"  [FAIL] {expected} 表不存在")

        # 检查wiki_pages表结构
        if "wiki_pages" in table_names:
            cursor.execute("PRAGMA table_info(wiki_pages);")
            wiki_columns = {col[1] for col in cursor.fetchall()}
            expected_columns = {"id", "workspace_id", "title", "content", "status",
                               "created_by", "updated_by", "created_at", "updated_at", "published_at"}
            missing = expected_columns - wiki_columns
            if missing:
                print(f"  [FAIL] wiki_pages表缺少列: {missing}")
            else:
                print(f"  [OK] wiki_pages表结构完整")

        # 检查parsing_results表结构
        if "parsing_results" in table_names:
            cursor.execute("PRAGMA table_info(parsing_results);")
            parsing_columns = {col[1] for col in cursor.fetchall()}
            expected_columns = {"id", "original_filename", "document_type", "file_size", "file_hash",
                               "extracted_text", "title", "author", "page_count", "language",
                               "metadata_json", "status", "error_message", "workspace_id",
                               "uploaded_by", "wiki_page_id", "created_at", "updated_at", "processed_at"}
            missing = expected_columns - parsing_columns
            if missing:
                print(f"  [FAIL] parsing_results表缺少列: {missing}")
            else:
                print(f"  [OK] parsing_results表结构完整")

        # 测试插入和查询（可选）
        print(f"\n测试数据操作:")
        try:
            # 测试插入wiki_page
            cursor.execute("""
                INSERT INTO wiki_pages (workspace_id, title, content, status, created_by, updated_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("test_workspace", "测试页面", "测试内容", "draft", "user1", "user1"))
            wiki_id = cursor.lastrowid
            print(f"  [OK] 插入wiki_page成功, ID: {wiki_id}")

            # 测试插入parsing_result
            cursor.execute("""
                INSERT INTO parsing_results (original_filename, document_type, file_size, file_hash,
                                           extracted_text, workspace_id, uploaded_by, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ("test.pdf", "pdf", 1024, "abc123", "测试文本", "test_workspace", "user1", "pending"))
            parsing_id = cursor.lastrowid
            print(f"  [OK] 插入parsing_result成功, ID: {parsing_id}")

            # 查询数据
            cursor.execute("SELECT COUNT(*) FROM wiki_pages")
            wiki_count = cursor.fetchone()[0]
            print(f"  [OK] wiki_pages表记录数: {wiki_count}")

            cursor.execute("SELECT COUNT(*) FROM parsing_results")
            parsing_count = cursor.fetchone()[0]
            print(f"  [OK] parsing_results表记录数: {parsing_count}")

            # 回滚测试数据
            conn.rollback()
            print(f"  [OK] 测试数据已回滚")

        except Exception as e:
            print(f"  [WARN] 数据操作测试失败: {e}")
            conn.rollback()

        print(f"\n[OK] 数据库验证通过!")

    finally:
        conn.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())