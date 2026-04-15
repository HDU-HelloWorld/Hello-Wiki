from src.core.config import settings
from src.infrastructure.ai.search_engine import KeywordSearchEngine
from src.infrastructure.db.repositories.async_wiki_repo_adapter import AsyncWikiRepositoryAdapter
from src.infrastructure.db.repositories.wiki_repo import FileSystemWikiRepository


def build_wiki_repository() -> FileSystemWikiRepository:
    return FileSystemWikiRepository(base_path=settings.STORAGE_BASE_PATH)


def build_async_wiki_repository() -> AsyncWikiRepositoryAdapter:
    return AsyncWikiRepositoryAdapter(build_wiki_repository())


def build_search_engine() -> KeywordSearchEngine:
    return KeywordSearchEngine()
