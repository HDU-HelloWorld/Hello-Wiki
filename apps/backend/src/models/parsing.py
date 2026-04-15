"""
文档解析结果模型
存储导入文档（PDF/DOCX/MD）的解析结果
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum


class ParseStatus(str, Enum):
    """解析任务状态枚举"""
    PENDING = "pending"      # 等待处理
    PROCESSING = "processing" # 处理中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败


class ParsingResult(SQLModel, table=True):
    """
    文档解析结果表
    存储上传文档的解析状态和提取内容
    """
    __tablename__ = "parsing_results"
    
    # 主键
    id: Optional[int] = Field(default=None, primary_key=True, description="解析结果唯一ID")
    
    # 文档信息
    source_type: str = Field(max_length=20, description="源文档类型: pdf, docx, md")
    source_path: str = Field(max_length=1000, description="原始文件存储路径")
    source_filename: Optional[str] = Field(default=None, max_length=255, description="原始文件名")
    
    # 解析内容
    extracted_text: str = Field(default="", description="提取的纯文本内容")
    content_blocks: Optional[str] = Field(default=None, description="结构化内容块，JSON格式")
    
    # 解析状态
    status: str = Field(default=ParseStatus.PENDING, description="解析状态")
    error_message: Optional[str] = Field(default=None, description="错误信息（如果失败）")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    
    # 关联
    created_page_id: Optional[int] = Field(default=None, description="导入后生成的Wiki页面ID")
    
    def __repr__(self) -> str:
        return f"<ParsingResult(id={self.id}, type='{self.source_type}', status='{self.status}')>"