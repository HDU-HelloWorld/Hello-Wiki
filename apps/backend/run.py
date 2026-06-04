from pathlib import Path

import uvicorn

from src.core.config import settings
from src.core.logging import configure_logging, get_logger
from src.main import create_app

logger = get_logger(__name__)

app = create_app()
BACKEND_ROOT = Path(__file__).resolve().parent


def main() -> None:
    """本地开发环境启动入口"""
    configure_logging()
    logger.info(
        "Starting %s in %s mode...",
        settings.PROJECT_NAME,
        "DEBUG" if settings.DEBUG else "PROD",
    )
    uvicorn.run(
        "run:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=[str(BACKEND_ROOT / "src")] if settings.DEBUG else None,
        reload_excludes=["data/logs/*", "*.log"] if settings.DEBUG else None,
        workers=1 if settings.DEBUG else settings.WORKERS_COUNT,
        log_config=None,
    )


if __name__ == "__main__":
    main()