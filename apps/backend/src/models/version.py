"""
页面版本模型
实现 Wiki 页面的版本管理功能
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class PageVersion(SQLModel, table=True):
    """
    页面版本表
    存储页面的历史版本，支持版本回溯
    """
    __tablename__ = "page_versions"
    
    # 主键
    id: Optional[int] = Field(default=None, primary_key=True, description="版本记录唯一ID")
    
    # 关联关系
    page_id: int = Field(
        foreign_key="pages.id", 
        nullable=False, 
        index=True,
        description="关联的页面ID"
    )
    
    # 版本内容
    content: str = Field(default="", description="该版本的Markdown内容")
    version_number: int = Field(nullable=False, description="版本号，从1开始递增")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="版本创建时间")
    
    # 元数据
    created_by: Optional[str] = Field(default=None, max_length=100, description="创建者")
    
    def __repr__(self) -> str:
        return f"<PageVersion(id={self.id}, page_id={self.page_id}, version={self.version_number})>"