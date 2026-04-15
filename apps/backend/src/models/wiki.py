"""
Wiki 页面模型
定义知识库页面的核心数据结构
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field
import json


class WikiPage(SQLModel, table=True):
    """
    Wiki 页面表
    存储知识库的所有页面内容
    """
    __tablename__ = "pages"
    
    # 主键
    id: Optional[int] = Field(default=None, primary_key=True, description="页面唯一ID")
    
    # 基本信息
    title: str = Field(max_length=500, nullable=False, index=True, description="页面标题")
    content: str = Field(default="", description="Markdown格式内容")
    tags: str = Field(default="[]", description="标签列表，JSON字符串格式")
    
    # 层级关系
    parent_id: Optional[int] = Field(
        default=None, 
        foreign_key="pages.id", 
        index=True,
        description="父页面ID，用于构建目录树"
    )
    
    # 版本控制
    version: int = Field(default=1, description="当前版本号")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    # 元数据
    created_by: Optional[str] = Field(default=None, max_length=100, description="创建者")
    
    def get_tags_list(self) -> List[str]:
        """
        将 JSON 字符串解析为标签列表
        
        Returns:
            标签列表，如 ['python', 'fastapi']
        """
        if not self.tags:
            return []
        try:
            return json.loads(self.tags)
        except json.JSONDecodeError:
            return []
    
    def set_tags_list(self, tags_list: List[str]) -> None:
        """
        将标签列表转为 JSON 字符串存储
        
        Args:
            tags_list: 标签列表
        """
        self.tags = json.dumps(tags_list, ensure_ascii=False)
    
    def __repr__(self) -> str:
        return f"<WikiPage(id={self.id}, title='{self.title}', version={self.version})>"