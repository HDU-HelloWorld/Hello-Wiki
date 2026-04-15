"""
Wiki 页面数据访问层
封装所有数据库操作，提供 CRUD 接口
"""

from sqlmodel import Session, select, func
from src.models.wiki import WikiPage
from typing import Optional, List, Dict, Any
from datetime import datetime


class WikiRepository:
    """
    Wiki 页面数据仓库
    负责所有页面相关的数据库操作
    """
    
    def __init__(self, session: Session):
        """
        初始化仓库
        
        Args:
            session: 数据库会话
        """
        self.session = session
    
    # ========== 基础 CRUD ==========
    
    def create(self, title: str, content: str = "", tags: str = "[]", 
            parent_id: Optional[int] = None, created_by: Optional[str] = None) -> int:
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
        # 确保返回 int 类型
        return page.id if page.id is not None else 0
    
    def get_by_id(self, page_id: int) -> Optional[WikiPage]:
        """
        根据 ID 获取页面
        
        Args:
            page_id: 页面 ID
            
        Returns:
            WikiPage 对象，不存在则返回 None
        """
        return self.session.get(WikiPage, page_id)
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[WikiPage]:
        statement = select(WikiPage).offset(offset).limit(limit).order_by(WikiPage.title)
        return list(self.session.exec(statement).all())  # 添加 list()
    
    def get_count(self) -> int:
        """
        获取页面总数
        
        Returns:
            页面数量
        """
        statement = select(func.count()).select_from(WikiPage)
        return self.session.exec(statement).one()
    
    def update_content(self, page_id: int, content: str) -> bool:
        """
        更新页面内容（自动增加版本号）
        
        Args:
            page_id: 页面 ID
            content: 新内容
            
        Returns:
            是否更新成功
        """
        page = self.get_by_id(page_id)
        if not page:
            return False
        
        page.content = content
        page.version += 1
        page.updated_at = datetime.now()
        self.session.commit()
        return True
    
    def update_title(self, page_id: int, title: str) -> bool:
        """
        更新页面标题
        
        Args:
            page_id: 页面 ID
            title: 新标题
            
        Returns:
            是否更新成功
        """
        page = self.get_by_id(page_id)
        if not page:
            return False
        
        page.title = title
        page.updated_at = datetime.now()
        self.session.commit()
        return True
    
    def update_tags(self, page_id: int, tags: str) -> bool:
        """
        更新页面标签
        
        Args:
            page_id: 页面 ID
            tags: 标签 JSON 字符串
            
        Returns:
            是否更新成功
        """
        page = self.get_by_id(page_id)
        if not page:
            return False
        
        page.tags = tags
        page.updated_at = datetime.now()
        self.session.commit()
        return True
    
    def delete(self, page_id: int) -> bool:
        """
        删除页面（级联删除子页面和版本记录）
        
        Args:
            page_id: 页面 ID
            
        Returns:
            是否删除成功
        """
        page = self.get_by_id(page_id)
        if not page:
            return False
        
        self.session.delete(page)
        self.session.commit()
        return True
    
    # ========== 目录树相关 ==========
    
    def get_children(self, parent_id: Optional[int] = None) -> List[WikiPage]:
        statement = select(WikiPage).where(WikiPage.parent_id == parent_id).order_by(WikiPage.title)
        return list(self.session.exec(statement).all())  # 添加 list()
    
    def get_tree(self, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取目录树（递归结构）
        
        Args:
            parent_id: 父页面 ID，None 表示从根开始
            
        Returns:
            树形结构列表，每个节点包含 id, title, children
        """
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
        """
        获取页面从根到自身的路径
        
        Args:
            page_id: 页面 ID
            
        Returns:
            路径上的页面列表（从根到当前页）
        """
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
        """
        移动页面到新的父节点
        
        Args:
            page_id: 页面 ID
            new_parent_id: 新父页面 ID，None 表示移到根级
            
        Returns:
            是否移动成功
        """
        page = self.get_by_id(page_id)
        if not page:
            return False
        
        # 防止循环引用：不能移动到自己或自己的子节点下
        if new_parent_id is not None:
            if page_id == new_parent_id:
                return False
            
            # 检查 new_parent 是否是 page 的后代
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
        statement = select(WikiPage).where(
            WikiPage.title.like(f'%{keyword}%')
        ).limit(limit)
        return list(self.session.exec(statement).all())
    
    def get_by_tags(self, tags: List[str], limit: int = 50) -> List[WikiPage]:
        """
        按标签筛选页面
        
        Args:
            tags: 标签列表
            limit: 最大返回数量
            
        Returns:
            包含任意指定标签的页面列表
        """
        # SQLite 的 JSON 查询语法
        conditions = []
        for tag in tags:
            conditions.append(WikiPage.tags.like(f'%"{tag}"%'))
        
        if not conditions:
            return []
        
        from sqlalchemy import or_
        statement = select(WikiPage).where(or_(*conditions)).limit(limit)
        return list(self.session.exec(statement).all())
    
    def __repr__(self) -> str:
        return f"<WikiRepository(session={self.session})>"