# -*- coding: utf-8 -*-
# 编码修复: parsing_result.py - 已替换Unicode符号避免Windows编码问题
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ParsingStatus(str, Enum):
    """文档解析状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(str, Enum):
    """支持的文档类型枚举"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MARKDOWN = "markdown"
    HTML = "html"


@dataclass(frozen=True)
class ParsingResultEntity:
    """
    文档解析结果领域实体
    用于表示从PDF、DOCX等文档中解析出的内容
    """
    id: Optional[int]
    # 原始文件信息
    original_filename: str
    document_type: DocumentType
    file_size: int  # 文件大小，单位：字节
    file_hash: str  # 文件内容哈希，用于去重

    # 解析结果
    extracted_text: str  # 提取的文本内容
    title: Optional[str]  # 从文档中提取的标题
    author: Optional[str]  # 作者信息
    page_count: Optional[int]  # 页数（针对PDF等分页文档）
    language: Optional[str]  # 检测到的语言

    # 元数据
    metadata: dict[str, str]  # 其他元数据键值对

    # 状态信息
    status: ParsingStatus
    error_message: Optional[str]  # 如果解析失败，错误信息

    # 关联信息
    workspace_id: str  # 所属工作空间
    uploaded_by: str  # 上传用户ID
    wiki_page_id: Optional[int]  # 关联的Wiki页面ID（如果已创建为Wiki页面）

    # 时间戳
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create_new(
        cls,
        original_filename: str,
        document_type: DocumentType,
        file_size: int,
        file_hash: str,
        workspace_id: str,
        uploaded_by: str,
    ) -> "ParsingResultEntity":
        """
        创建新的解析任务实体

        Args:
            original_filename: 原始文件名
            document_type: 文档类型
            file_size: 文件大小（字节）
            file_hash: 文件哈希
            workspace_id: 工作空间ID
            uploaded_by: 上传用户ID

        Returns:
            初始状态的ParsingResultEntity
        """
        now = datetime.now()
        return cls(
            id=None,
            original_filename=original_filename,
            document_type=document_type,
            file_size=file_size,
            file_hash=file_hash,
            extracted_text="",  # 初始为空文本
            title=None,
            author=None,
            page_count=None,
            language=None,
            metadata={},
            status=ParsingStatus.PENDING,
            error_message=None,
            workspace_id=workspace_id,
            uploaded_by=uploaded_by,
            wiki_page_id=None,
            created_at=now,
            updated_at=now,
        )

    def mark_processing(self) -> "ParsingResultEntity":
        """标记为处理中状态（返回新实例）"""
        return ParsingResultEntity(
            id=self.id,
            original_filename=self.original_filename,
            document_type=self.document_type,
            file_size=self.file_size,
            file_hash=self.file_hash,
            extracted_text=self.extracted_text,
            title=self.title,
            author=self.author,
            page_count=self.page_count,
            language=self.language,
            metadata=self.metadata,
            status=ParsingStatus.PROCESSING,
            error_message=self.error_message,
            workspace_id=self.workspace_id,
            uploaded_by=self.uploaded_by,
            wiki_page_id=self.wiki_page_id,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def mark_completed(
        self,
        extracted_text: str,
        title: Optional[str] = None,
        author: Optional[str] = None,
        page_count: Optional[int] = None,
        language: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> "ParsingResultEntity":
        """标记为已完成状态（返回新实例）"""
        return ParsingResultEntity(
            id=self.id,
            original_filename=self.original_filename,
            document_type=self.document_type,
            file_size=self.file_size,
            file_hash=self.file_hash,
            extracted_text=extracted_text,
            title=title,
            author=author,
            page_count=page_count,
            language=language,
            metadata=metadata or self.metadata,
            status=ParsingStatus.COMPLETED,
            error_message=None,
            workspace_id=self.workspace_id,
            uploaded_by=self.uploaded_by,
            wiki_page_id=self.wiki_page_id,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def mark_failed(self, error_message: str) -> "ParsingResultEntity":
        """标记为失败状态（返回新实例）"""
        return ParsingResultEntity(
            id=self.id,
            original_filename=self.original_filename,
            document_type=self.document_type,
            file_size=self.file_size,
            file_hash=self.file_hash,
            extracted_text=self.extracted_text,
            title=self.title,
            author=self.author,
            page_count=self.page_count,
            language=self.language,
            metadata=self.metadata,
            status=ParsingStatus.FAILED,
            error_message=error_message,
            workspace_id=self.workspace_id,
            uploaded_by=self.uploaded_by,
            wiki_page_id=self.wiki_page_id,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def link_to_wiki_page(self, wiki_page_id: int) -> "ParsingResultEntity":
        """关联到Wiki页面（返回新实例）"""
        return ParsingResultEntity(
            id=self.id,
            original_filename=self.original_filename,
            document_type=self.document_type,
            file_size=self.file_size,
            file_hash=self.file_hash,
            extracted_text=self.extracted_text,
            title=self.title,
            author=self.author,
            page_count=self.page_count,
            language=self.language,
            metadata=self.metadata,
            status=self.status,
            error_message=self.error_message,
            workspace_id=self.workspace_id,
            uploaded_by=self.uploaded_by,
            wiki_page_id=wiki_page_id,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )