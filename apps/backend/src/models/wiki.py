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
    
    id: Optional[int] = Field(default=None, primary_key=True, description="页面唯一ID")
    title: str = Field(max_length=500, nullable=False, index=True, description="页面标题")
    content: str = Field(default="", description="Markdown格式内容")
    tags: str = Field(default="[]", description="标签列表，JSON字符串格式")
    parent_id: Optional[int] = Field(default=None, foreign_key="pages.id", index=True, description="父页面ID")
    version: int = Field(default=1, description="当前版本号")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    created_by: Optional[str] = Field(default=None, max_length=100, description="创建者")
    
    def get_tags_list(self) -> List[str]:
        """获取标签列表"""
        if not self.tags:
            return []
        try:
            result = json.loads(self.tags)
            if isinstance(result, list):
                return [str(tag) for tag in result]
            return []
        except json.JSONDecodeError:
            return []
    
    def set_tags_list(self, tags_list: List[str]) -> None:
        """设置标签列表"""
        self.tags = json.dumps(tags_list, ensure_ascii=False)
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<WikiPage(id={self.id}, title='{self.title}', version={self.version})>"