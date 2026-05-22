# -*- coding: utf-8 -*-
# 编码修复: models.py - 已替换Unicode符号避免Windows编码问题
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class WikiPageDB(SQLModel, table=True):
    """Wiki页面数据库模型"""
    __tablename__ = "wiki_pages"

    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: str = Field(index=True)
    title: str
    content: str = Field(default="")  # Wiki页面内容（Markdown格式）
    status: str = Field(default="draft")  # draft, published, archived
    created_by: str  # 创建用户ID
    updated_by: str  # 最后更新用户ID

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    published_at: Optional[datetime] = None  # 发布时间


class ParsingResultDB(SQLModel, table=True):
    """文档解析结果数据库模型"""
    __tablename__ = "parsing_results"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 原始文件信息
    original_filename: str
    document_type: str  # pdf, docx, txt, markdown, html
    file_size: int = Field(ge=0)  # 文件大小（字节）
    file_hash: str = Field(index=True)  # 文件哈希，用于去重

    # 解析结果
    extracted_text: str = Field(default="")  # 提取的文本内容（TEXT类型）
    title: Optional[str] = None  # 从文档中提取的标题
    author: Optional[str] = None  # 作者信息
    page_count: Optional[int] = Field(default=None, ge=0)  # 页数
    language: Optional[str] = None  # 检测到的语言

    # 元数据（JSON格式存储）
    metadata_json: str = Field(default="{}")  # JSON字符串格式的元数据

    # 状态信息
    status: str = Field(default="pending", index=True)  # pending, processing, completed, failed
    error_message: Optional[str] = None  # 错误信息

    # 关联信息
    workspace_id: str = Field(index=True)
    uploaded_by: str  # 上传用户ID
    wiki_page_id: Optional[int] = Field(default=None, foreign_key="wiki_pages.id")  # 关联的Wiki页面

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    updated_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None  # 处理完成时间