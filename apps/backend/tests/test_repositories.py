"""
WikiRepository 单元测试
验证数据访问层的正确性
"""

import pytest
from sqlmodel import Session, create_engine, SQLModel
from src.repositories.wiki import WikiRepository
from src.models.wiki import WikiPage
from src.models.version import PageVersion
from src.models.parsing import ParsingResult

# 使用内存数据库进行测试
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def session():
    """创建测试数据库会话"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
    
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def repo(session):
    """创建 WikiRepository 实例"""
    return WikiRepository(session)


class TestWikiRepository:
    """WikiRepository 测试类"""
    
    def test_create_page(self, repo):
        """测试创建页面"""
        page_id = repo.create(
            title="测试页面",
            content="# Hello World",
            tags='["test"]',
            parent_id=None
        )
        
        assert page_id is not None
        assert page_id > 0
    
    def test_get_by_id(self, repo):
        """测试根据 ID 获取页面"""
        page_id = repo.create(title="获取测试")
        page = repo.get_by_id(page_id)
        
        assert page is not None
        assert page.title == "获取测试"
        assert page.version == 1
    
    def test_get_all(self, repo):
        """测试获取所有页面"""
        # 创建 3 个测试页面
        for i in range(3):
            repo.create(title=f"页面{i}")
        
        pages = repo.get_all()
        assert len(pages) >= 3
    
    def test_update_content(self, repo):
        """测试更新内容"""
        page_id = repo.create(title="更新测试", content="原始内容")
        
        result = repo.update_content(page_id, "更新后的内容")
        assert result is True
        
        page = repo.get_by_id(page_id)
        assert page.content == "更新后的内容"
        assert page.version == 2
    
    def test_update_title(self, repo):
        """测试更新标题"""
        page_id = repo.create(title="旧标题")
        
        result = repo.update_title(page_id, "新标题")
        assert result is True
        
        page = repo.get_by_id(page_id)
        assert page.title == "新标题"
    
    def test_delete_page(self, repo):
        """测试删除页面"""
        page_id = repo.create(title="待删除")
        
        result = repo.delete(page_id)
        assert result is True
        
        page = repo.get_by_id(page_id)
        assert page is None
    
    def test_get_children(self, repo):
        """测试获取子页面"""
        parent_id = repo.create(title="父页面")
        
        child1_id = repo.create(title="子页面1", parent_id=parent_id)
        child2_id = repo.create(title="子页面2", parent_id=parent_id)
        
        children = repo.get_children(parent_id)
        assert len(children) == 2
        
        child_ids = [c.id for c in children]
        assert child1_id in child_ids
        assert child2_id in child_ids
    
    def test_get_tree(self, repo):
        """测试获取目录树"""
        # 创建树结构
        root_id = repo.create(title="根")
        child1_id = repo.create(title="子1", parent_id=root_id)
        child2_id = repo.create(title="子2", parent_id=root_id)
        grandchild_id = repo.create(title="孙", parent_id=child1_id)
        
        tree = repo.get_tree()
        
        # 验证树结构
        assert len(tree) == 1  # 只有一个根
        assert tree[0]["id"] == root_id
        assert len(tree[0]["children"]) == 2  # 两个子节点
        
        # 验证孙子节点
        child1_node = None
        for child in tree[0]["children"]:
            if child["id"] == child1_id:
                child1_node = child
                break
        
        assert child1_node is not None
        assert len(child1_node["children"]) == 1
        assert child1_node["children"][0]["id"] == grandchild_id
    
    def test_get_path(self, repo):
        """测试获取路径"""
        # 创建树结构
        root_id = repo.create(title="根")
        child_id = repo.create(title="子", parent_id=root_id)
        grandchild_id = repo.create(title="孙", parent_id=child_id)
        
        path = repo.get_path(grandchild_id)
        assert len(path) == 3
        assert path[0].id == root_id
        assert path[1].id == child_id
        assert path[2].id == grandchild_id
    
    def test_search_by_title(self, repo):
        """测试按标题搜索"""
        repo.create(title="Python教程")
        repo.create(title="JavaScript入门")
        repo.create(title="Python高级")
        
        results = repo.search_by_title("Python")
        assert len(results) == 2
    
    def test_get_by_tags(self, repo):
        """测试按标签筛选"""
        repo.create(title="Python", tags='["python", "backend"]')
        repo.create(title="JavaScript", tags='["js", "frontend"]')
        repo.create(title="FastAPI", tags='["python", "fastapi"]')
        
        results = repo.get_by_tags(["python"])
        assert len(results) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])