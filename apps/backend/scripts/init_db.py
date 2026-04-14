#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 编码修复: init_db.py - 已替换Unicode符号避免Windows编码问题
"""
数据库初始化脚本
用于创建数据库表结构
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 现在导入模型和数据库函数
# 注意：需要导入模型以便SQLModel.metadata注册它们
from infra.models.models import ParsingResultDB, WikiPageDB
from core.database import create_db_and_tables


def main() -> None:
    """创建数据库表"""
    print("正在创建数据库表...")
    try:
        create_db_and_tables()
        print("[OK] 数据库表创建成功！")
        print(f"   - {WikiPageDB.__tablename__}")
        print(f"   - {ParsingResultDB.__tablename__}")
    except Exception as e:
        print(f"[ERROR] 数据库表创建失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()