"""
Wiki 页面数据访问层
封装所有数据库操作，提供 CRUD 接口
"""

from sqlmodel import Session, select, func
from src.models.wiki import WikiPage
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import or_


class WikiRepository:
    """
    Wiki 页面数据仓库
    负责所有页面相关的数据库操作
    """
    
    def __init__(self, session: Session) -> None:
        """初始化仓库"""
        self.session = session
    
    # ========== 基础 CRUD ==========
    
    def create(self, title: str, content: str = "", tags: str = "[]", 
               parent_id: Optional[int] = None, created_by: Optional[str] = None) -> int:
        """创建新页面"""
        page = WikiPage(
            title=title,
            content=content,
            tags=tags,
            parent_id=parent_id,
            version=1,
            created_by=created_by
        )
        self.session.add(page)
        self.session.commit()
        self.session.refresh(page)
        return page.id if page.id is not None else 0
    
    def get_by_id(self, page_id: int) -> Optional[WikiPage]:
        """根据 ID 获取页面"""
        return self.session.get(WikiPage, page_id)
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[WikiPage]:
        """获取所有页面（分页）"""
        statement = select(WikiPage).offset(offset).limit(limit).order_by(WikiPage.title)
        return list(self.session.exec(statement).all())
    
    def get_count(self) -> int:
        """获取页面总数"""
        statement = select(func.count()).select_from(WikiPage)
        return self.session.exec(statement).one()
    
    def update_content(self, page_id: int, content: str) -> bool:
        """更新页面内容"""
        page = self.get_by_id(page_id)
        if not page:
            return False
        page.content = content
        page.version += 1
        page.updated_at = datetime.now()
        self.session.commit()
        return True
    
    def update_title(self, page_id: int, title: str) -> bool:
        """更新页面标题"""
        page = self.get_by_id(page_id)
        if not page:
            return False
        page.title = title
        page.updated_at = datetime.now()
        self.session.commit()
        return True
    
    def update_tags(self, page_id: int, tags: str) -> bool:
        """更新页面标签"""
        page = self.get_by_id(page_id)
        if not page:
            return False
        page.tags = tags
        page.updated_at = datetime.now()
        self.session.commit()
        return True
    
    def delete(self, page_id: int) -> bool:
        """删除页面"""
        page = self.get_by_id(page_id)
        if not page:
            return False
        self.session.delete(page)
        self.session.commit()
        return True
    
    # ========== 目录树相关 ==========
    
    def get_children(self, parent_id: Optional[int] = None) -> List[WikiPage]:
        """获取子页面"""
        statement = select(WikiPage).where(WikiPage.parent_id == parent_id).order_by(WikiPage.title)
        return list(self.session.exec(statement).all())
    
    def get_tree(self, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取目录树"""
        children = self.get_children(parent_id)
        result = []
        for child in children:
            node = {
                "id": child.id,
                "title": child.title,
                "children": self.get_tree(child.id)
            }
            result.append(node)
        return result
    
    def get_path(self, page_id: int) -> List[WikiPage]:
        """获取页面路径"""
        path: List[WikiPage] = []
        current = self.get_by_id(page_id)
        while current:
            path.insert(0, current)
            if current.parent_id:
                current = self.get_by_id(current.parent_id)
            else:
                break
        return path
    
    def move_page(self, page_id: int, new_parent_id: Optional[int]) -> bool:
        """移动页面"""
        page = self.get_by_id(page_id)
        if not page:
            return False
        if new_parent_id is not None:
            if page_id == new_parent_id:
                return False
            ancestor = self.get_by_id(new_parent_id)
            while ancestor:
                if ancestor.parent_id == page_id:
                    return False
                if ancestor.parent_id:
                    ancestor = self.get_by_id(ancestor.parent_id)
                else:
                    break
        page.parent_id = new_parent_id
        page.updated_at = datetime.now()
        self.session.commit()
        return True
    
    # ========== 搜索相关 ==========
    
    def search_by_title(self, keyword: str, limit: int = 50) -> List[WikiPage]:
        """按标题模糊搜索"""
        # 使用 SQL 的 LIKE 进行模糊匹配
        statement = select(WikiPage).where(
            WikiPage.title.contains(keyword)
        ).limit(limit)
        return list(self.session.exec(statement).all())
    
    def get_by_tags(self, tags: List[str], limit: int = 50) -> List[WikiPage]:
        """按标签筛选页面"""
        if not tags:
            return []
        conditions = []
        for tag in tags:
            # 使用 JSON 查询或 LIKE 匹配
            conditions.append(WikiPage.tags.contains(f'"{tag}"'))
        if not conditions:
            return []
        statement = select(WikiPage).where(or_(*conditions)).limit(limit)
        return list(self.session.exec(statement).all())