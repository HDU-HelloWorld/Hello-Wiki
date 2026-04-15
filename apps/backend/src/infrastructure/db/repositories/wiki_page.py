"""
Wiki 页面仓库具体实现
使用 SQLModel + SQLite
"""

from sqlmodel import Session, select, func
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import or_

from src.domain.wiki.entity import WikiPage
from src.domain.wiki.repository import WikiPageRepository
from src.infrastructure.db.models.wiki import WikiPageModel  # 需要创建 ORM 模型


class WikiPageRepositoryImpl(WikiPageRepository):
    """Wiki 页面仓库实现"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def _to_domain(self, model: WikiPageModel) -> WikiPage:
        """ORM 模型 → 领域实体"""
        import json
        tags = json.loads(model.tags) if model.tags else []
        return WikiPage(
            id=model.id,
            title=model.title,
            content=model.content,
            tags=tags,
            parent_id=model.parent_id,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by
        )
    
    def _to_model(self, domain: WikiPage) -> WikiPageModel:
        """领域实体 → ORM 模型"""
        return WikiPageModel(
            id=domain.id if domain.id != 0 else None,
            title=domain.title,
            content=domain.content,
            tags=domain.tags_json,
            parent_id=domain.parent_id,
            version=domain.version,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            created_by=domain.created_by
        )
    
    def save(self, page: WikiPage) -> int:
        """保存页面"""
        model = self._to_model(page)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model.id if model.id is not None else 0
    
    def get_by_id(self, page_id: int) -> Optional[WikiPage]:
        """根据 ID 获取页面"""
        model = self.session.get(WikiPageModel, page_id)
        if not model:
            return None
        return self._to_domain(model)
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[WikiPage]:
        """获取所有页面"""
        statement = select(WikiPageModel).offset(offset).limit(limit).order_by(WikiPageModel.title)
        models = self.session.exec(statement).all()
        return [self._to_domain(m) for m in models]
    
    def get_count(self) -> int:
        """获取页面总数"""
        statement = select(func.count()).select_from(WikiPageModel)
        return self.session.exec(statement).one()
    
    def update(self, page: WikiPage) -> bool:
        """更新页面"""
        model = self.session.get(WikiPageModel, page.id)
        if not model:
            return False
        model.title = page.title
        model.content = page.content
        model.tags = page.tags_json
        model.parent_id = page.parent_id
        model.version = page.version
        model.updated_at = datetime.now()
        self.session.commit()
        return True
    
    def delete(self, page_id: int) -> bool:
        """删除页面"""
        model = self.session.get(WikiPageModel, page_id)
        if not model:
            return False
        self.session.delete(model)
        self.session.commit()
        return True
    
    def get_children(self, parent_id: Optional[int] = None) -> List[WikiPage]:
        """获取子页面"""
        statement = select(WikiPageModel).where(
            WikiPageModel.parent_id == parent_id
        ).order_by(WikiPageModel.title)
        models = self.session.exec(statement).all()
        return [self._to_domain(m) for m in models]
    
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
    
    def search_by_title(self, keyword: str, limit: int = 50) -> List[WikiPage]:
        """按标题搜索"""
        from sqlalchemy import func
        statement = select(WikiPageModel).where(
            func.lower(WikiPageModel.title).like(f'%{keyword.lower()}%')
        ).limit(limit)
        models = self.session.exec(statement).all()
        return [self._to_domain(m) for m in models]
    
    def get_by_tags(self, tags: List[str], limit: int = 50) -> List[WikiPage]:
        """按标签筛选"""
        if not tags:
            return []
        conditions = []
        for tag in tags:
            conditions.append(WikiPageModel.tags.like(f'%"{tag}"%'))
        if not conditions:
            return []
        statement = select(WikiPageModel).where(or_(*conditions)).limit(limit)
        models = self.session.exec(statement).all()
        return [self._to_domain(m) for m in models]