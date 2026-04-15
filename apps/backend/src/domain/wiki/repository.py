"""
Wiki 页面仓库接口
定义数据访问的抽象契约
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from src.domain.wiki.entity import WikiPage


class WikiPageRepository(ABC):
    """Wiki 页面仓库接口"""
    
    @abstractmethod
    def save(self, page: WikiPage) -> int:
        """保存页面（返回生成的 ID）"""
        pass
    
    @abstractmethod
    def get_by_id(self, page_id: int) -> Optional[WikiPage]:
        """根据 ID 获取页面"""
        pass
    
    @abstractmethod
    def get_all(self, limit: int = 100, offset: int = 0) -> List[WikiPage]:
        """获取所有页面（分页）"""
        pass
    
    @abstractmethod
    def get_count(self) -> int:
        """获取页面总数"""
        pass
    
    @abstractmethod
    def update(self, page: WikiPage) -> bool:
        """更新页面"""
        pass
    
    @abstractmethod
    def delete(self, page_id: int) -> bool:
        """删除页面"""
        pass
    
    @abstractmethod
    def get_children(self, parent_id: Optional[int] = None) -> List[WikiPage]:
        """获取子页面"""
        pass
    
    @abstractmethod
    def get_tree(self, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取目录树"""
        pass
    
    @abstractmethod
    def get_path(self, page_id: int) -> List[WikiPage]:
        """获取页面路径"""
        pass
    
    @abstractmethod
    def search_by_title(self, keyword: str, limit: int = 50) -> List[WikiPage]:
        """按标题搜索"""
        pass
    
    @abstractmethod
    def get_by_tags(self, tags: List[str], limit: int = 50) -> List[WikiPage]:
        """按标签筛选"""
        pass